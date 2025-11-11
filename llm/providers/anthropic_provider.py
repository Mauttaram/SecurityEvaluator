"""
Anthropic (Claude) Provider Implementation.

Supports Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku, and other Anthropic models.
"""

import time
import logging
from typing import Optional, Dict, Any

try:
    from anthropic import Anthropic, APIError, RateLimitError, APIConnectionError, APITimeoutError
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Anthropic package not installed. Install with: pip install anthropic")

from .base import BaseLLMProvider, LLMResponse, LLMProvider


logger = logging.getLogger(__name__)


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic (Claude) API provider.

    Supports Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku, etc.
    """

    # Pricing per 1M tokens (January 2025)
    # Source: https://www.anthropic.com/pricing
    PRICING = {
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "claude-3-5-sonnet-20240620": {"input": 3.00, "output": 15.00},
        "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
        "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
        "claude-2.1": {"input": 8.00, "output": 24.00},
        "claude-2.0": {"input": 8.00, "output": 24.00},
    }

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key
            model: Model name (default: claude-3-5-sonnet-20241022)
            temperature: Default temperature
            max_tokens: Default max tokens
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            retry_delay: Base retry delay
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic package not installed. Install with: pip install anthropic"
            )

        super().__init__(api_key, model, temperature, max_tokens, timeout, max_retries, retry_delay)
        self.client = Anthropic(api_key=api_key, timeout=timeout)
        logger.info(f"Anthropic provider initialized: model={model}")

    def get_provider_name(self) -> LLMProvider:
        """Return provider enum."""
        return LLMProvider.ANTHROPIC

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion from Claude.

        Args:
            prompt: The prompt to send
            system_prompt: System prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional Anthropic parameters

        Returns:
            LLMResponse with generated content
        """
        start_time = time.time()
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        # Build messages (Anthropic uses messages API)
        messages = [{"role": "user", "content": prompt}]

        # Build request parameters
        request_params = {
            "model": self.model,
            "messages": messages,
            "temperature": temp,
            "max_tokens": max_tok,
        }

        # Add system prompt if provided
        if system_prompt:
            request_params["system"] = system_prompt

        # Add additional kwargs
        request_params.update(kwargs)

        # Retry logic
        last_error = None
        for attempt in range(self.max_retries):
            try:
                self.total_requests += 1

                response = self.client.messages.create(**request_params)

                # Calculate metrics
                latency_ms = (time.time() - start_time) * 1000
                usage = {
                    'prompt_tokens': response.usage.input_tokens,
                    'completion_tokens': response.usage.output_tokens,
                    'total_tokens': response.usage.input_tokens + response.usage.output_tokens
                }
                cost = self._calculate_cost(self.model, usage)

                # Update stats
                self.total_tokens += usage['total_tokens']
                self.total_cost += cost

                # Extract content
                content = response.content[0].text if response.content else ""

                return LLMResponse(
                    content=content,
                    model=response.model,
                    provider=LLMProvider.ANTHROPIC,
                    usage=usage,
                    finish_reason=response.stop_reason or "end_turn",
                    latency_ms=latency_ms,
                    cost_usd=cost,
                    cached=False,
                    metadata={
                        'attempt': attempt + 1,
                        'response_id': response.id,
                        'stop_sequence': response.stop_sequence
                    }
                )

            except RateLimitError as e:
                last_error = e
                logger.warning(f"Anthropic rate limit (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                continue

            except (APIConnectionError, APITimeoutError) as e:
                last_error = e
                logger.warning(f"Anthropic connection error (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                continue

            except APIError as e:
                last_error = e
                logger.error(f"Anthropic API error: {e}")
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
            logger.warning(f"Unknown model pricing: {model}, using Claude 3.5 Sonnet rates")
            model = "claude-3-5-sonnet-20241022"

        pricing = self.PRICING[model]
        prompt_cost = (usage['prompt_tokens'] / 1_000_000) * pricing['input']
        completion_cost = (usage['completion_tokens'] / 1_000_000) * pricing['output']
        return prompt_cost + completion_cost
