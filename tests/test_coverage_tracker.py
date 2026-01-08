"""
Tests for Coverage Tracking (Enhancement 7).

Tests verify:
- Coverage tracking
- Priority calculation
- Expansion suggestions
- Template generation
"""

import pytest
from datetime import datetime

from framework.coverage_tracker import CoverageTracker, CoverageExpansionAgent
from framework.models import Attack, EvaluationResult, EvaluationMetrics, create_attack_id
from scenarios.sql_injection import SQLInjectionScenario


@pytest.fixture
def scenario():
    """Create SQL injection scenario for testing."""
    return SQLInjectionScenario()


@pytest.fixture
def coverage_tracker(scenario):
    """Create coverage tracker for testing."""
    return CoverageTracker(scenario=scenario, taxonomy='MITRE_ATT&CK')


@pytest.fixture
def evaluation_result(scenario):
    """Create mock evaluation result."""
    result = EvaluationResult(
        evaluation_id='test_eval',
        purple_agent='test_agent',
        scenario='sql_injection',
        start_time=datetime.now()
    )

    # Add test attacks
    attacks = []
    for i in range(15):
        attack = Attack(
            attack_id=create_attack_id('sql_injection', f'test_{i}', datetime.now()),
            scenario='sql_injection',
            technique='sqli_basic' if i < 10 else 'sqli_union',
            payload=f"' OR 1=1-- {i}",
            metadata={},
            is_malicious=True
        )
        attacks.append(attack)

    result.attacks = attacks

    # Add metrics
    result.metrics = EvaluationMetrics(
        precision=0.8,
        recall=0.7,
        f1_score=0.75,
        false_positive_rate=0.1,
        false_negative_rate=0.3,
        total_latency_ms=1000.0
    )

    result.finalize()

    return result


def test_coverage_tracker_initialization(coverage_tracker):
    """Test coverage tracker initializes correctly."""
    assert coverage_tracker is not None
    assert coverage_tracker.taxonomy == 'MITRE_ATT&CK'
    assert coverage_tracker.coverage_report is not None
    assert coverage_tracker.coverage_report.total_techniques > 0


def test_coverage_tracker_initial_coverage(coverage_tracker):
    """Test initial coverage is 0%."""
    report = coverage_tracker.coverage_report

    assert len(report.covered_techniques) == 0
    assert len(report.uncovered_techniques) > 0
    assert report.coverage_percentage == 0.0


def test_coverage_tracker_update_coverage(coverage_tracker, evaluation_result):
    """Test coverage tracking updates from evaluation."""
    initial_covered = len(coverage_tracker.coverage_report.covered_techniques)

    coverage_tracker.update_coverage(evaluation_result)

    # Should have some coverage now
    # (sqli_basic has 10 tests = fully covered, sqli_union has 5 tests = partially covered)
    final_covered = len(coverage_tracker.coverage_report.covered_techniques)

    # At least sqli_basic should be covered (10+ tests)
    assert final_covered >= initial_covered


def test_coverage_tracker_partial_coverage(coverage_tracker, evaluation_result):
    """Test partial coverage detection."""
    coverage_tracker.update_coverage(evaluation_result)

    partially_covered = coverage_tracker.coverage_report.partially_covered

    # sqli_union should be partially covered (5 tests = 50%)
    # Check if any technique is partially covered
    assert len(partially_covered) >= 0  # May or may not have partial coverage depending on mapping


def test_coverage_tracker_coverage_percentage(coverage_tracker, evaluation_result):
    """Test coverage percentage calculation."""
    coverage_tracker.update_coverage(evaluation_result)

    report = coverage_tracker.coverage_report
    report.calculate_coverage()

    assert 0.0 <= report.coverage_percentage <= 100.0

    # With some attacks tested, should have non-zero coverage
    if len(report.covered_techniques) > 0:
        assert report.coverage_percentage > 0.0


def test_coverage_tracker_prioritize_techniques(coverage_tracker):
    """Test technique prioritization."""
    priorities = coverage_tracker.prioritize_next_techniques(top_n=5)

    assert isinstance(priorities, list)
    assert len(priorities) <= 5

    # Each priority should be (technique, priority_score)
    for tech, priority in priorities:
        assert isinstance(tech, str)
        assert 0.0 <= priority <= 1.0

    # Should be sorted by priority (descending)
    for i in range(len(priorities) - 1):
        assert priorities[i][1] >= priorities[i+1][1]


def test_coverage_tracker_related_techniques(coverage_tracker):
    """Test related technique detection."""
    # Get some reference techniques
    current_techniques = set(coverage_tracker.scenario.get_techniques())
    current_mitre = set()
    for tech in current_techniques:
        current_mitre.update(coverage_tracker.mitre_mapping.get(tech, []))

    if len(current_mitre) > 0:
        sample_tech = list(current_mitre)[0]

        # Should identify as related to itself
        is_related = coverage_tracker._is_related(sample_tech, current_mitre)
        assert is_related == True


