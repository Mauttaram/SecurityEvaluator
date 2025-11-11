#!/usr/bin/env python3
"""
Integration Test - Orchestrator + 7 Agents + LLMs + Real Attacks

Tests the complete evaluation pipeline with all components.
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ImportError:
    pass  # dotenv not required

from framework.scenarios import PromptInjectionScenario
from framework.ecosystem import UnifiedEcosystem
from framework.models import Attack, TestResult, TestOutcome
from tests.llm_test_client import create_llm_clients


class TestPromptInjectionDetector:
    """
    Test Purple Agent for prompt injection detection.

    Production-like detector with pattern matching and heuristics.
    """

    def __init__(self, strictness: str = "balanced"):
        self.strictness = strictness
        self.detection_patterns = [
            "ignore previous instructions",
            "disregard",
            "forget",
            "system prompt",
            "reveal",
            "act as",
            "pretend",
            "override",
            "bypass",
            "developer mode"
        ]

    def get_name(self) -> str:
        return f"TestPromptInjectionDetector_{self.strictness}"

    def reset(self):
        pass

    def detect(self, attack: Attack) -> TestResult:
        """Detect prompt injection"""
        if hasattr(attack, 'payload'):
            prompt = str(attack.payload).lower()
        else:
            prompt = str(attack).lower()

        # Pattern matching
        detected = any(pattern in prompt for pattern in self.detection_patterns)

        # Adjust confidence based on strictness
        if detected:
            if self.strictness == "strict":
                confidence = 0.9
            elif self.strictness == "balanced":
                confidence = 0.7
            else:  # loose
                confidence = 0.6
        else:
            confidence = 0.2

        return TestResult(
            result_id=f"test_{hash(prompt)}",
            attack_id=getattr(attack, 'attack_id', 'unknown'),
            purple_agent=self.get_name(),
            detected=detected,
            confidence=confidence,
            outcome=TestOutcome.TRUE_POSITIVE if detected else TestOutcome.FALSE_NEGATIVE
        )


def test_integration_no_llm():
    """
    Integration test WITHOUT LLMs (algorithmic only).

    Tests:
    - Orchestrator coordination
    - All 7 agents initialized
    - BoundaryProber execution
    - Exploiter execution
    - Attack generation and testing
    - Metrics calculation
    """
    print("=" * 80)
    print("INTEGRATION TEST 1: Orchestrator + Agents (No LLM)")
    print("=" * 80)
    print()

    # Setup
    scenario = PromptInjectionScenario()
    purple_agent = TestPromptInjectionDetector(strictness="balanced")

    print("📋 Configuration:")
    print(f"   Scenario: {scenario.get_name()}")
    print(f"   Purple Agent: {purple_agent.get_name()}")
    print(f"   LLM Mode: Disabled")
    print(f"   Techniques: {len(scenario.get_techniques())}")
    print()

    # Create ecosystem
    print("🚀 Creating UnifiedEcosystem...")
    ecosystem = UnifiedEcosystem(
        scenario=scenario,
        use_llm=False,  # No LLM
        llm_clients=None,
        config={
            'use_sandbox': False,  # Disable for testing
            'use_cost_optimization': False,
            'use_coverage_tracking': True
        }
    )
    print(f"   ✅ Initialized with {len(ecosystem.agents)} agents")
    print()

    # Run evaluation
    print("🧪 Running evaluation (3 rounds)...")
    print()

    result = ecosystem.evaluate(
        purple_agent=purple_agent,
        max_rounds=3,
        budget_usd=None
    )

    # Verify results
    print()
    print("=" * 80)
    print("📊 INTEGRATION TEST RESULTS")
    print("=" * 80)
    print()

    print("Attacks Tested:")
    print(f"   Total: {result.total_attacks_tested}")
    print(f"   Unique: {len(result.attacks)}")
    print()

    print("Metrics:")
    print(f"   F1 Score:      {result.metrics.f1_score:.3f}")
    print(f"   Precision:     {result.metrics.precision:.3f}")
    print(f"   Recall:        {result.metrics.recall:.3f}")
    print(f"   Accuracy:      {result.metrics.accuracy:.3f}")
    print()

    print("Confusion Matrix:")
    print(f"   True Positives:  {result.metrics.true_positives}")
    print(f"   False Negatives: {result.metrics.false_negatives}")
    print(f"   False Positives: {result.metrics.false_positives}")
    print(f"   True Negatives:  {result.metrics.true_negatives}")
    print()

    # Assertions
    assert result.total_attacks_tested > 0, "❌ No attacks tested!"
    assert result.metrics.f1_score > 0, "❌ F1 score is 0!"
    print("✅ ALL CHECKS PASSED!")
    print()

    return result


def test_integration_with_mock_llm():
    """
    Integration test WITH mock LLMs.

    Tests:
    - Orchestrator coordination
    - All 7 agents with LLM support
    - ExploiterAgent with LLM generation
    - MutatorAgent with LLM mutations
    - LLMJudgeAgent with consensus
    - Cost tracking
    """
    print("=" * 80)
    print("INTEGRATION TEST 2: Orchestrator + Agents + Mock LLMs")
    print("=" * 80)
    print()

    # Setup
    scenario = PromptInjectionScenario()
    purple_agent = TestPromptInjectionDetector(strictness="balanced")

    # Create mock LLM clients
    print("🤖 Creating mock LLM clients...")
    llm_clients = create_llm_clients(mode="mock", num_clients=3)
    print(f"   ✅ Created {len(llm_clients)} mock LLM clients")
    for i, client in enumerate(llm_clients):
        print(f"      Client {i+1}: {client.model_name} ({client.response_style})")
    print()

    print("📋 Configuration:")
    print(f"   Scenario: {scenario.get_name()}")
    print(f"   Purple Agent: {purple_agent.get_name()}")
    print(f"   LLM Mode: Enabled (Mock)")
    print(f"   LLM Clients: {len(llm_clients)}")
    print()

    # Create ecosystem
    print("🚀 Creating UnifiedEcosystem with LLMs...")
    ecosystem = UnifiedEcosystem(
        scenario=scenario,
        use_llm=True,  # Enable LLM
        llm_clients=llm_clients,
        config={
            'use_sandbox': False,
            'use_cost_optimization': False,  # Disable for testing (ModelRouter interface issues)
            'use_coverage_tracking': False   # Disable for simpler testing
        }
    )
    print(f"   ✅ Initialized with {len(ecosystem.agents)} agents + LLM support")
    print()

    # Run evaluation
    print("🧪 Running evaluation (3 rounds with LLMs - limited for testing)...")
    print()

    result = ecosystem.evaluate(
        purple_agent=purple_agent,
        max_rounds=3,  # Reduced for testing
        budget_usd=1.0  # $1 budget
    )

    # Verify results
    print()
    print("=" * 80)
    print("📊 INTEGRATION TEST RESULTS (WITH LLMs)")
    print("=" * 80)
    print()

    print("Attacks Tested:")
    print(f"   Total: {result.total_attacks_tested}")
    print(f"   Unique: {len(result.attacks)}")
    print()

    print("Metrics:")
    print(f"   F1 Score:      {result.metrics.f1_score:.3f}")
    print(f"   Precision:     {result.metrics.precision:.3f}")
    print(f"   Recall:        {result.metrics.recall:.3f}")
    print(f"   Accuracy:      {result.metrics.accuracy:.3f}")
    print()

    print("Confusion Matrix:")
    print(f"   True Positives:  {result.metrics.true_positives}")
    print(f"   False Negatives: {result.metrics.false_negatives}")
    print(f"   False Positives: {result.metrics.false_positives}")
    print(f"   True Negatives:  {result.metrics.true_negatives}")
    print()

    print("LLM Usage:")
    total_llm_calls = sum(client.call_count for client in llm_clients)
    total_llm_cost = sum(client.get_cost() for client in llm_clients)
    print(f"   Total LLM Calls: {total_llm_calls}")
    print(f"   Total Cost: ${total_llm_cost:.4f}")
    print()

    if hasattr(result, 'coverage'):
        print("MITRE ATT&CK Coverage:")
        print(f"   Techniques Tested: {len(result.coverage.get('covered_techniques', []))}")
        print(f"   Coverage %: {result.coverage.get('percentage', 0):.1f}%")
        print()

    # Assertions
    assert result.total_attacks_tested > 0, "❌ No attacks tested!"
    assert result.metrics.f1_score > 0, "❌ F1 score is 0!"
    print("✅ ALL CHECKS PASSED (INCLUDING LLM INTEGRATION)!")
    print()

    return result


def test_agent_capabilities():
    """
    Test that all 7 agents are properly initialized and have correct capabilities.
    """
    print("=" * 80)
    print("AGENT CAPABILITIES TEST")
    print("=" * 80)
    print()

    scenario = PromptInjectionScenario()
    llm_clients = create_llm_clients(mode="mock", num_clients=3)

    ecosystem = UnifiedEcosystem(
        scenario=scenario,
        use_llm=True,
        llm_clients=llm_clients,
        config={}
    )

    print(f"Total Agents: {len(ecosystem.agents)}")
    print()

    expected_capabilities = {
        'BoundaryProber': ['PROBE'],
        'Exploiter': ['GENERATE', 'EXPLOIT'],
        'Mutator': ['MUTATE'],
        'Validator': ['VALIDATE'],
        'Perspective': ['EVALUATE'],
        'LLMJudge': ['EVALUATE'],
        'Counterfactual': ['ANALYZE']
    }

    agent_types_found = {}
    for agent in ecosystem.agents:
        agent_type = agent.__class__.__name__.replace('Agent', '')
        if agent_type not in agent_types_found:
            agent_types_found[agent_type] = 0
        agent_types_found[agent_type] += 1

        print(f"✅ {agent.agent_id}:")
        print(f"   Type: {agent_type}")
        print(f"   Capabilities: {[c.name for c in agent.capabilities.capabilities]}")
        print()

    print("Agent Type Summary:")
    for agent_type, count in agent_types_found.items():
        print(f"   {agent_type}: {count} instances")
    print()

    # Verify we have all agent types
    for expected_type in expected_capabilities.keys():
        assert expected_type in agent_types_found, f"❌ Missing agent type: {expected_type}"

    print("✅ ALL 7 AGENT TYPES PRESENT!")
    print()


def main():
    """Run all integration tests"""
    print("\n")
    print("*" * 80)
    print("COMPREHENSIVE INTEGRATION TEST SUITE")
    print("*" * 80)
    print("\n")

    try:
        # Test 1: Agent capabilities
        test_agent_capabilities()

        # Test 2: Integration without LLM
        print("\n")
        result1 = test_integration_no_llm()

        # Test 3: Integration with mock LLM
        print("\n")
        result2 = test_integration_with_mock_llm()

        # Summary
        print()
        print("*" * 80)
        print("✅ ALL INTEGRATION TESTS PASSED!")
        print("*" * 80)
        print()
        print("Summary:")
        print(f"   Test 1 (No LLM): {result1.total_attacks_tested} attacks, F1={result1.metrics.f1_score:.3f}")
        print(f"   Test 2 (Mock LLM): {result2.total_attacks_tested} attacks, F1={result2.metrics.f1_score:.3f}")
        print()

        return 0

    except AssertionError as e:
        print()
        print("*" * 80)
        print(f"❌ TEST FAILED: {e}")
        print("*" * 80)
        return 1

    except Exception as e:
        print()
        print("*" * 80)
        print(f"❌ ERROR: {e}")
        print("*" * 80)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
