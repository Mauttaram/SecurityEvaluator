"""
SQL Injection Detection Benchmark - LLM as Judge Implementation.

This is an alternative Green Agent that uses an LLM to evaluate Purple Agent responses
qualitatively rather than just comparing binary vulnerability classifications. The LLM
judge can assess explanation quality, reasoning correctness, and provide nuanced scoring.
"""

import asyncio
import time
import random
import argparse
import logging
from pathlib import Path
from typing import Any
from enum import Enum

import httpx
from pydantic import BaseModel, Field
from agentbeats.green_executor import GreenAgent
from agentbeats.models import EvalRequest as AgentBeatsEvalRequest
from a2a.server.tasks import TaskUpdater

# Handle both relative and absolute imports
try:
    from .models import (
        EvalRequest,
        EvalResponse,
        CodeSample,
        PurpleAgentResponse,
        TestResult,
        DetectionOutcome,
        EvaluationConfig,
        EvaluationMode,
        EvaluationMetrics,
        CategoryMetrics
    )
    from .dataset_manager import DatasetManager
    from .scoring_engine import ScoringEngine
    from .agent_card import sql_injection_agent_card
except ImportError:
    from models import (
        EvalRequest,
        EvalResponse,
        CodeSample,
        PurpleAgentResponse,
        TestResult,
        DetectionOutcome,
        EvaluationConfig,
        EvaluationMode,
        EvaluationMetrics,
        CategoryMetrics
    )
    from dataset_manager import DatasetManager
    from scoring_engine import ScoringEngine
    from agent_card import sql_injection_agent_card


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# LLM Judge Specific Models
# ============================================================================

class LLMProvider(str, Enum):
    """Supported LLM providers for judging."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"


class JudgmentCriteria(BaseModel):
    """Criteria for LLM to judge purple agent responses."""

    vulnerability_detection_accuracy: float = Field(
        ..., ge=0.0, le=1.0,
        description="How accurate is the vulnerability detection (0-1)"
    )
    explanation_quality: float = Field(
        ..., ge=0.0, le=1.0,
        description="Quality and clarity of explanation (0-1)"
    )
    technical_correctness: float = Field(
        ..., ge=0.0, le=1.0,
        description="Technical accuracy of analysis (0-1)"
    )
    actionability: float = Field(
        ..., ge=0.0, le=1.0,
        description="How actionable are the recommendations (0-1)"
    )
    completeness: float = Field(
        ..., ge=0.0, le=1.0,
        description="Did the agent identify all issues (0-1)"
    )

    @property
    def overall_score(self) -> float:
        """Calculate weighted overall score."""
        return (
            self.vulnerability_detection_accuracy * 0.40 +
            self.explanation_quality * 0.20 +
            self.technical_correctness * 0.25 +
            self.actionability * 0.10 +
            self.completeness * 0.05
        )


class LLMJudgment(BaseModel):
    """LLM's judgment of a purple agent response."""

    test_case_id: str = Field(..., description="ID of the test case")
    criteria: JudgmentCriteria = Field(..., description="Detailed scoring criteria")
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall score (0-1)")
    reasoning: str = Field(..., description="LLM's reasoning for the judgment")
    identified_issues: list[str] = Field(default_factory=list, description="Issues found by LLM")
    strengths: list[str] = Field(default_factory=list, description="Strengths identified by LLM")
    verdict: DetectionOutcome = Field(..., description="Final verdict on detection")
    confidence: float = Field(..., ge=0.0, le=1.0, description="LLM's confidence in judgment")


