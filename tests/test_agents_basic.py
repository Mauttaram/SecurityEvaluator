#!/usr/bin/env python3
"""
Basic Agent Tests - Simplified version that works with actual implementations

Tests that agents can be initialized and have correct capabilities.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest

from framework.scenarios import PromptInjectionScenario
from framework.knowledge_base import InMemoryKnowledgeBase
from framework.ecosystem import UnifiedEcosystem


class TestAgentsBasic(unittest.TestCase):
    """Test that all agents can be initialized"""

    def test_ecosystem_initialization(self):
        """Test that ecosystem initializes all agents"""
        scenario = PromptInjectionScenario()

        ecosystem = UnifiedEcosystem(
            scenario=scenario,
            use_llm=False,
            llm_clients=None,
            config={}
        )

        # Check agents were created
        self.assertIsNotNone(ecosystem.agents)
        self.assertGreater(len(ecosystem.agents), 0)

        print(f"\n✅ Ecosystem initialized with {len(ecosystem.agents)} agents")

    def test_agent_capabilities(self):
        """Test that agents have correct capabilities"""
        scenario = PromptInjectionScenario()

        ecosystem = UnifiedEcosystem(
            scenario=scenario,
            use_llm=False,
            llm_clients=None,
            config={}
        )

        # Count agents by type
        agent_types = {}
        for agent in ecosystem.agents:
            agent_type = agent.__class__.__name__
            if agent_type not in agent_types:
                agent_types[agent_type] = 0
            agent_types[agent_type] += 1

        print(f"\n✅ Agent types found:")
        for agent_type, count in agent_types.items():
            print(f"   - {agent_type}: {count}")

        # Verify we have the main agent types
        expected_types = ['BoundaryProberAgent', 'ExploiterAgent', 'MutatorAgent', 'ValidatorAgent']
        for expected in expected_types:
            self.assertIn(expected, agent_types, f"Missing {expected}")

    def test_orchestrator_initialization(self):
        """Test that orchestrator is initialized"""
        scenario = PromptInjectionScenario()

        ecosystem = UnifiedEcosystem(
            scenario=scenario,
            use_llm=False,
            llm_clients=None,
            config={}
        )

        self.assertIsNotNone(ecosystem.orchestrator)
        self.assertEqual(len(ecosystem.orchestrator.agents), len(ecosystem.agents))

        print(f"\n✅ Orchestrator initialized with {len(ecosystem.orchestrator.agents)} agents")

    def test_knowledge_base(self):
        """Test that knowledge base is initialized"""
        scenario = PromptInjectionScenario()

        ecosystem = UnifiedEcosystem(
            scenario=scenario,
            use_llm=False,
            llm_clients=None,
            config={}
        )

        self.assertIsNotNone(ecosystem.knowledge_base)

        # Test knowledge base query (basic check)
        entries = ecosystem.knowledge_base.query()
        self.assertIsNotNone(entries)

        print(f"\n✅ Knowledge base initialized")


def run_basic_tests():
    """Run basic agent tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestAgentsBasic))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_basic_tests()
    sys.exit(0 if success else 1)
