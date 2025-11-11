#!/usr/bin/env python3
"""
Production-Safe Example: SQL Injection Evaluation

Demonstrates all three production enhancements:
- Enhancement 5: Formal Sandbox
- Enhancement 6: Cost Optimization (no LLM for demo)
- Enhancement 7: Coverage Tracking

This configuration is safe for production deployments.
"""

import logging
from datetime import datetime

from framework.ecosystem import UnifiedEcosystem
from scenarios.sql_injection import SQLInjectionScenario, SimplePatternPurpleAgent


def main():
    """Run production-safe evaluation."""

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    logger.info("="*60)
    logger.info("Production-Safe Security Evaluation")
    logger.info("="*60)

    # =========================================================================
    # STEP 1: Create Production-Safe Configuration
    # =========================================================================

    logger.info("\n📋 Step 1: Configuring production-safe settings...")

    config = {
        # Enhancement 5: Formal Sandbox (CRITICAL for production)
        'use_sandbox': True,
        'sandbox_config': {
            'image': 'python:3.10-slim',
            'cpu_limit': 0.5,              # Limit to 0.5 CPUs
            'memory_limit': '512m',         # Limit to 512MB RAM
            'timeout_seconds': 30,          # Kill after 30 seconds
            'enable_network': False         # Block all network access
        },

        # Enhancement 6: Cost Optimization
        # (Disabled for this demo since no LLM, but shown for reference)
        'use_cost_optimization': False,

        # Enhancement 7: Coverage Tracking
        'use_coverage_tracking': True,
        'taxonomy': 'MITRE_ATT&CK',

        # Agent configuration (small for demo)
        'num_boundary_probers': 1,
        'num_exploiters': 2,
        'num_mutators': 1,
        'num_validators': 1
    }

    logger.info("✅ Sandbox enabled: Container isolation active")
    logger.info("✅ Coverage tracking enabled: MITRE ATT&CK monitoring")
    logger.info("✅ Resource limits: 0.5 CPU, 512MB RAM, 30s timeout")

    # =========================================================================
    # STEP 2: Initialize Ecosystem
    # =========================================================================

    logger.info("\n🔧 Step 2: Initializing ecosystem...")

    scenario = SQLInjectionScenario()
    ecosystem = UnifiedEcosystem(
        scenario=scenario,
        use_llm=False,  # Set to True for LLM-enhanced evaluation
        config=config
    )

    logger.info(f"✅ Ecosystem initialized with {len(ecosystem.agents)} agents")
    logger.info(f"   Scenario: {scenario.get_name()}")
    logger.info(f"   Techniques: {', '.join(scenario.get_techniques())}")

    # =========================================================================
    # STEP 3: Create Purple Agent to Evaluate
    # =========================================================================

    logger.info("\n🎯 Step 3: Creating purple agent...")

    # Simple pattern-based SQL injection detector
    purple_agent = SimplePatternPurpleAgent(
        patterns=[
            "'", '"',           # Quote characters
            'OR', 'AND',        # Logic operators
            'UNION', 'SELECT',  # SQL keywords
            'DROP', 'DELETE',   # Dangerous operations
            '--', '/*', '*/'    # Comment characters
        ]
    )

    logger.info(f"✅ Purple agent created: {purple_agent.get_name()}")
    logger.info(f"   Detection patterns: {len(purple_agent.patterns)}")

    # =========================================================================
    # STEP 4: Run Evaluation
    # =========================================================================

    logger.info("\n🚀 Step 4: Running evaluation...")
    logger.info("   Max rounds: 3 (small for demo)")
    logger.info("   Budget: Unlimited (no LLMs used)")

    start_time = datetime.now()

    result = ecosystem.evaluate(
        purple_agent=purple_agent,
        max_rounds=3,
        budget_usd=None  # No budget limit (no LLMs used)
    )

    elapsed = (datetime.now() - start_time).total_seconds()

    logger.info(f"✅ Evaluation complete in {elapsed:.1f}s")

    # =========================================================================
    # STEP 5: Show Results
    # =========================================================================

    logger.info("\n" + "="*60)
    logger.info("📊 EVALUATION RESULTS")
    logger.info("="*60)

    # Metrics
    logger.info("\n🎯 Detection Metrics:")
    logger.info(f"   F1 Score:    {result.metrics.f1_score:.3f}")
    logger.info(f"   Precision:   {result.metrics.precision:.3f}")
    logger.info(f"   Recall:      {result.metrics.recall:.3f}")
    logger.info(f"   FPR:         {result.metrics.false_positive_rate:.3f}")
    logger.info(f"   FNR:         {result.metrics.false_negative_rate:.3f}")

    # Statistics
    logger.info("\n📈 Statistics:")
    logger.info(f"   Total attacks tested: {result.total_attacks_tested}")
    logger.info(f"   Evasions found:       {len(result.get_evasions())}")
    logger.info(f"   Execution time:       {result.total_time_seconds:.1f}s")
    logger.info(f"   Total cost:           ${result.total_cost_usd:.2f}")

    # Evasions (if any)
    evasions = result.get_evasions()
    if evasions:
        logger.info("\n⚠️  Evasions Discovered:")
        for i, evasion in enumerate(evasions[:5]):  # Show first 5
            logger.info(f"   {i+1}. {evasion.attack.payload[:60]}...")
        if len(evasions) > 5:
            logger.info(f"   ... and {len(evasions) - 5} more")
    else:
        logger.info("\n✅ No evasions discovered!")

    # =========================================================================
    # STEP 6: Coverage Report
    # =========================================================================

    logger.info("\n" + "="*60)
    logger.info("📊 MITRE ATT&CK COVERAGE")
    logger.info("="*60)

    coverage_report = ecosystem.get_coverage_report()

    if coverage_report:
        summary = coverage_report['coverage_summary']

        logger.info(f"\n📈 Coverage Summary:")
        logger.info(f"   Total techniques:      {summary['total_techniques']}")
        logger.info(f"   Covered:               {summary['covered']} ({summary['coverage_percentage']:.1f}%)")
        logger.info(f"   Partially covered:     {summary['partially_covered']}")
        logger.info(f"   Uncovered:             {summary['uncovered']}")

        # Covered techniques
        if coverage_report['covered_techniques']:
            logger.info(f"\n✅ Covered Techniques:")
            for tech in coverage_report['covered_techniques'][:5]:
                logger.info(f"   • {tech}")
            if len(coverage_report['covered_techniques']) > 5:
                logger.info(f"   ... and {len(coverage_report['covered_techniques']) - 5} more")

        # Priority next techniques
        if coverage_report['priority_next_techniques']:
            logger.info(f"\n🎯 Priority Next Techniques:")
            for item in coverage_report['priority_next_techniques'][:3]:
                logger.info(f"   • {item['technique']} (priority: {item['priority']:.2f})")

        # Coverage debt
        debt = coverage_report['coverage_debt']
        logger.info(f"\n📉 Coverage Debt:")
        logger.info(f"   Total uncovered:       {debt['total_debt']}")
        logger.info(f"   High priority:         {debt['high_priority_debt']}")
        logger.info(f"   Time to full coverage: {debt['estimated_time_to_full_coverage']}")

    # =========================================================================
    # STEP 7: Next Steps Suggestion
    # =========================================================================

    logger.info("\n" + "="*60)
    logger.info("💡 NEXT STEPS")
    logger.info("="*60)

    suggestion = ecosystem.suggest_next_scenario()

    if suggestion and suggestion.get('suggestion') is not None:
        logger.info(f"\n🎯 Suggested Next Scenario:")
        logger.info(f"   Technique:     {suggestion['suggested_technique']}")
        logger.info(f"   Priority:      {suggestion['priority_score']:.2f}")
        logger.info(f"   Impact:        {suggestion['coverage_impact']} techniques")

        guide = suggestion['implementation_guide']
        logger.info(f"\n📖 Implementation Guide:")
        logger.info(f"   Time estimate: {guide['estimated_time']}")
        logger.info(f"   Scenario:      {guide['scenario_class']}")

        logger.info(f"\n💻 Generate template with:")
        logger.info(f"   python -m framework.coverage_cli template {suggestion['suggested_technique']}")
    else:
        logger.info("\n🎉 Full coverage achieved!")

    # =========================================================================
    # STEP 8: eBOM (Evaluation Bill of Materials)
    # =========================================================================

    logger.info("\n" + "="*60)
    logger.info("📦 EVALUATION REPRODUCIBILITY (eBOM)")
    logger.info("="*60)

    ebom = result.ebom

    logger.info(f"\n🔧 Framework:")
    logger.info(f"   Name:    {ebom['framework']['name']}")
    logger.info(f"   Version: {ebom['framework']['version']}")
    logger.info(f"   Scenario: {ebom['framework']['scenario']}")

    logger.info(f"\n🤖 Agents Used:")
    for agent_info in ebom['agents']:
        logger.info(f"   • {agent_info['agent_id']} ({agent_info['role']}) - {agent_info['contributions']} contributions")

    logger.info(f"\n📊 Resources:")
    logger.info(f"   Total cost:    ${ebom['resources']['total_cost_usd']:.2f}")
    logger.info(f"   Total time:    {ebom['resources']['total_time_seconds']:.1f}s")
    logger.info(f"   LLM calls:     {ebom['resources']['llm_calls']}")
    logger.info(f"   Attacks tested: {ebom['resources']['total_attacks_tested']}")

    # =========================================================================
    # FINAL MESSAGE
    # =========================================================================

    logger.info("\n" + "="*60)
    logger.info("✅ PRODUCTION-SAFE EVALUATION COMPLETE")
    logger.info("="*60)

    logger.info("\n🔒 Security Features Active:")
    logger.info("   ✅ Container isolation (sandbox)")
    logger.info("   ✅ seccomp syscall filtering")
    logger.info("   ✅ Resource limits (CPU, RAM, time)")
    logger.info("   ✅ Network isolation")
    logger.info("   ✅ Coverage tracking")

    logger.info("\n💡 For detailed production guide, see:")
    logger.info("   PRODUCTION_GUIDE.md")

    logger.info("\n🧪 To run tests:")
    logger.info("   pytest tests/ -v")

    logger.info("\n" + "="*60)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error(f"❌ Error: {e}")
        if 'Docker' in str(e):
            logging.error("\n💡 Docker not available. To run this example:")
            logging.error("   1. Install Docker: https://docs.docker.com/get-docker/")
            logging.error("   2. Start Docker daemon")
            logging.error("   3. Run this example again")
        raise
