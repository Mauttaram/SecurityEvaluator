#!/usr/bin/env python3
"""
Direct test of ComprehensiveSecurityScenario to verify MITRE integration.

This test bypasses the AgentBeats framework and directly tests the scenario
to ensure MITRE techniques are being selected and payloads generated correctly.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from framework.scenarios import ComprehensiveSecurityScenario
from framework.models import Attack
import json


def test_comprehensive_scenario():
    """Test ComprehensiveSecurityScenario directly."""
    
    print("=" * 80)
    print("COMPREHENSIVE SECURITY SCENARIO - DIRECT TEST")
    print("=" * 80)
    print()
    
    # Create scenario with configuration
    config = {
        'mitre': {
            'enabled': True,
            'ttp_selection': {
                'max_techniques': 25,
                'include_atlas': True,
                'include_attack': True,
                'atlas_weight': 0.7,
                'attack_weight': 0.3
            },
            'agent_profile': {
                'mark_as_ai_agent': True,
                'agent_type': 'ai-automation'
            },
            'payload_generation': {
                'payloads_per_technique': 2,
                'include_benign_controls': True,
                'benign_count': 5
            }
        }
    }
    
    print("1️⃣  Creating ComprehensiveSecurityScenario...")
    scenario = ComprehensiveSecurityScenario(config=config)
    print(f"   ✅ Scenario name: {scenario.get_name()}")
    print()
    
    # Set agent profile (simulating what the framework would do)
    print("2️⃣  Setting agent profile...")
    agent_card = {
        'name': 'home_automation_agent',
        'type': 'ai-automation',
        'description': 'Smart home automation agent with IoT control',
        'capabilities': ['home_automation', 'iot_control', 'voice_commands']
    }
    scenario.set_agent_profile(agent_card)
    print("   ✅ Agent profile set")
    print()
    
    # Get attack templates (this should trigger MITRE TTP selection)
    print("3️⃣  Generating attack templates from MITRE knowledge base...")
    attacks = scenario.get_attack_templates()
    print(f"   ✅ Generated {len(attacks)} attack templates")
    print()
    
    # Analyze attacks
    print("4️⃣  Analyzing generated attacks...")
    atlas_attacks = []
    attack_attacks = []
    benign_attacks = []
    other_attacks = []
    
    for attack in attacks:
        tech_id = attack.metadata.get('mitre_technique_id', 'N/A')
        
        if tech_id.startswith('AML.'):
            atlas_attacks.append(attack)
        elif tech_id.startswith('T'):
            attack_attacks.append(attack)
        elif tech_id.startswith('BENIGN'):
            benign_attacks.append(attack)
        else:
            other_attacks.append(attack)
    
    print(f"   📊 Attack Distribution:")
    print(f"      🎯 ATLAS (AI/ML): {len(atlas_attacks)}")
    print(f"      🔴 ATT&CK: {len(attack_attacks)}")
    print(f"      ✅ Benign Controls: {len(benign_attacks)}")
    print(f"      ⚪ Other: {len(other_attacks)}")
    print()
    
    # Show sample ATLAS attacks
    if atlas_attacks:
        print("5️⃣  Sample ATLAS Attacks:")
        for i, attack in enumerate(atlas_attacks[:5], 1):
            tech_id = attack.metadata.get('mitre_technique_id', 'N/A')
            tech_name = attack.metadata.get('mitre_technique_name', 'N/A')
            category = attack.metadata.get('category', 'N/A')
            payload_preview = str(attack.payload)[:100]
            
            print(f"   Attack #{i}:")
            print(f"      ID: {tech_id}")
            print(f"      Name: {tech_name}")
            print(f"      Category: {category}")
            print(f"      Payload: {payload_preview}...")
            print(f"      Malicious: {attack.is_malicious}")
            print(f"      Severity: {attack.severity}")
            print()
    
    # Show sample ATT&CK attacks
    if attack_attacks:
        print("6️⃣  Sample ATT&CK Attacks:")
        for i, attack in enumerate(attack_attacks[:3], 1):
            tech_id = attack.metadata.get('mitre_technique_id', 'N/A')
            tech_name = attack.metadata.get('mitre_technique_name', 'N/A')
            category = attack.metadata.get('category', 'N/A')
            payload_preview = str(attack.payload)[:100]
            
            print(f"   Attack #{i}:")
            print(f"      ID: {tech_id}")
            print(f"      Name: {tech_name}")
            print(f"      Category: {category}")
            print(f"      Payload: {payload_preview}...")
            print()
    
    # Get MITRE coverage report
    print("7️⃣  MITRE Coverage Report:")
    coverage = scenario.get_coverage_report()
    print(f"   Total Techniques: {coverage['total_techniques']}")
    print(f"   ATLAS Techniques: {coverage['atlas_techniques']}")
    print(f"   ATT&CK Techniques: {coverage['attack_techniques']}")
    print(f"   Coverage: {coverage['coverage_percentage']:.2f}%")
    print()
    
    # Show technique details
    if coverage['techniques']:
        print("8️⃣  Selected MITRE Techniques:")
        for tech in coverage['techniques'][:10]:
            print(f"      {tech['id']} ({tech['source'].upper()}): {tech['name']}")
        if len(coverage['techniques']) > 10:
            print(f"      ... and {len(coverage['techniques']) - 10} more")
        print()
    
    # Validation
    print("=" * 80)
    print("VALIDATION")
    print("=" * 80)
    
    success = True
    
    if len(attacks) < 10:
        print("❌ FAILED: Too few attacks generated (expected >= 10)")
        success = False
    else:
        print(f"✅ PASSED: Sufficient attacks generated ({len(attacks)})")
    
    if len(atlas_attacks) == 0:
        print("❌ FAILED: No ATLAS techniques used")
        success = False
    else:
        print(f"✅ PASSED: ATLAS techniques present ({len(atlas_attacks)})")
    
    if coverage['total_techniques'] == 0:
        print("❌ FAILED: No MITRE techniques selected")
        success = False
    else:
        print(f"✅ PASSED: MITRE techniques selected ({coverage['total_techniques']})")
    
    # Export sample to JSON for inspection
    sample_data = {
        'summary': {
            'total_attacks': len(attacks),
            'atlas_count': len(atlas_attacks),
            'attack_count': len(attack_attacks),
            'benign_count': len(benign_attacks),
            'coverage': coverage
        },
        'sample_attacks': []
    }
    
    for attack in (atlas_attacks[:3] + attack_attacks[:3] + benign_attacks[:2]):
        sample_data['sample_attacks'].append({
            'attack_id': attack.attack_id,
            'technique': attack.technique,
            'payload': str(attack.payload),
            'is_malicious': attack.is_malicious,
            'severity': str(attack.severity),
            'metadata': attack.metadata
        })
    
    output_file = Path('reports/comprehensive_scenario_test.json')
    output_file.parent.mkdir(exist_ok=True)
    output_file.write_text(json.dumps(sample_data, indent=2))
    print(f"\n📄 Sample data exported to: {output_file}")
    
    print()
    if success:
        print("=" * 80)
        print("✅ ALL TESTS PASSED")
        print("=" * 80)
        return 0
    else:
        print("=" * 80)
        print("❌ SOME TESTS FAILED")
        print("=" * 80)
        return 1


if __name__ == '__main__':
    sys.exit(test_comprehensive_scenario())
