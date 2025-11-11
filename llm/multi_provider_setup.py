"""
Multi-Provider Setup Helper.

This module provides helper functions to load LLM providers from environment variables
and create multi-provider setups for consensus-based judging.

Usage:
    from llm.multi_provider_setup import load_providers_from_env

    # Load all available providers from .env
    providers = load_providers_from_env()

    # Use with ecosystem
    ecosystem = create_ecosystem(
        scenario=scenario,
        llm_mode='multi',
        llm_clients=providers
    )
"""

import os
import logging
from typing import List, Optional
from dotenv import load_dotenv

from .providers import (
    create_provider,
    create_multi_provider_setup,
    BaseLLMProvider,
    LLMProvider
)


logger = logging.getLogger(__name__)


def load_providers_from_env(
    require_all: bool = False,
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> List[BaseLLMProvider]:
    """
    Load all available LLM providers from environment variables.

    Reads API keys from .env file and creates provider instances for:
    - OpenAI (if OPENAI_API_KEY is set)
    - Anthropic (if ANTHROPIC_API_KEY is set)
    - Google (if GOOGLE_API_KEY is set)

    Args:
        require_all: If True, raises error if not all providers are available
        temperature: Default temperature for all providers
        max_tokens: Default max tokens for all providers

    Returns:
        List of available provider instances

    Raises:
        ValueError: If require_all=True and some API keys are missing

    Example:
        >>> providers = load_providers_from_env()
        >>> print(f"Loaded {len(providers)} providers")
        Loaded 3 providers
    """
    # Load environment variables
    load_dotenv()

    # Get API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')

    # Get model overrides
    openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    anthropic_model = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
    google_model = os.getenv('GOOGLE_MODEL', 'gemini-2.0-flash-exp')

    # Check if all required
    if require_all:
        missing = []
        if not openai_key:
            missing.append('OPENAI_API_KEY')
        if not anthropic_key:
            missing.append('ANTHROPIC_API_KEY')
        if not google_key:
            missing.append('GOOGLE_API_KEY')

        if missing:
            raise ValueError(
                f"Missing required API keys: {', '.join(missing)}. "
                "Set them in .env file or environment variables."
            )

    # Create providers
    providers = create_multi_provider_setup(
        openai_key=openai_key,
        claude_key=anthropic_key,
        gemini_key=google_key,
        openai_model=openai_model,
        claude_model=anthropic_model,
        gemini_model=google_model,
        temperature=temperature,
        max_tokens=max_tokens
    )

    logger.info(f"Loaded {len(providers)} LLM providers from environment")
    for provider in providers:
        logger.info(f"  - {provider.get_provider_name().value}: {provider.model}")

    return providers


def load_single_provider_from_env(
    provider_name: str = 'openai',
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> BaseLLMProvider:
    """
    Load a single LLM provider from environment variables.

    Args:
        provider_name: Provider to load ('openai', 'anthropic', 'google')
        temperature: Default temperature
        max_tokens: Default max tokens

    Returns:
        Provider instance

    Raises:
        ValueError: If API key is not set

    Example:
        >>> provider = load_single_provider_from_env('openai')
        >>> response = provider.generate("What is 2+2?")
    """
    load_dotenv()

    provider_name = provider_name.lower()

    if provider_name == 'openai':
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        return create_provider(
            LLMProvider.OPENAI,
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    elif provider_name == 'anthropic' or provider_name == 'claude':
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")
        model = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
        return create_provider(
            LLMProvider.ANTHROPIC,
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    elif provider_name == 'google' or provider_name == 'gemini':
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set in environment")
        model = os.getenv('GOOGLE_MODEL', 'gemini-2.0-flash-exp')
        return create_provider(
            LLMProvider.GOOGLE,
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    else:
        raise ValueError(f"Unknown provider: {provider_name}. Use 'openai', 'anthropic', or 'google'")


def get_provider_stats(providers: List[BaseLLMProvider]) -> dict:
    """
    Get combined stats from all providers.

    Args:
        providers: List of provider instances

    Returns:
        Dictionary with combined statistics

    Example:
        >>> stats = get_provider_stats(providers)
        >>> print(f"Total cost: ${stats['total_cost_usd']:.2f}")
    """
    total_requests = sum(p.total_requests for p in providers)
    total_tokens = sum(p.total_tokens for p in providers)
    total_cost = sum(p.total_cost for p in providers)
    total_failed = sum(p.failed_requests for p in providers)

    provider_stats = [p.get_stats() for p in providers]

    return {
        'num_providers': len(providers),
        'total_requests': total_requests,
        'total_tokens': total_tokens,
        'total_cost_usd': round(total_cost, 4),
        'total_failed': total_failed,
        'success_rate': round(
            (total_requests - total_failed) / max(total_requests, 1),
            3
        ),
        'providers': provider_stats
    }


__all__ = [
    'load_providers_from_env',
    'load_single_provider_from_env',
    'get_provider_stats',
]
