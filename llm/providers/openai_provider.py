"""
OpenAI Provider Implementation.

Supports GPT-4o, GPT-4o-mini, GPT-4-turbo, o1, and other OpenAI models.
"""

import time
import logging
from typing import Optional, Dict, Any

from openai import OpenAI, APIError, RateLimitError, APIConnectionError, APITimeoutError

from .base import BaseLLMProvider, LLMResponse, LLMProvider


logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI API provider.

    Supports all OpenAI models including GPT-4o, GPT-4o-mini, o1, etc.
    """

    # Pricing per 1M tokens (January 2025)
    # Source: https://openai.com/api/pricing/
    PRICING = {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-4-turbo-preview": {"input": 10.00, "output": 30.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        "o1": {"input": 15.00, "output": 60.00},
        "o1-mini": {"input": 3.00, "output": 12.00},
        "o1-preview": {"input": 15.00, "output": 60.00},
    }

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-4o-mini)
            temperature: Default temperature
            max_tokens: Default max tokens
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            retry_delay: Base retry delay
        """
        super().__init__(api_key, model, temperature, max_tokens, timeout, max_retries, retry_delay)
        self.client = OpenAI(api_key=api_key, timeout=timeout)
        logger.info(f"OpenAI provider initialized: model={model}")

    def get_provider_name(self) -> LLMProvider:
        """Return provider enum."""
        return LLMProvider.OPENAI

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion from OpenAI.

        Args:
            prompt: The prompt to send
            system_prompt: System prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional OpenAI parameters

        Returns:
            LLMResponse with generated content
        """
        start_time = time.time()
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Retry logic
        last_error = None
        for attempt in range(self.max_retries):
            try:
                self.total_requests += 1

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temp,
                    max_tokens=max_tok,
                    **kwargs
                )

                # Calculate metrics
                latency_ms = (time.time() - start_time) * 1000
                usage = {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
                cost = self._calculate_cost(self.model, usage)

                # Update stats
                self.total_tokens += usage['total_tokens']
                self.total_cost += cost

                return LLMResponse(
                    content=response.choices[0].message.content,
                    model=response.model,
                    provider=LLMProvider.OPENAI,
                    usage=usage,
                    finish_reason=response.choices[0].finish_reason,
                    latency_ms=latency_ms,
                    cost_usd=cost,
                    cached=False,
                    metadata={
                        'attempt': attempt + 1,
                        'response_id': response.id
                    }
                )

            except RateLimitError as e:
                last_error = e
                logger.warning(f"OpenAI rate limit (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                continue

            except (APIConnectionError, APITimeoutError) as e:
                last_error = e
                logger.warning(f"OpenAI connection error (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                continue

            except APIError as e:
                last_error = e
                logger.error(f"OpenAI API error: {e}")
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
            logger.warning(f"Unknown model pricing: {model}, using gpt-4o-mini rates")
            model = "gpt-4o-mini"

        pricing = self.PRICING[model]
        prompt_cost = (usage['prompt_tokens'] / 1_000_000) * pricing['input']
        completion_cost = (usage['completion_tokens'] / 1_000_000) * pricing['output']
        return prompt_cost + completion_cost
