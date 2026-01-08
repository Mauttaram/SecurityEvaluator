"""
Multi-Provider LLM Support.

This package provides a unified interface for multiple LLM providers:
- OpenAI (GPT-4o, GPT-4o-mini, o1, etc.)
- Anthropic (Claude 3.5 Sonnet, Claude 3 Opus, etc.)
- Google (Gemini 2.0 Flash, Gemini 1.5 Pro, etc.)

Usage:
    from llm.providers import create_provider, LLMProvider

    # Create OpenAI provider
    openai = create_provider(
        provider=LLMProvider.OPENAI,
        api_key="sk-...",
        model="gpt-4o-mini"
    )

    # Create multi-LLM setup for consensus
    providers = [
        create_provider(LLMProvider.OPENAI, api_key=openai_key),
        create_provider(LLMProvider.ANTHROPIC, api_key=claude_key),
        create_provider(LLMProvider.GOOGLE, api_key=gemini_key)
    ]
"""

from .base import BaseLLMProvider, LLMProvider, LLMRequest, LLMResponse
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .gemini_provider import GeminiProvider


def create_provider(
    provider: LLMProvider,
    api_key: str,
    model: str = None,
    **kwargs
) -> BaseLLMProvider:
    """
    Factory function to create LLM provider.

    Args:
        provider: Provider enum (OPENAI, ANTHROPIC, GOOGLE)
        api_key: API key for the provider
        model: Model name (uses provider default if not specified)
        **kwargs: Additional provider-specific parameters

    Returns:
        BaseLLMProvider instance

    Example:
        >>> openai = create_provider(
        ...     provider=LLMProvider.OPENAI,
        ...     api_key="sk-...",
        ...     model="gpt-4o-mini"
        ... )
        >>> response = openai.generate("What is 2+2?")
        >>> print(response.content)
    """
    if provider == LLMProvider.OPENAI:
        return OpenAIProvider(
            api_key=api_key,
            model=model or "gpt-4o-mini",
            **kwargs
        )
    elif provider == LLMProvider.ANTHROPIC:
        return AnthropicProvider(
            api_key=api_key,
            model=model or "claude-3-5-sonnet-20241022",
            **kwargs
        )
    elif provider == LLMProvider.GOOGLE:
        return GeminiProvider(
            api_key=api_key,
            model=model or "gemini-2.0-flash-exp",
            **kwargs
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def create_multi_provider_setup(
    openai_key: str = None,
    claude_key: str = None,
    gemini_key: str = None,
    openai_model: str = "gpt-4o-mini",
    claude_model: str = "claude-3-5-sonnet-20241022",
    gemini_model: str = "gemini-2.0-flash-exp",
    **kwargs
) -> list[BaseLLMProvider]:
    """
    Create multiple providers for consensus-based judging.

    Args:
        openai_key: OpenAI API key (optional)
        claude_key: Anthropic API key (optional)
        gemini_key: Google API key (optional)
        openai_model: OpenAI model name
        claude_model: Claude model name
        gemini_model: Gemini model name
        **kwargs: Additional parameters passed to all providers

    Returns:
        List of provider instances (only for provided API keys)

    Example:
        >>> providers = create_multi_provider_setup(
        ...     openai_key="sk-...",
        ...     claude_key="sk-ant-...",
        ...     gemini_key="AIza..."
        ... )
        >>> # Use with LLMJudgeAgent for consensus
        >>> judge = LLMJudgeAgent(
        ...     agent_id="multi_judge",
        ...     llm_clients=providers,
        ...     knowledge_base=kb
        ... )
    """
    providers = []

    if openai_key:
        providers.append(create_provider(
            LLMProvider.OPENAI,
            api_key=openai_key,
            model=openai_model,
            **kwargs
        ))

    if claude_key:
        providers.append(create_provider(
            LLMProvider.ANTHROPIC,
            api_key=claude_key,
            model=claude_model,
            **kwargs
        ))

    if gemini_key:
        providers.append(create_provider(
            LLMProvider.GOOGLE,
            api_key=gemini_key,
            model=gemini_model,
            **kwargs
        ))

    if not providers:
        raise ValueError("At least one API key must be provided")

    return providers


__all__ = [
    'BaseLLMProvider',
    'LLMProvider',
    'LLMRequest',
    'LLMResponse',
    'OpenAIProvider',
    'AnthropicProvider',
    'GeminiProvider',
    'create_provider',
    'create_multi_provider_setup',
]
