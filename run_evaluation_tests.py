#!/usr/bin/env python3
"""
Complete Evaluation and Testing Script

Two modes:
1. Framework Validation (--validate): Test that the Green Agent framework is working
2. Scenario Evaluation (default): Use the Green Agent to evaluate Purple Agent detectors

Usage:
    # Framework Validation (test the testing framework)
    python run_evaluation_tests.py --validate

    # Scenario Evaluation (test Purple Agents)
    python run_evaluation_tests.py --scenario prompt --max-rounds 10
    python run_evaluation_tests.py --scenario sql --llm
    python run_evaluation_tests.py --scenario all --quick
"""

import argparse
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ImportError:
    pass  # dotenv not required

from framework.scenarios import SQLInjectionScenario, PromptInjectionScenario, ActiveScanningScenario
from framework import create_ecosystem


# ============================================================================
# SAMPLE PURPLE AGENTS (Detectors to Test)
# ============================================================================

class SimpleSQLDetector:
    """
    Simple pattern-based SQL injection detector.
    This is the Purple Agent being evaluated.
    """

    def get_name(self) -> str:
        """Return agent name."""
        return "SimpleSQLDetector"

    def reset(self):
        """Reset agent state."""
        pass  # Stateless detector

    def detect(self, attack):
        """Detect SQL injection patterns."""
        # Handle both string and Attack object
        if hasattr(attack, 'payload'):
            code_sample = str(attack.payload)
        else:
            code_sample = str(attack)

        code_upper = code_sample.upper()

        # Simple keyword detection
        sql_keywords = [
            'UNION', 'SELECT', 'DROP', 'DELETE', 'INSERT', 'UPDATE',
            'OR 1=1', "OR '1'='1", '--', '#', '/*', 'SLEEP(', 'WAITFOR'
        ]

        # Check for SQL injection patterns
        detected = any(keyword in code_upper for keyword in sql_keywords)

        # Check for dangerous quote patterns
        if "'" in code_sample or '"' in code_sample:
            if any(kw in code_upper for kw in ['OR', 'AND', 'UNION', 'SELECT']):
                detected = True

        # Return TestResult-compatible format
        from framework.models import TestResult, TestOutcome
        return TestResult(
            result_id=f"test_{hash(code_sample)}",
            attack_id=getattr(attack, 'attack_id', 'unknown'),
            purple_agent="SimpleSQLDetector",
            detected=detected,
            confidence=0.8 if detected else 0.2,
            outcome=TestOutcome.TRUE_POSITIVE if detected else TestOutcome.FALSE_NEGATIVE
        )


class SimplePromptInjectionDetector:
    """
    Simple prompt injection detector.
    This is the Purple Agent being evaluated.
    """

    def get_name(self) -> str:
        """Return agent name."""
        return "SimplePromptInjectionDetector"

    def reset(self):
        """Reset agent state."""
        pass  # Stateless detector

    def detect(self, attack):
        """Detect prompt injection patterns."""
        # Handle both string and Attack object
        if hasattr(attack, 'payload'):
            prompt = str(attack.payload)
        else:
            prompt = str(attack)

        prompt_lower = prompt.lower()

        # Jailbreak patterns
        jailbreak_patterns = [
            'ignore previous instructions',
            'disregard',
            'forget',
            'new instructions',
            'act as',
            'pretend',
            'roleplay',
            'dan mode',
            'developer mode'
        ]

        # System prompt leaking
        leak_patterns = [
            'system prompt',
            'show prompt',
            'reveal instructions',
            'what are your instructions',
            'print system',
        ]

        # Role manipulation
        role_patterns = [
            'you are now',
            'switch roles',
            'assume',
        ]

        # Instruction override
        override_patterns = [
            'override',
            'disable',
            'turn off',
            'bypass'
        ]

        # Check patterns
        detected = (
            any(pattern in prompt_lower for pattern in jailbreak_patterns) or
            any(pattern in prompt_lower for pattern in leak_patterns) or
            any(pattern in prompt_lower for pattern in role_patterns) or
            any(pattern in prompt_lower for pattern in override_patterns)
        )

        # Return TestResult-compatible format
        from framework.models import TestResult, TestOutcome
        return TestResult(
            result_id=f"test_{hash(prompt)}",
            attack_id=getattr(attack, 'attack_id', 'unknown'),
            purple_agent="SimplePromptInjectionDetector",
            detected=detected,
            confidence=0.9 if detected else 0.1,
            outcome=TestOutcome.TRUE_POSITIVE if detected else TestOutcome.FALSE_NEGATIVE
        )


