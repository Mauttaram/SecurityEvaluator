"""
Base Provider Interface for Multi-LLM Support.

This module defines the abstract base class that all LLM providers must implement.
Supports OpenAI, Anthropic (Claude), and Google (Gemini).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class LLMRequest(BaseModel):
    """Unified request format for all providers."""
    prompt: str = Field(..., description="The prompt to send to the LLM")
    system_prompt: Optional[str] = Field(None, description="System prompt (if supported)")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature for sampling")
    max_tokens: int = Field(2000, gt=0, description="Maximum tokens to generate")
    stop_sequences: Optional[List[str]] = Field(None, description="Stop sequences")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class LLMResponse(BaseModel):
    """Unified response format for all providers."""
    content: str = Field(..., description="The generated content")
    model: str = Field(..., description="Model used")
    provider: LLMProvider = Field(..., description="Provider used")
    usage: Dict[str, int] = Field(..., description="Token usage: {prompt_tokens, completion_tokens, total_tokens}")
    finish_reason: str = Field(..., description="Why generation stopped")
    latency_ms: float = Field(..., description="Response latency in milliseconds")
    cost_usd: float = Field(0.0, description="Estimated cost in USD")
    cached: bool = Field(False, description="Whether response was cached")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All providers (OpenAI, Anthropic, Google) must implement this interface.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ):
        """
        Initialize provider.

        Args:
            api_key: API key for the provider
            model: Model name to use
            temperature: Default temperature (0.0-2.0)
            max_tokens: Default max tokens to generate
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for transient errors
            retry_delay: Base delay between retries (exponential backoff)
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Stats
        self.total_requests = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.failed_requests = 0

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion from the LLM.

        Args:
            prompt: The prompt to send
            system_prompt: System prompt (if supported)
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse with generated content and metadata
        """
        pass

    @abstractmethod
    def _calculate_cost(self, model: str, usage: Dict[str, int]) -> float:
        """
        Calculate cost in USD for this request.

        Args:
            model: Model name
            usage: Token usage dict with prompt_tokens and completion_tokens

        Returns:
            Estimated cost in USD
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> LLMProvider:
        """Return provider enum."""
        pass

    def get_stats(self) -> Dict[str, Any]:
        """Return usage statistics."""
        return {
            'provider': self.get_provider_name().value,
            'model': self.model,
            'total_requests': self.total_requests,
            'total_tokens': self.total_tokens,
            'total_cost_usd': round(self.total_cost, 4),
            'failed_requests': self.failed_requests,
            'success_rate': round(
                (self.total_requests - self.failed_requests) / max(self.total_requests, 1),
                3
            )
        }

    def reset_stats(self):
        """Reset usage statistics."""
        self.total_requests = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.failed_requests = 0