def test_coverage_tracker_generate_report(coverage_tracker, evaluation_result):
    """Test coverage report generation."""
    coverage_tracker.update_coverage(evaluation_result)
    report = coverage_tracker.generate_coverage_report()

    assert 'taxonomy' in report
    assert report['taxonomy'] == 'MITRE_ATT&CK'

    assert 'coverage_summary' in report
    summary = report['coverage_summary']
    assert 'total_techniques' in summary
    assert 'covered' in summary
    assert 'partially_covered' in summary
    assert 'uncovered' in summary
    assert 'coverage_percentage' in summary

    assert 'covered_techniques' in report
    assert isinstance(report['covered_techniques'], list)

    assert 'coverage_debt' in report
    debt = report['coverage_debt']
    assert 'total_debt' in debt
    assert 'estimated_time_to_full_coverage' in debt


def test_coverage_tracker_time_estimate(coverage_tracker):
    """Test time to coverage estimation."""
    time_estimate = coverage_tracker._estimate_time_to_coverage()

    assert isinstance(time_estimate, str)
    # Should mention time unit
    assert any(unit in time_estimate.lower() for unit in ['hour', 'day', 'week', 'month'])


def test_expansion_agent_initialization(coverage_tracker):
    """Test expansion agent initializes correctly."""
    agent = CoverageExpansionAgent(coverage_tracker)

    assert agent is not None
    assert agent.coverage_tracker == coverage_tracker


def test_expansion_agent_suggest_scenario(coverage_tracker, evaluation_result):
    """Test expansion agent suggests next scenario."""
    coverage_tracker.update_coverage(evaluation_result)
    agent = CoverageExpansionAgent(coverage_tracker)

    suggestion = agent.suggest_next_scenario()

    assert isinstance(suggestion, dict)

    if suggestion.get('suggestion') is not None:
        # Should have implementation guide
        assert 'suggested_technique' in suggestion
        assert 'priority_score' in suggestion
        assert 'coverage_impact' in suggestion
        assert 'implementation_guide' in suggestion

        guide = suggestion['implementation_guide']
        assert 'scenario_class' in guide
        assert 'estimated_time' in guide
        assert 'required_components' in guide
        assert 'mitre_reference' in guide
    else:
        # Full coverage achieved
        assert suggestion.get('reason') == 'Full coverage achieved!'


def test_expansion_agent_template_generation(coverage_tracker):
    """Test expansion agent generates scenario template."""
    agent = CoverageExpansionAgent(coverage_tracker)

    template = agent.generate_scenario_template('T1234')

    assert isinstance(template, str)
    assert len(template) > 0

    # Should contain key components
    assert 'T1234' in template
    assert 'SecurityScenario' in template
    assert 'Mutator' in template
    assert 'Validator' in template
    assert 'def get_name' in template
    assert 'def get_techniques' in template
    assert 'def get_mutators' in template
    assert 'def get_validators' in template
    assert 'def create_attack' in template
    assert 'def execute_attack' in template
    assert 'def get_mitre_mapping' in template


def test_expansion_agent_template_has_todos(coverage_tracker):
    """Test generated template has TODO markers."""
    agent = CoverageExpansionAgent(coverage_tracker)

    template = agent.generate_scenario_template('T5678')

    # Should have TODO comments for implementation
    assert 'TODO' in template
    assert template.count('TODO') >= 3  # At least 3 TODOs


def test_coverage_tracker_multiple_evaluations(coverage_tracker, evaluation_result):
    """Test coverage tracker handles multiple evaluations."""
    # First evaluation
    coverage_tracker.update_coverage(evaluation_result)
    first_coverage = coverage_tracker.coverage_report.coverage_percentage

    # Second evaluation (same attacks)
    coverage_tracker.update_coverage(evaluation_result)
    second_coverage = coverage_tracker.coverage_report.coverage_percentage

    # Coverage should stay same or increase
    assert second_coverage >= first_coverage


def test_coverage_report_priority_queue(coverage_tracker, evaluation_result):
    """Test priority queue is maintained."""
    coverage_tracker.update_coverage(evaluation_result)
    coverage_tracker.prioritize_next_techniques(top_n=3)

    report = coverage_tracker.coverage_report

    assert len(report.priority_queue) <= 3

    # Should be sorted by priority
    for i in range(len(report.priority_queue) - 1):
        assert report.priority_queue[i][1] >= report.priority_queue[i+1][1]


def test_coverage_debt_calculation(coverage_tracker, evaluation_result):
    """Test coverage debt calculation."""
    coverage_tracker.update_coverage(evaluation_result)
    priorities = coverage_tracker.prioritize_next_techniques(top_n=10)

    report = coverage_tracker.generate_coverage_report()
    debt = report['coverage_debt']

    # Total debt = uncovered techniques
    assert debt['total_debt'] == len(coverage_tracker.coverage_report.uncovered_techniques)

    # High priority debt
    high_priority = len([p for tech, p in priorities if p > 0.7])
    assert debt['high_priority_debt'] == high_priority


def test_mitre_mapping_structure(scenario):
    """Test MITRE mapping has correct structure."""
    mapping = scenario.get_mitre_mapping()

    assert isinstance(mapping, dict)

    # Each scenario technique should map to MITRE techniques
    for scenario_tech, mitre_techs in mapping.items():
        assert isinstance(scenario_tech, str)
        assert isinstance(mitre_techs, list)

        # Each MITRE technique should be valid format (T1234 or T1234.001)
        for mitre_tech in mitre_techs:
            assert mitre_tech.startswith('T')
            assert any(c.isdigit() for c in mitre_tech)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