class SimpleScanDetector:
    """
    Simple active scanning detector.
    This is the Purple Agent being evaluated.
    """

    def __init__(self):
        self.request_history = []
        self.suspicious_threshold = 5

    def get_name(self) -> str:
        """Return agent name."""
        return "SimpleScanDetector"

    def reset(self):
        """Reset agent state."""
        self.request_history = []

    def detect(self, attack):
        """Detect active scanning patterns."""
        # Handle both string and Attack object
        if hasattr(attack, 'payload'):
            path = str(attack.payload)
            metadata = attack.metadata
        else:
            path = str(attack)
            metadata = {}

        # Track request
        self.request_history.append({
            'path': path,
            'timestamp': time.time(),
            'metadata': metadata
        })

        # Detection logic
        detected = False
        detection_reasons = []

        # 1. Check for known scanner paths
        scanner_paths = [
            'admin', 'phpmyadmin', 'backup', '.env', 'config',
            'swagger', 'openapi', 'ai-plugin', 'agent-card'
        ]
        if any(scanner_path in path.lower() for scanner_path in scanner_paths):
            detected = True
            detection_reasons.append('known_scanner_path')

        # 2. Check for rapid requests (more than 5 in last second)
        current_time = time.time()
        recent_requests = [
            r for r in self.request_history
            if current_time - r['timestamp'] < 1.0
        ]
        if len(recent_requests) > 5:
            detected = True
            detection_reasons.append('rapid_requests')

        # 3. Check for sequential enumeration pattern
        if len(self.request_history) >= 3:
            recent_paths = [r['path'] for r in self.request_history[-3:]]
            # If paths are very similar (same prefix), likely enumeration
            if len(set(p.split('/')[0] if '/' in p else p for p in recent_paths)) == 1:
                detected = True
                detection_reasons.append('sequential_enumeration')

        # 4. Check for suspicious User-Agent
        user_agent = metadata.get('user_agent', '')
        suspicious_uas = ['curl', 'wget', 'scanner', 'nikto', 'nmap']
        if any(sua in user_agent.lower() for sua in suspicious_uas):
            detected = True
            detection_reasons.append('suspicious_user_agent')

        # 5. Check for URL encoding evasion
        if '%2F' in path or '%2E' in path:
            detected = True
            detection_reasons.append('url_encoding_evasion')

        # Return TestResult-compatible format
        from framework.models import TestResult, TestOutcome
        return TestResult(
            result_id=f"test_{hash(path)}",
            attack_id=getattr(attack, 'attack_id', 'unknown'),
            purple_agent="SimpleScanDetector",
            detected=detected,
            confidence=0.85 if detected else 0.15,
            outcome=TestOutcome.TRUE_POSITIVE if detected else TestOutcome.FALSE_NEGATIVE,
            detection_reason=', '.join(detection_reasons) if detection_reasons else None
        )


# ============================================================================
# TEST EXECUTION FUNCTIONS
# ============================================================================

