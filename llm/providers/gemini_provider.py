"""
Google Gemini Provider Implementation.

Supports Gemini 2.0 Flash, Gemini 1.5 Pro, Gemini 1.5 Flash, and other Google models.
"""

import time
import logging
from typing import Optional, Dict, Any

try:
    import google.generativeai as genai
    from google.api_core import exceptions as google_exceptions
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Google Generative AI package not installed. Install with: pip install google-generativeai")

from .base import BaseLLMProvider, LLMResponse, LLMProvider


logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini API provider.

    Supports Gemini 2.0 Flash, Gemini 1.5 Pro, Gemini 1.5 Flash, etc.
    """

    # Pricing per 1M tokens (January 2025)
    # Source: https://ai.google.dev/pricing
    PRICING = {
        "gemini-2.0-flash-exp": {"input": 0.00, "output": 0.00},  # Free during preview
        "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
        "gemini-1.5-pro-002": {"input": 1.25, "output": 5.00},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
        "gemini-1.5-flash-002": {"input": 0.075, "output": 0.30},
        "gemini-1.5-flash-8b": {"input": 0.0375, "output": 0.15},
        "gemini-1.0-pro": {"input": 0.50, "output": 1.50},
    }

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash-exp",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ):
        """
        Initialize Gemini provider.

        Args:
            api_key: Google API key
            model: Model name (default: gemini-2.0-flash-exp)
            temperature: Default temperature
            max_tokens: Default max tokens (called max_output_tokens in Gemini)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            retry_delay: Base retry delay
        """
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "Google Generative AI package not installed. Install with: pip install google-generativeai"
            )

        super().__init__(api_key, model, temperature, max_tokens, timeout, max_retries, retry_delay)

        # Configure Gemini
        genai.configure(api_key=api_key)

        # Create model
        self.client = genai.GenerativeModel(model_name=model)

        logger.info(f"Gemini provider initialized: model={model}")

    def get_provider_name(self) -> LLMProvider:
        """Return provider enum."""
        return LLMProvider.GOOGLE

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion from Gemini.

        Args:
            prompt: The prompt to send
            system_prompt: System prompt (Gemini supports system instructions)
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional Gemini parameters

        Returns:
            LLMResponse with generated content
        """
        start_time = time.time()
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        # Prepend system prompt if provided
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        # Build generation config
        generation_config = genai.GenerationConfig(
            temperature=temp,
            max_output_tokens=max_tok,
            **kwargs
        )

        # Retry logic
        last_error = None
        for attempt in range(self.max_retries):
            try:
                self.total_requests += 1

                response = self.client.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )

                # Calculate metrics
                latency_ms = (time.time() - start_time) * 1000

                # Extract usage (Gemini provides usage metadata)
                usage_metadata = response.usage_metadata
                usage = {
                    'prompt_tokens': usage_metadata.prompt_token_count,
                    'completion_tokens': usage_metadata.candidates_token_count,
                    'total_tokens': usage_metadata.total_token_count
                }
                cost = self._calculate_cost(self.model, usage)

                # Update stats
                self.total_tokens += usage['total_tokens']
                self.total_cost += cost

                # Extract content
                content = response.text if hasattr(response, 'text') else ""

                # Determine finish reason
                finish_reason = "stop"
                if response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'finish_reason'):
                        finish_reason = str(candidate.finish_reason.name).lower()

                return LLMResponse(
                    content=content,
                    model=self.model,
                    provider=LLMProvider.GOOGLE,
                    usage=usage,
                    finish_reason=finish_reason,
                    latency_ms=latency_ms,
                    cost_usd=cost,
                    cached=False,
                    metadata={
                        'attempt': attempt + 1,
                        'prompt_feedback': str(response.prompt_feedback) if hasattr(response, 'prompt_feedback') else None
                    }
                )

            except google_exceptions.ResourceExhausted as e:
                last_error = e
                logger.warning(f"Gemini rate limit (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                continue

            except (google_exceptions.DeadlineExceeded, google_exceptions.ServiceUnavailable) as e:
                last_error = e
                logger.warning(f"Gemini connection error (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                continue

            except google_exceptions.GoogleAPIError as e:
                last_error = e
                logger.error(f"Gemini API error: {e}")
                self.failed_requests += 1
                raise

            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error: {e}")
                self.failed_requests += 1
                raise

        # Max retries exceeded
        self.failed_requests += 1
        raise Exception(f"Max retries exceeded. Last error: {last_error}")

    def _calculate_cost(self, model: str, usage: Dict[str, int]) -> float:
        """
        Calculate cost in USD.

        Args:
            model: Model name
            usage: Token usage dict

        Returns:
            Cost in USD
        """
        if model not in self.PRICING:
            logger.warning(f"Unknown model pricing: {model}, using Gemini 2.0 Flash rates")
            model = "gemini-2.0-flash-exp"

        pricing = self.PRICING[model]
        prompt_cost = (usage['prompt_tokens'] / 1_000_000) * pricing['input']
        completion_cost = (usage['completion_tokens'] / 1_000_000) * pricing['output']
        return prompt_cost + completion_cost
