#!/usr/bin/env python3
"""
Test MITRE integration with the existing framework.

This script tests the BoundaryProber and Exploiter agents with MITRE components.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from framework.knowledge_base import InMemoryKnowledgeBase
from framework.scenarios import PromptInjectionScenario
from framework.agents import BoundaryProberAgent, ExploiterAgent
from framework.base import Task

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class MockPurpleAgent:
    """Mock purple agent for testing."""
    
    def __init__(self, name='test_automation_agent'):
        self.name = name
    
    def get_name(self):
        return self.name


def test_mitre_integration():
    """Test MITRE integration end-to-end."""
    
    logger.info("=" * 70)
    logger.info("Testing MITRE Integration")
    logger.info("=" * 70)
    
    # 1. Setup
    logger.info("\n1. Initializing components...")
    kb = InMemoryKnowledgeBase()
    scenario = PromptInjectionScenario()
    purple_agent = MockPurpleAgent('home_automation_agent')
    
    # 2. Create BoundaryProber
    logger.info("\n2. Creating BoundaryProber agent...")
    boundary_prober = BoundaryProberAgent(
        agent_id='test_boundary_prober',
        knowledge_base=kb,
        scenario=scenario
    )
    
    # Check if MITRE components are available
    if boundary_prober.profiler is None:
        logger.warning("MITRE components not available in BoundaryProber")
        logger.warning("This is expected if imports failed")
    else:
        logger.info("✅ BoundaryProber has MITRE components")
    
    # 3. Create Exploiter
    logger.info("\n3. Creating Exploiter agent...")
    exploiter = ExploiterAgent(
        agent_id='test_exploiter',
        knowledge_base=kb,
        scenario=scenario,
        use_llm=False  # Test without LLM
    )
    
    if exploiter.payload_generator is None:
        logger.warning("MITRE PayloadGenerator not available in Exploiter")
        logger.warning("This is expected if imports failed")
    else:
        logger.info("✅ Exploiter has MITRE PayloadGenerator")
    
    # 4. Test BoundaryProber profiling
    logger.info("\n4. Testing BoundaryProber profiling...")
    if boundary_prober.profiler:
        try:
            # Trigger profiling by executing a task
            task = Task(
                task_id='test_probe',
                task_type='probe_boundaries',
                description='Test probe',
                parameters={
                    'purple_agent': purple_agent,
                    'technique': 'jailbreak',
                    'num_probes': 5
                }
            )
            
            result = boundary_prober.execute_task(task)
            logger.info(f"Probing result: {result}")
            
            # Check if profile was created
            if boundary_prober.agent_profile:
                logger.info(f"✅ Agent profiled: type={boundary_prober.agent_profile.agent_type}, "
                          f"platforms={boundary_prober.agent_profile.platforms}")
            
            # Check if TTPs were selected
            if boundary_prober.selected_ttps:
                logger.info(f"✅ Selected {len(boundary_prober.selected_ttps)} MITRE TTPs")
                for i, ttp in enumerate(boundary_prober.selected_ttps[:3]):
                    logger.info(f"   - {ttp.technique_id}: {ttp.name} (tactics: {ttp.tactics})")
                if len(boundary_prober.selected_ttps) > 3:
                    logger.info(f"   ... and {len(boundary_prober.selected_ttps) - 3} more")
            
        except Exception as e:
            logger.error(f"Profiling failed: {e}", exc_info=True)
    else:
        logger.info("Skipping profiling test (MITRE not available)")
    
    # 5. Test Exploiter with MITRE
    logger.info("\n5. Testing Exploiter with MITRE payloads...")
    if exploiter.payload_generator:
        try:
            # Load TTPs from knowledge base
            exploiter._load_ttps_from_knowledge_base()
            
            if exploiter.selected_ttps:
                logger.info(f"✅ Exploiter loaded {len(exploiter.selected_ttps)} TTPs from KB")
            else:
                logger.warning("No TTPs loaded from knowledge base")
            
            # Generate attacks
            task = Task(
                task_id='test_exploit',
                task_type='generate_attacks',
                description='Test attack generation',
                parameters={
                    'technique': 'jailbreak',
                    'num_attacks': 10
                }
            )
            
            result = exploiter.execute_task(task)
            attacks = result.get('attacks', [])
            
            logger.info(f"✅ Generated {len(attacks)} attacks")
            
            # Show statistics
            stats = exploiter.get_generation_stats()
            logger.info(f"Generation sources: {stats['sources']}")
            
            # Show sample attacks
            if attacks:
                logger.info("\nSample attacks generated:")
                for i, attack in enumerate(attacks[:3]):
                    logger.info(f"  Attack {i+1}:")
                    logger.info(f"    Payload: {attack.payload[:100]}...")
                    logger.info(f"    Technique: {attack.technique}")
                    logger.info(f"    Generation: {attack.metadata.get('generation_source', 'unknown')}")
                    if 'mitre_technique_id' in attack.metadata:
                        logger.info(f"    MITRE ID: {attack.metadata['mitre_technique_id']}")
                        logger.info(f"    MITRE Name: {attack.metadata['mitre_technique_name']}")
                        logger.info(f"    Severity: {attack.metadata.get('severity', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Attack generation failed: {e}", exc_info=True)
    else:
        logger.info("Skipping MITRE payload generation test (not available)")
    
    # 6. Test fallback behavior
    logger.info("\n6. Testing fallback behavior (without MITRE)...")
    try:
        # Create exploiter without MITRE
        exploiter_fallback = ExploiterAgent(
            agent_id='test_exploiter_fallback',
            knowledge_base=InMemoryKnowledgeBase(),  # Fresh KB with no TTPs
            scenario=scenario,
            use_llm=False
        )
        
        task = Task(
            task_id='test_fallback',
            task_type='generate_attacks',
            description='Test fallback',
            parameters={
                'technique': 'jailbreak',
                'num_attacks': 5
            }
        )
        
        result = exploiter_fallback.execute_task(task)
        attacks = result.get('attacks', [])
        
        logger.info(f"✅ Fallback generation produced {len(attacks)} attacks")
        
        stats = exploiter_fallback.get_generation_stats()
        logger.info(f"Fallback sources: {stats['sources']}")
        
    except Exception as e:
        logger.error(f"Fallback test failed: {e}", exc_info=True)
    
    # 7. Summary
    logger.info("\n" + "=" * 70)
    logger.info("MITRE Integration Test Summary")
    logger.info("=" * 70)
    
    mitre_available = boundary_prober.profiler is not None
    logger.info(f"MITRE Components Available: {mitre_available}")
    
    if mitre_available:
        logger.info(f"Agent Profiled: {boundary_prober.agent_profile is not None}")
        logger.info(f"TTPs Selected: {len(boundary_prober.selected_ttps)} techniques")
        logger.info(f"Payloads Generated: {exploiter.attacks_generated} attacks")
        logger.info(f"Generation Sources: {exploiter.generation_sources}")
    else:
        logger.info("MITRE integration gracefully degraded to fallback methods")
    
    logger.info("\n✅ Integration test completed!")
    logger.info("=" * 70)


if __name__ == '__main__':
    test_mitre_integration()