def test_sql_injection(use_llm=False, max_rounds=5):
    """Test SQL Injection scenario."""
    print("=" * 80)
    print("🔍 TESTING SQL INJECTION DETECTION")
    print("=" * 80)
    print()

    # Create scenario and Purple Agent
    scenario = SQLInjectionScenario()
    purple_agent = SimpleSQLDetector()

    print("📋 Setup:")
    print(f"   Scenario: SQL Injection Detection")
    print(f"   Purple Agent: SimpleSQLDetector (pattern-based)")
    print(f"   LLM Mode: {'Enabled' if use_llm else 'Disabled'}")
    print(f"   Max Rounds: {max_rounds}")
    print()

    # Create ecosystem
    print("🚀 Creating evaluation ecosystem...")
    ecosystem = create_ecosystem(
        scenario=scenario,
        llm_mode='cheap' if use_llm else 'none',
        config={
            'use_sandbox': False,  # Disable for local testing
            'num_boundary_probers': 2,
            'num_exploiters': 3,
            'num_mutators': 2,
        }
    )
    print("   ✅ Ecosystem created")
    print()

    # Run evaluation
    print("🧪 Running evaluation...")
    print("   This will take a few minutes...")
    print()

    try:
        result = ecosystem.evaluate(purple_agent, max_rounds=max_rounds)

        # Display results
        print()
        print("=" * 80)
        print("📊 SQL INJECTION EVALUATION RESULTS")
        print("=" * 80)
        print()

        print("Overall Performance:")
        print(f"   F1 Score:      {result.metrics.f1_score:.3f}")
        print(f"   Precision:     {result.metrics.precision:.3f}")
        print(f"   Recall:        {result.metrics.recall:.3f}")
        print(f"   Accuracy:      {result.metrics.accuracy:.3f}")
        print()

        print("Confusion Matrix:")
        print(f"   True Positives:  {result.metrics.true_positives}")
        print(f"   False Negatives: {result.metrics.false_negatives} ⚠️  (Missed attacks)")
        print(f"   False Positives: {result.metrics.false_positives}")
        print(f"   True Negatives:  {result.metrics.true_negatives}")
        print()

        if hasattr(result, 'per_technique') and result.per_technique:
            print("Per-Technique Performance:")
            for technique, metrics in result.per_technique.items():
                print(f"   {technique:20s} F1={metrics.f1_score:.3f}")
            print()

        total_tests = (result.metrics.true_positives + result.metrics.true_negatives +
                      result.metrics.false_positives + result.metrics.false_negatives)
        print(f"Total Tests: {total_tests}")
        if result.end_time and result.start_time:
            duration = (result.end_time - result.start_time).total_seconds()
            print(f"Time: {duration:.1f}s")
        else:
            print(f"Time: N/A")
        if use_llm:
            print(f"Cost: ${result.metrics.total_cost_usd:.2f}")
        print()

        # Assessment
        if result.metrics.f1_score >= 0.9:
            print("✅ EXCELLENT - Purple Agent performs very well!")
        elif result.metrics.f1_score >= 0.7:
            print("⚠️  GOOD - Purple Agent is decent but has weaknesses")
        else:
            print("❌ WEAK - Purple Agent needs significant improvement")

        print()
        return result

    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_prompt_injection(use_llm=False, max_rounds=5):
    """Test Prompt Injection scenario."""
    print("=" * 80)
    print("🔍 TESTING PROMPT INJECTION DETECTION")
    print("=" * 80)
    print()

    # Create scenario and Purple Agent
    scenario = PromptInjectionScenario()
    purple_agent = SimplePromptInjectionDetector()

    print("📋 Setup:")
    print(f"   Scenario: Prompt Injection Detection")
    print(f"   Purple Agent: SimplePromptInjectionDetector (pattern-based)")
    print(f"   LLM Mode: {'Enabled' if use_llm else 'Disabled'}")
    print(f"   Max Rounds: {max_rounds}")
    print()

    # Create ecosystem
    print("🚀 Creating evaluation ecosystem...")
    ecosystem = create_ecosystem(
        scenario=scenario,
        llm_mode='cheap' if use_llm else 'none',
        config={
            'use_sandbox': False,  # Disable for local testing
            'num_boundary_probers': 2,
            'num_exploiters': 3,
            'num_mutators': 2,
        }
    )
    print("   ✅ Ecosystem created")
    print()

    # Run evaluation
    print("🧪 Running evaluation...")
    print("   This will take a few minutes...")
    print()

    try:
        result = ecosystem.evaluate(purple_agent, max_rounds=max_rounds)

        # Display results
        print()
        print("=" * 80)
        print("📊 PROMPT INJECTION EVALUATION RESULTS")
        print("=" * 80)
        print()

        print("Overall Performance:")
        print(f"   F1 Score:      {result.metrics.f1_score:.3f}")
        print(f"   Precision:     {result.metrics.precision:.3f}")
        print(f"   Recall:        {result.metrics.recall:.3f}")
        print(f"   Accuracy:      {result.metrics.accuracy:.3f}")
        print()

        print("Confusion Matrix:")
        print(f"   True Positives:  {result.metrics.true_positives}")
        print(f"   False Negatives: {result.metrics.false_negatives} ⚠️  (Missed attacks)")
        print(f"   False Positives: {result.metrics.false_positives}")
        print(f"   True Negatives:  {result.metrics.true_negatives}")
        print()

        if hasattr(result, 'per_technique') and result.per_technique:
            print("Per-Technique Performance:")
            for technique, metrics in result.per_technique.items():
                print(f"   {technique:20s} F1={metrics.f1_score:.3f}")
            print()

        total_tests = (result.metrics.true_positives + result.metrics.true_negatives +
                      result.metrics.false_positives + result.metrics.false_negatives)
        print(f"Total Tests: {total_tests}")
        if result.end_time and result.start_time:
            duration = (result.end_time - result.start_time).total_seconds()
            print(f"Time: {duration:.1f}s")
        else:
            print(f"Time: N/A")
        if use_llm:
            print(f"Cost: ${result.metrics.total_cost_usd:.2f}")
        print()

        # Assessment
        if result.metrics.f1_score >= 0.9:
            print("✅ EXCELLENT - Purple Agent performs very well!")
        elif result.metrics.f1_score >= 0.7:
            print("⚠️  GOOD - Purple Agent is decent but has weaknesses")
        else:
            print("❌ WEAK - Purple Agent needs significant improvement")

        print()
        return result

    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_active_scanning(use_llm=False, max_rounds=5):
    """Test Active Scanning scenario."""
    print("=" * 80)
    print("🔍 TESTING ACTIVE SCANNING DETECTION (MITRE T1595)")
    print("=" * 80)
    print()

    # Create scenario and Purple Agent
    scenario = ActiveScanningScenario()
    purple_agent = SimpleScanDetector()

    print("📋 Setup:")
    print(f"   Scenario: Active Scanning Detection (MITRE T1595)")
    print(f"   Purple Agent: SimpleScanDetector (pattern-based)")
    print(f"   LLM Mode: {'Enabled' if use_llm else 'Disabled'}")
    print(f"   Max Rounds: {max_rounds}")
    print()

    # Create ecosystem
    print("🚀 Creating evaluation ecosystem...")
    ecosystem = create_ecosystem(
        scenario=scenario,
        llm_mode='cheap' if use_llm else 'none',
        config={
            'use_sandbox': False,  # Disable for local testing
            'num_boundary_probers': 2,
            'num_exploiters': 3,
            'num_mutators': 2,
        }
    )
    print("   ✅ Ecosystem created")
    print()

    # Run evaluation
    print("🧪 Running evaluation...")
    print("   This will take a few minutes...")
    print()

    try:
        result = ecosystem.evaluate(purple_agent, max_rounds=max_rounds)

        # Display results
        print()
        print("=" * 80)
        print("📊 ACTIVE SCANNING EVALUATION RESULTS")
        print("=" * 80)
        print()

        print("Overall Performance:")
        print(f"   F1 Score:      {result.metrics.f1_score:.3f}")
        print(f"   Precision:     {result.metrics.precision:.3f}")
        print(f"   Recall:        {result.metrics.recall:.3f}")
        print(f"   Accuracy:      {result.metrics.accuracy:.3f}")
        print()

        print("Confusion Matrix:")
        print(f"   True Positives:  {result.metrics.true_positives}")
        print(f"   False Negatives: {result.metrics.false_negatives} ⚠️  (Missed scans)")
        print(f"   False Positives: {result.metrics.false_positives}")
        print(f"   True Negatives:  {result.metrics.true_negatives}")
        print()

        if hasattr(result, 'per_technique') and result.per_technique:
            print("Per-Technique Performance:")
            for technique, metrics in result.per_technique.items():
                print(f"   {technique:25s} F1={metrics.f1_score:.3f}")
            print()

        total_tests = (result.metrics.true_positives + result.metrics.true_negatives +
                      result.metrics.false_positives + result.metrics.false_negatives)
        print(f"Total Tests: {total_tests}")
        if result.end_time and result.start_time:
            duration = (result.end_time - result.start_time).total_seconds()
            print(f"Time: {duration:.1f}s")
        else:
            print(f"Time: N/A")
        if use_llm:
            print(f"Cost: ${result.metrics.total_cost_usd:.2f}")
        print()

        # Assessment
        if result.metrics.f1_score >= 0.9:
            print("✅ EXCELLENT - Purple Agent detects scans very well!")
        elif result.metrics.f1_score >= 0.7:
            print("⚠️  GOOD - Purple Agent is decent but has weaknesses")
        else:
            print("❌ WEAK - Purple Agent needs significant improvement")

        print()
        return result

    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# FRAMEWORK VALIDATION
