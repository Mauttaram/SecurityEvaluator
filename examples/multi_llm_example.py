#!/usr/bin/env python3
"""
Multi-LLM Consensus Example.

This example shows how to use multiple LLM providers (OpenAI, Claude, Gemini)
for consensus-based judging in security evaluations.

PHASE 1 (Development): Single LLM
PHASE 2 (Production): Multi-LLM Consensus

Usage:
    # Phase 1 - Single LLM (cheap, fast)
    python examples/multi_llm_example.py --phase 1

    # Phase 2 - Multi-LLM Consensus (expensive, reliable)
    python examples/multi_llm_example.py --phase 2
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from framework.scenarios import SQLInjectionScenario
from framework import create_ecosystem
from llm.multi_provider_setup import (
    load_providers_from_env,
    load_single_provider_from_env,
    get_provider_stats
)


class SimpleSQLDetector:
    """Simple SQL injection detector for testing."""

    def get_name(self) -> str:
        return "SimpleSQLDetector"

    def reset(self):
        pass

    def detect(self, attack):
        from framework.models import TestResult, TestOutcome, Severity

        if hasattr(attack, 'payload'):
            code = str(attack.payload).upper()
        else:
            code = str(attack).upper()

        keywords = ['UNION', 'SELECT', 'DROP', 'OR 1=1', '--']
        detected = any(kw in code for kw in keywords)

        return TestResult(
            result_id=f"test_{hash(code)}",
            attack_id=getattr(attack, 'attack_id', 'unknown'),
            detected=detected,
            confidence=0.8 if detected else 0.2,
            outcome=TestOutcome.TRUE_POSITIVE if detected else TestOutcome.FALSE_NEGATIVE,
            severity=Severity.HIGH if detected else Severity.LOW
        )


def phase1_single_llm():
    """
    Phase 1: Single LLM for cost-effective development.

    Uses:
    - Single OpenAI LLM (gpt-4o-mini)
    - Cost: $2-5 per evaluation
    - Reliability: ~80-85%
    """
    print("=" * 80)
    print("PHASE 1: Single LLM (Development Mode)")
    print("=" * 80)
    print()

    # Load single provider
    print("Loading single LLM provider (OpenAI)...")
    try:
        provider = load_single_provider_from_env('openai')
        print(f"✅ Loaded: {provider.get_provider_name().value} - {provider.model}")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nPlease set OPENAI_API_KEY in .env file")
        return

    print()

    # Create scenario and purple agent
    scenario = SQLInjectionScenario()
    purple_agent = SimpleSQLDetector()

    print("Creating evaluation ecosystem...")
    ecosystem = create_ecosystem(
        scenario=scenario,
        llm_mode='cheap',  # Single LLM mode
        llm_clients=[provider],
        config={
            'use_sandbox': False,
            'num_boundary_probers': 1,
            'num_exploiters': 2,
            'num_mutators': 1,
        }
    )
    print("✅ Ecosystem created (single LLM mode)")
    print()

    # Run evaluation
    print("Running evaluation (2 rounds for demo)...")
    result = ecosystem.evaluate(purple_agent, max_rounds=2)

    # Display results
    print()
    print("=" * 80)
    print("RESULTS - PHASE 1 (Single LLM)")
    print("=" * 80)
    print()
    print(f"F1 Score:      {result.metrics.f1_score:.3f}")
    print(f"Precision:     {result.metrics.precision:.3f}")
    print(f"Recall:        {result.metrics.recall:.3f}")
    print(f"Total Tests:   {result.metrics.total_tests}")
    print(f"Duration:      {result.duration_seconds:.1f}s")
    print()

    # Provider stats
    stats = get_provider_stats([provider])
    print("LLM Usage:")
    print(f"  Provider:    {provider.get_provider_name().value}")
    print(f"  Requests:    {stats['total_requests']}")
    print(f"  Tokens:      {stats['total_tokens']:,}")
    print(f"  Cost:        ${stats['total_cost_usd']:.4f}")
    print()
    print("💡 Phase 1 is perfect for development and testing!")
    print()


def phase2_multi_llm():
    """
    Phase 2: Multi-LLM Consensus for production reliability.

    Uses:
    - OpenAI (gpt-4o-mini)
    - Anthropic (claude-3-5-sonnet)
    - Google (gemini-2.0-flash-exp)
    - Dawid-Skene consensus algorithm
    - Cost: $6-15 per evaluation (3x Phase 1)
    - Reliability: ~90-95%
    """
    print("=" * 80)
    print("PHASE 2: Multi-LLM Consensus (Production Mode)")
    print("=" * 80)
    print()

    # Load all providers
    print("Loading multi-provider setup (OpenAI + Claude + Gemini)...")
    try:
        providers = load_providers_from_env(require_all=False)
        print(f"✅ Loaded {len(providers)} providers:")
        for p in providers:
            print(f"   - {p.get_provider_name().value}: {p.model}")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nPlease set API keys in .env file:")
        print("  - OPENAI_API_KEY")
        print("  - ANTHROPIC_API_KEY")
        print("  - GOOGLE_API_KEY")
        return

    if len(providers) < 2:
        print("\n⚠️  Warning: Need at least 2 providers for consensus!")
        print("Set additional API keys in .env file")
        return

    print()

    # Create scenario and purple agent
    scenario = SQLInjectionScenario()
    purple_agent = SimpleSQLDetector()

    print("Creating evaluation ecosystem with multi-LLM consensus...")
    ecosystem = create_ecosystem(
        scenario=scenario,
        llm_mode='multi',  # Multi-LLM mode
        llm_clients=providers,
        config={
            'use_sandbox': False,
            'num_boundary_probers': 1,
            'num_exploiters': 2,
            'num_mutators': 1,
        }
    )
    print("✅ Ecosystem created (multi-LLM mode with Dawid-Skene consensus)")
    print()

    # Run evaluation
    print("Running evaluation (2 rounds for demo)...")
    print("Note: This will query all LLMs for consensus...")
    result = ecosystem.evaluate(purple_agent, max_rounds=2)

    # Display results
    print()
    print("=" * 80)
    print("RESULTS - PHASE 2 (Multi-LLM Consensus)")
    print("=" * 80)
    print()
    print(f"F1 Score:      {result.metrics.f1_score:.3f}")
    print(f"Precision:     {result.metrics.precision:.3f}")
    print(f"Recall:        {result.metrics.recall:.3f}")
    print(f"Total Tests:   {result.metrics.total_tests}")
    print(f"Duration:      {result.duration_seconds:.1f}s")
    print()

    # Provider stats
    stats = get_provider_stats(providers)
    print("Multi-LLM Usage:")
    print(f"  Providers:   {stats['num_providers']}")
    print(f"  Requests:    {stats['total_requests']}")
    print(f"  Tokens:      {stats['total_tokens']:,}")
    print(f"  Total Cost:  ${stats['total_cost_usd']:.4f}")
    print()
    print("Per-Provider Breakdown:")
    for pstats in stats['providers']:
        print(f"  {pstats['provider']:10s} - ${pstats['total_cost_usd']:.4f} ({pstats['total_requests']} requests)")
    print()
    print("✅ Phase 2 provides calibrated consensus for maximum reliability!")
    print("💡 Use for production deployments and published benchmarks.")
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Multi-LLM Consensus Example',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python examples/multi_llm_example.py --phase 1   # Single LLM (development)
  python examples/multi_llm_example.py --phase 2   # Multi-LLM (production)
        """
    )

    parser.add_argument(
        '--phase',
        type=int,
        choices=[1, 2],
        required=True,
        help='Phase 1 (single LLM) or Phase 2 (multi-LLM consensus)'
    )

    args = parser.parse_args()

    print()
    if args.phase == 1:
        phase1_single_llm()
    else:
        phase2_multi_llm()


if __name__ == '__main__':
    main()