class LLMJudgeConfig(BaseModel):
    """Configuration for LLM judge."""

    provider: LLMProvider = Field(LLMProvider.ANTHROPIC, description="LLM provider")
    model: str = Field("claude-3-5-sonnet-20241022", description="Model name")
    api_key: str | None = Field(None, description="API key (or use env var)")
    temperature: float = Field(0.1, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(2000, ge=100, description="Max tokens for response")
    judge_timeout: float = Field(30.0, ge=1.0, description="Timeout for LLM judge call")


class LLMTestResult(TestResult):
    """Extended test result with LLM judgment."""

    llm_judgment: LLMJudgment | None = Field(None, description="LLM's detailed judgment")
    llm_score: float = Field(0.0, ge=0.0, le=1.0, description="LLM quality score")


class LLMEvaluationMetrics(EvaluationMetrics):
    """Extended metrics including LLM quality scores."""

    average_llm_score: float = Field(0.0, ge=0.0, le=1.0, description="Average LLM quality score")
    average_explanation_quality: float = Field(0.0, ge=0.0, le=1.0, description="Avg explanation quality")
    average_technical_correctness: float = Field(0.0, ge=0.0, le=1.0, description="Avg technical correctness")
    average_actionability: float = Field(0.0, ge=0.0, le=1.0, description="Avg actionability")


# ============================================================================
# LLM Judge Implementation
# ============================================================================

class LLMJudge:
    """LLM-based judge for evaluating purple agent responses."""

    def __init__(self, config: LLMJudgeConfig):
        """
        Initialize the LLM judge.

        Args:
            config: LLM judge configuration
        """
        self.config = config
        self.client: httpx.AsyncClient | None = None

        # Set up API key from config or environment
        if config.api_key:
            self.api_key = config.api_key
        else:
            import os
            if config.provider == LLMProvider.ANTHROPIC:
                self.api_key = os.getenv("ANTHROPIC_API_KEY")
            elif config.provider == LLMProvider.OPENAI:
                self.api_key = os.getenv("OPENAI_API_KEY")
            elif config.provider == LLMProvider.GOOGLE:
                self.api_key = os.getenv("GOOGLE_API_KEY")

        if not self.api_key:
            raise ValueError(f"API key not found for provider {config.provider}")

    async def initialize(self):
        """Initialize HTTP client."""
        self.client = httpx.AsyncClient(timeout=self.config.judge_timeout)

    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.close()

    async def judge_response(
        self,
        code_sample: CodeSample,
        purple_response: PurpleAgentResponse
    ) -> LLMJudgment:
        """
        Use LLM to judge a purple agent's response.

        Args:
            code_sample: The code sample that was analyzed
            purple_response: Purple agent's response

        Returns:
            LLMJudgment with detailed scoring
        """
        # Build prompt for LLM judge
        prompt = self._build_judge_prompt(code_sample, purple_response)

        # Call LLM based on provider
        if self.config.provider == LLMProvider.ANTHROPIC:
            llm_response = await self._call_anthropic(prompt)
        elif self.config.provider == LLMProvider.OPENAI:
            llm_response = await self._call_openai(prompt)
        elif self.config.provider == LLMProvider.GOOGLE:
            llm_response = await self._call_google(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

        # Parse LLM response into judgment
        judgment = self._parse_judgment(llm_response, code_sample, purple_response)

        return judgment

    def _build_judge_prompt(
        self,
        code_sample: CodeSample,
        purple_response: PurpleAgentResponse
    ) -> str:
        """
        Build the prompt for the LLM judge.

        Args:
            code_sample: Code sample being evaluated
            purple_response: Purple agent's response

        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert security analyst evaluating an AI security tool's analysis of code for SQL injection vulnerabilities.

CODE SAMPLE:
```{code_sample.language}
{code_sample.code}
```

GROUND TRUTH:
- Is Vulnerable: {code_sample.is_vulnerable}
- Category: {code_sample.category}
- Severity: {code_sample.severity or 'N/A'}
- Description: {code_sample.description or 'N/A'}

AI TOOL'S ANALYSIS:
- Detection: {"Vulnerable" if purple_response.is_vulnerable else "Secure"}
- Confidence: {purple_response.confidence:.2f}
- Vulnerability Type: {purple_response.vulnerability_type or 'N/A'}
- Explanation: {purple_response.explanation or 'No explanation provided'}
- Detected Patterns: {', '.join(purple_response.detected_patterns) if purple_response.detected_patterns else 'None'}
- Line Numbers: {', '.join(map(str, purple_response.line_numbers)) if purple_response.line_numbers else 'None'}
- Severity: {purple_response.severity or 'N/A'}

EVALUATION TASK:
Evaluate the AI tool's analysis on the following criteria (score each 0.0 to 1.0):

1. vulnerability_detection_accuracy: Did it correctly identify if the code is vulnerable?
2. explanation_quality: Is the explanation clear, well-structured, and helpful?
3. technical_correctness: Are the technical details and reasoning correct?
4. actionability: Does it provide actionable insights for fixing issues?
5. completeness: Did it identify all relevant aspects of the vulnerability?

Provide your evaluation in the following JSON format:
{{
    "vulnerability_detection_accuracy": <score 0.0-1.0>,
    "explanation_quality": <score 0.0-1.0>,
    "technical_correctness": <score 0.0-1.0>,
    "actionability": <score 0.0-1.0>,
    "completeness": <score 0.0-1.0>,
    "reasoning": "<your detailed reasoning>",
    "identified_issues": ["<issue 1>", "<issue 2>", ...],
    "strengths": ["<strength 1>", "<strength 2>", ...],
    "confidence": <your confidence in this judgment 0.0-1.0>
}}

Be objective and thorough in your evaluation."""

        return prompt

    async def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic's Claude API."""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = await self.client.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()

        return result["content"][0]["text"]

    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI's GPT API."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.config.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }

        response = await self.client.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()

        return result["choices"][0]["message"]["content"]

    async def _call_google(self, prompt: str) -> str:
        """Call Google's Gemini API."""
        url = f"https://generativelanguage.googleapis.com/v1/models/{self.config.model}:generateContent"
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "key": self.api_key
        }
        data = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ],
            "generationConfig": {
                "temperature": self.config.temperature,
                "maxOutputTokens": self.config.max_tokens
            }
        }

        response = await self.client.post(url, json=data, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()

        return result["candidates"][0]["content"]["parts"][0]["text"]

    def _parse_judgment(
        self,
        llm_response: str,
        code_sample: CodeSample,
        purple_response: PurpleAgentResponse
    ) -> LLMJudgment:
        """
        Parse LLM response into structured judgment.

        Args:
            llm_response: Raw LLM response text
            code_sample: Original code sample
            purple_response: Purple agent's response

        Returns:
            Structured LLMJudgment
        """
        import json
        import re

        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', llm_response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                raise ValueError("Could not extract JSON from LLM response")

        # Parse JSON
        judgment_data = json.loads(json_str)

        # Create criteria
        criteria = JudgmentCriteria(
            vulnerability_detection_accuracy=judgment_data["vulnerability_detection_accuracy"],
            explanation_quality=judgment_data["explanation_quality"],
            technical_correctness=judgment_data["technical_correctness"],
            actionability=judgment_data["actionability"],
            completeness=judgment_data["completeness"]
        )

        # Determine verdict based on ground truth and purple agent response
        ground_truth = code_sample.is_vulnerable
        predicted = purple_response.is_vulnerable

        if ground_truth and predicted:
            verdict = DetectionOutcome.TRUE_POSITIVE
        elif not ground_truth and not predicted:
            verdict = DetectionOutcome.TRUE_NEGATIVE
        elif not ground_truth and predicted:
            verdict = DetectionOutcome.FALSE_POSITIVE
        else:
            verdict = DetectionOutcome.FALSE_NEGATIVE

        # Build judgment
        judgment = LLMJudgment(
            test_case_id=code_sample.id,
            criteria=criteria,
            overall_score=criteria.overall_score,
            reasoning=judgment_data["reasoning"],
            identified_issues=judgment_data.get("identified_issues", []),
            strengths=judgment_data.get("strengths", []),
            verdict=verdict,
            confidence=judgment_data.get("confidence", 0.8)
        )

        return judgment


# ============================================================================
# LLM-based SQL Injection Judge
# ============================================================================

class SQLInjectionLLMJudge(GreenAgent):
    """
    Green Agent that uses an LLM to judge Purple Agent responses.

    This provides more nuanced evaluation than binary classification,
    assessing explanation quality, technical correctness, and actionability.
    """

    def __init__(self, dataset_root: str | Path, llm_config: LLMJudgeConfig):
        """
        Initialize the LLM-based judge.

        Args:
            dataset_root: Root directory containing dataset JSON files
            llm_config: Configuration for LLM judge
        """
        super().__init__()
        self.dataset_manager = DatasetManager(dataset_root)
        self.scoring_engine = ScoringEngine()
        self.llm_judge = LLMJudge(llm_config)

        # Load datasets
        logger.info("Loading datasets...")
        metadata = self.dataset_manager.load_datasets()
        logger.info(f"Loaded {metadata.total_samples} samples across {len(metadata.languages)} languages")

    async def run_eval(self, req: EvalRequest, updater: TaskUpdater) -> EvalResponse:
        """
        Run LLM-based evaluation on a Purple Agent.

        Args:
            req: Evaluation request
            updater: Task updater

        Returns:
            EvalResponse with LLM-enhanced results
        """
        try:
            # Parse configuration
            config = self._parse_config(req.config)
            logger.info(f"Starting LLM-based evaluation")
            logger.info(f"Purple Agent: {req.purple_agent_id} at {req.purple_agent_endpoint}")

            # Initialize LLM judge
            await self.llm_judge.initialize()

            # Set random seed
            if config.random_seed is not None:
                random.seed(config.random_seed)

            await updater.update(status="running", message="Initializing LLM-based evaluation...")

            # Run evaluation
            start_time = time.time()
            response = await self._run_llm_evaluation(
                req.purple_agent_id,
                req.purple_agent_endpoint,
                config,
                updater
            )

            execution_time = time.time() - start_time
            response.execution_time_seconds = execution_time

            # Clean up
            await self.llm_judge.close()

            # Final update
            await updater.update(
                status="completed",
                message=f"Evaluation completed: F1={response.metrics.f1_score:.3f}, "
                       f"Avg LLM Score={response.metrics.average_llm_score:.3f}"
            )

            logger.info(f"Evaluation completed in {execution_time:.2f}s")
            logger.info(f"Results: F1={response.metrics.f1_score:.3f}, "
                       f"LLM Score={response.metrics.average_llm_score:.3f}")

            return response

        except Exception as e:
            logger.error(f"Evaluation failed: {e}", exc_info=True)
            await updater.update(status="failed", message=f"Evaluation failed: {str(e)}")
            await self.llm_judge.close()
            return EvalResponse(
                success=False,
                error_message=str(e),
                tests_executed=0,
                execution_time_seconds=0.0
            )

    async def _run_llm_evaluation(
        self,
        purple_agent_id: str,
        purple_agent_endpoint: str,
        config: EvaluationConfig,
        updater: TaskUpdater
    ) -> EvalResponse:
        """
        Run LLM-based evaluation.

        Args:
            purple_agent_id: Purple agent ID
            purple_agent_endpoint: Purple agent endpoint
            config: Evaluation configuration
            updater: Task updater

        Returns:
            EvalResponse with results
        """
        # Sample test cases
        test_samples = self.dataset_manager.sample_diverse(
            n=config.test_budget,
            seed=config.random_seed,
            categories=config.categories_to_test,
            languages=config.languages_to_test
        )

        logger.info(f"Selected {len(test_samples)} test cases")

        await updater.update(
            status="running",
            message=f"Executing {len(test_samples)} tests with LLM judge..."
        )

        # Execute tests with LLM judging
        test_results = await self._execute_tests_with_llm_judge(
            test_samples,
            purple_agent_endpoint,
            config.per_test_timeout_seconds,
            updater
        )

        # Calculate metrics (including LLM scores)
        overall_metrics = self._calculate_llm_metrics(test_results)
        category_metrics = self.scoring_engine.calculate_category_metrics(
            [TestResult(**r.model_dump(exclude={'llm_judgment', 'llm_score'})) for r in test_results]
        )

        return EvalResponse(
            success=True,
            metrics=overall_metrics,
            category_metrics=category_metrics,
            tests_executed=len(test_results),
            execution_time_seconds=0.0,
            metadata={
                "mode": "llm_judge",
                "purple_agent_id": purple_agent_id,
                "llm_provider": self.llm_judge.config.provider.value,
                "llm_model": self.llm_judge.config.model
            }
        )

    async def _execute_tests_with_llm_judge(
        self,
        test_samples: list[CodeSample],
        purple_agent_endpoint: str,
        timeout: float,
        updater: TaskUpdater
    ) -> list[LLMTestResult]:
        """
        Execute tests and have LLM judge each response.

        Args:
            test_samples: Code samples to test
            purple_agent_endpoint: Purple agent URL
            timeout: Timeout per test
            updater: Task updater

        Returns:
            List of LLM test results
        """
        results = []

        async with httpx.AsyncClient(timeout=timeout) as client:
            for idx, sample in enumerate(test_samples):
                try:
                    # Call purple agent
                    purple_response = await self._call_purple_agent(
                        client,
                        purple_agent_endpoint,
                        sample
                    )

                    # Have LLM judge the response
                    llm_judgment = await self.llm_judge.judge_response(sample, purple_response)

                    # Create test result
                    result = LLMTestResult(
                        test_case_id=sample.id,
                        ground_truth=sample.is_vulnerable,
                        predicted=purple_response.is_vulnerable,
                        outcome=llm_judgment.verdict,
                        category=sample.category,
                        language=sample.language,
                        confidence=purple_response.confidence,
                        execution_time_ms=purple_response.execution_time_ms,
                        purple_agent_response=purple_response,
                        llm_judgment=llm_judgment,
                        llm_score=llm_judgment.overall_score
                    )
                    results.append(result)

                    # Update progress
                    if (idx + 1) % 5 == 0:
                        await updater.update(
                            status="running",
                            message=f"Tested {idx + 1}/{len(test_samples)} samples "
                                   f"(Avg LLM score: {sum(r.llm_score for r in results) / len(results):.3f})..."
                        )

                except Exception as e:
                    logger.error(f"Test failed for sample {sample.id}: {e}")
                    # Create minimal result on failure
                    result = LLMTestResult(
                        test_case_id=sample.id,
                        ground_truth=sample.is_vulnerable,
                        predicted=False,
                        outcome=DetectionOutcome.FALSE_NEGATIVE if sample.is_vulnerable else DetectionOutcome.TRUE_NEGATIVE,
                        category=sample.category,
                        language=sample.language,
                        confidence=0.0,
                        llm_score=0.0
                    )
                    results.append(result)

        return results

    async def _call_purple_agent(
        self,
        client: httpx.AsyncClient,
        endpoint: str,
        sample: CodeSample
    ) -> PurpleAgentResponse:
        """Call the Purple Agent to analyze a code sample."""
        request_data = {
            "test_case_id": sample.id,
            "code": sample.code,
            "language": sample.language,
            "category": sample.category
        }

        start_time = time.time()
        response = await client.post(endpoint, json=request_data)
        response.raise_for_status()
        execution_time_ms = (time.time() - start_time) * 1000

        data = response.json()

        return PurpleAgentResponse(
            test_case_id=data.get("test_case_id", sample.id),
            is_vulnerable=data.get("is_vulnerable", False),
            confidence=data.get("confidence", 0.5),
            vulnerability_type=data.get("vulnerability_type"),
            explanation=data.get("explanation"),
            detected_patterns=data.get("detected_patterns", []),
            line_numbers=data.get("line_numbers", []),
            severity=data.get("severity"),
            execution_time_ms=execution_time_ms
        )

    def _calculate_llm_metrics(self, results: list[LLMTestResult]) -> LLMEvaluationMetrics:
        """
        Calculate metrics including LLM quality scores.

        Args:
            results: List of LLM test results

        Returns:
            LLM evaluation metrics
        """
        # Calculate base metrics
        base_results = [TestResult(**r.model_dump(exclude={'llm_judgment', 'llm_score'})) for r in results]
        base_metrics = self.scoring_engine.calculate_metrics(base_results)

        # Calculate LLM-specific metrics
        total_llm_score = sum(r.llm_score for r in results)
        avg_llm_score = total_llm_score / len(results) if results else 0.0

        # Calculate average criteria scores
        valid_judgments = [r.llm_judgment for r in results if r.llm_judgment is not None]

        if valid_judgments:
            avg_explanation_quality = sum(j.criteria.explanation_quality for j in valid_judgments) / len(valid_judgments)
            avg_technical_correctness = sum(j.criteria.technical_correctness for j in valid_judgments) / len(valid_judgments)
            avg_actionability = sum(j.criteria.actionability for j in valid_judgments) / len(valid_judgments)
        else:
            avg_explanation_quality = 0.0
            avg_technical_correctness = 0.0
            avg_actionability = 0.0

        return LLMEvaluationMetrics(
            **base_metrics.model_dump(),
            average_llm_score=avg_llm_score,
            average_explanation_quality=avg_explanation_quality,
            average_technical_correctness=avg_technical_correctness,
            average_actionability=avg_actionability
        )

    def _parse_config(self, config_dict: dict[str, Any]) -> EvaluationConfig:
        """Parse configuration from request."""
        return EvaluationConfig(
            mode=EvaluationMode.FIXED,  # LLM judge uses fixed mode
            test_budget=config_dict.get("test_budget", 50),  # Smaller default due to LLM costs
            timeout_seconds=config_dict.get("timeout_seconds", 600),
            per_test_timeout_seconds=config_dict.get("per_test_timeout_seconds", 30.0),
            random_seed=config_dict.get("random_seed"),
            categories_to_test=config_dict.get("categories"),
            languages_to_test=config_dict.get("languages")
        )


async def main():
    """Main entry point for running the LLM Judge."""
    import contextlib
    import uvicorn
    from agentbeats.green_executor import GreenExecutor
    from a2a.server.apps import A2AStarletteApplication
    from a2a.server.request_handlers import DefaultRequestHandler
    from a2a.server.tasks import InMemoryTaskStore

    parser = argparse.ArgumentParser(description="SQL Injection Detection - LLM as Judge")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=9011, help="Port to bind to")
    parser.add_argument(
        "--dataset-root",
        default="datasets/sql_injection",
        help="Root directory containing datasets"
    )
    parser.add_argument("--card-url", type=str, help="External URL for agent card")
    parser.add_argument("--cloudflare-quick-tunnel", action="store_true",
                       help="Use Cloudflare quick tunnel")
    parser.add_argument("--llm-provider", type=str, default="anthropic",
                       choices=["anthropic", "openai", "google"],
                       help="LLM provider for judging")
    parser.add_argument("--llm-model", type=str,
                       help="LLM model name (default: provider-specific)")
    parser.add_argument("--api-key", type=str, help="API key for LLM provider")

    args = parser.parse_args()

    # Set default model based on provider
    if not args.llm_model:
        if args.llm_provider == "anthropic":
            args.llm_model = "claude-3-5-sonnet-20241022"
        elif args.llm_provider == "openai":
            args.llm_model = "gpt-4-turbo-preview"
        elif args.llm_provider == "google":
            args.llm_model = "gemini-pro"

    # Create LLM judge config
    llm_config = LLMJudgeConfig(
        provider=LLMProvider(args.llm_provider),
        model=args.llm_model,
        api_key=args.api_key
    )

    # Handle Cloudflare tunnel
    if args.cloudflare_quick_tunnel:
        from agentbeats.cloudflare import quick_tunnel
        agent_url_cm = quick_tunnel(f"http://{args.host}:{args.port}")
    else:
        agent_url_cm = contextlib.nullcontext(args.card_url or f"http://{args.host}:{args.port}/")

    async with agent_url_cm as agent_url:
        # Initialize judge
        dataset_root = Path(args.dataset_root)
        judge = SQLInjectionLLMJudge(dataset_root, llm_config)

        # Create executor
        executor = GreenExecutor(judge)

        # Create agent card
        agent_card = sql_injection_agent_card(
            agent_name="sql_injection_llm_judge",
            card_url=agent_url
        )

        # Create request handler
        request_handler = DefaultRequestHandler(
            agent_executor=executor,
            task_store=InMemoryTaskStore(),
        )

        # Create A2A server
        server = A2AStarletteApplication(
            agent_card=agent_card,
            http_handler=request_handler,
        )

        # Start server
        logger.info(f"Starting SQL Injection LLM Judge on {args.host}:{args.port}")
        logger.info(f"LLM Provider: {args.llm_provider} ({args.llm_model})")
        logger.info(f"Dataset root: {dataset_root.absolute()}")

        uvicorn_config = uvicorn.Config(server.build(), host=args.host, port=args.port)
        uvicorn_server = uvicorn.Server(uvicorn_config)
        await uvicorn_server.serve()


if __name__ == "__main__":
    asyncio.run(main())