# ============================================================================

def validate_framework():
    """
    Validate that the Green Agent framework is working properly.

    Tests:
    - Agent initialization and capabilities
    - Orchestrator coordination
    - LLM integration (mock)
    - Attack generation and execution
    - Metrics calculation
    """
    print()
    print("=" * 80)
    print("🔧 FRAMEWORK VALIDATION MODE")
    print("=" * 80)
    print()
    print("This validates that the Green Agent framework components are working.")
    print()

    try:
        # Import test modules
        from tests.test_agents_basic import run_basic_tests
        from tests.test_integration_full import (
            test_integration_no_llm,
            test_integration_with_mock_llm,
            test_agent_capabilities
        )

        print("=" * 80)
        print("TEST 1: Agent Capabilities")
        print("=" * 80)
        print()

        test_agent_capabilities()

        print()
        print("=" * 80)
        print("TEST 2: Basic Agent Tests")
        print("=" * 80)
        print()

        success = run_basic_tests()
        if not success:
            print("❌ Basic agent tests failed!")
            return False

        print()
        print("=" * 80)
        print("TEST 3: Integration Test (No LLM)")
        print("=" * 80)
        print()

        result1 = test_integration_no_llm()
        if result1.total_attacks_tested == 0:
            print("❌ No attacks executed!")
            return False

        print()
        print("=" * 80)
        print("TEST 4: Integration Test (Mock LLM)")
        print("=" * 80)
        print()

        result2 = test_integration_with_mock_llm()
        if result2.total_attacks_tested == 0:
            print("❌ No attacks executed!")
            return False

        # Summary
        print()
        print("=" * 80)
        print("✅ FRAMEWORK VALIDATION PASSED")
        print("=" * 80)
        print()
        print("Summary:")
        print(f"  • All agents initialized and working")
        print(f"  • Orchestrator coordinating properly")
        print(f"  • LLM integration functional")
        print(f"  • Test 1 (No LLM): {result1.total_attacks_tested} attacks, F1={result1.metrics.f1_score:.3f}")
        print(f"  • Test 2 (Mock LLM): {result2.total_attacks_tested} attacks, F1={result2.metrics.f1_score:.3f}")
        print()
        print("🎉 Green Agent framework is ready for production use!")
        print()

        return True

    except Exception as e:
        print()
        print("=" * 80)
        print("❌ FRAMEWORK VALIDATION FAILED")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main test execution."""
    parser = argparse.ArgumentParser(
        description='Green Agent Framework - Validation and Evaluation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Framework Validation (test the framework)
  python run_evaluation_tests.py --validate

  # Scenario Evaluation (test Purple Agents)
  python run_evaluation_tests.py --scenario prompt --max-rounds 10
  python run_evaluation_tests.py --scenario sql --llm
  python run_evaluation_tests.py --scenario all --quick
        """
    )

    parser.add_argument(
        '--validate',
        action='store_true',
        help='Run framework validation tests (verifies Green Agent is working)'
    )
    parser.add_argument(
        '--scenario',
        choices=['sql', 'prompt', 'active_scan', 'all'],
        default='all',
        help='Which scenario to test (default: all)'
    )
    parser.add_argument(
        '--llm',
        action='store_true',
        help='Enable LLM support (requires OPENAI_API_KEY)'
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Quick test mode (2 rounds instead of 5)'
    )
    parser.add_argument(
        '--max-rounds',
        type=int,
        default=None,
        dest='max_rounds',
        help='Number of evaluation rounds (default: 5, or 2 with --quick)'
    )

    args = parser.parse_args()

    # Framework validation mode
    if args.validate:
        success = validate_framework()
        return 0 if success else 1

    # Determine number of rounds for scenario evaluation
    if args.max_rounds:
        max_rounds = args.max_rounds
    elif args.quick:
        max_rounds = 2
    else:
        max_rounds = 5

    # Print header
    print()
    print("=" * 80)
    print("🚀 SECURITY EVALUATION FRAMEWORK - TEST SUITE")
    print("=" * 80)
    print()
    print(f"Configuration:")
    print(f"   Scenario: {args.scenario}")
    print(f"   LLM Mode: {'Enabled' if args.llm else 'Disabled'}")
    print(f"   Max Rounds: {max_rounds}")
    print(f"   Test Mode: {'Quick' if args.quick else 'Full'}")
    print()

    if args.llm:
        print("ℹ️  LLM mode enabled - make sure OPENAI_API_KEY is set in .env")
        print()

    results = {}

    # Run SQL Injection test
    if args.scenario in ['sql', 'all']:
        sql_result = test_sql_injection(use_llm=args.llm, max_rounds=max_rounds)
        results['sql_injection'] = sql_result

        if args.scenario == 'all':
            print()
            print("─" * 80)
            print()

    # Run Prompt Injection test
    if args.scenario in ['prompt', 'all']:
        prompt_result = test_prompt_injection(use_llm=args.llm, max_rounds=max_rounds)
        results['prompt_injection'] = prompt_result

        if args.scenario == 'all':
            print()
            print("─" * 80)
            print()

    # Run Active Scanning test
    if args.scenario in ['active_scan', 'all']:
        active_scan_result = test_active_scanning(use_llm=args.llm, max_rounds=max_rounds)
        results['active_scanning'] = active_scan_result

    # Summary
    if args.scenario == 'all':
        print()
        print("=" * 80)
        print("📈 SUMMARY")
        print("=" * 80)
        print()

        if results.get('sql_injection'):
            sql_f1 = results['sql_injection'].metrics.f1_score
            print(f"SQL Injection:      F1={sql_f1:.3f}")

        if results.get('prompt_injection') and results['prompt_injection'] is not None:
            prompt_f1 = results['prompt_injection'].metrics.f1_score
            print(f"Prompt Injection:   F1={prompt_f1:.3f}")

        if results.get('active_scanning') and results['active_scanning'] is not None:
            active_f1 = results['active_scanning'].metrics.f1_score
            print(f"Active Scanning:    F1={active_f1:.3f}")

        print()

    if any(r is not None for r in results.values()):
        print("✅ Tests completed!")
    else:
        print("⚠️  Some tests were skipped")

    print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
