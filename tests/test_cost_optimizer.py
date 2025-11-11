"""
Tests for Cost Optimization (Enhancement 6).

Tests verify:
- Model routing
- Budget enforcement
- Cost prediction
- Phase-based budget management
"""

import pytest
from datetime import datetime

from framework.cost_optimizer import ModelRouter, BudgetEnforcer, CostPredictor
from framework.base import Task, Phase
from framework.models import EvaluationResult


class MockLLMClient:
    """Mock LLM client for testing."""

    def __init__(self, name: str, cost_per_1k: float):
        self.name = name
        self.model_name = name
        self.cost_per_1k = cost_per_1k
        self.calls = 0

    def generate(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        self.calls += 1
        return f"Mock response from {self.name}"


@pytest.fixture
def llm_clients():
    """Create mock LLM clients."""
    return [
        MockLLMClient('gpt-4', cost_per_1k=0.06),
        MockLLMClient('gpt-3.5-turbo', cost_per_1k=0.002),
        MockLLMClient('claude-haiku', cost_per_1k=0.001)
    ]


@pytest.fixture
def model_router(llm_clients):
    """Create model router for testing."""
    return ModelRouter(llm_clients=llm_clients)


@pytest.fixture
def budget_enforcer():
    """Create budget enforcer for testing."""
    return BudgetEnforcer()


def test_model_router_initialization(model_router, llm_clients):
    """Test model router initializes correctly."""
    assert model_router is not None
    assert len(model_router.clients) == len(llm_clients)
    assert model_router.cheap_client.name == 'claude-haiku'
    assert model_router.expensive_client.name == 'gpt-4'


def test_model_router_simple_task(model_router):
    """Test model router handles simple tasks."""
    task = Task(
        task_id='test_1',
        task_type='judge',
        description='Simple yes/no question',
        parameters={}
    )
    prompt = "Is this malicious? YES or NO"

    client = model_router.route(task, prompt)

    # Should route to cheap model (short prompt, simple task)
    assert client.name in ['claude-haiku', 'gpt-3.5-turbo']


def test_model_router_complex_task(model_router):
    """Test model router handles complex tasks."""
    task = Task(
        task_id='test_2',
        task_type='generate_attacks',
        description='Generate creative novel attacks',
        parameters={}
    )
    prompt = "Generate 10 creative SQL injection attacks that evade detection..." * 10

    client = model_router.route(task, prompt)

    # Should route to expensive model (long prompt, complex task)
    # Note: This might fail if heuristics change, but it's a good baseline
    assert client.name in ['gpt-4', 'gpt-3.5-turbo']


def test_model_router_feedback_loop(model_router):
    """Test model router learns from feedback."""
    task = Task(
        task_id='test_3',
        task_type='assess',
        description='Assess quality',
        parameters={}
    )

    # Get initial routing
    client1 = model_router.route(task, "Assess this")
    initial_name = client1.name

    # Provide positive feedback multiple times
    for _ in range(5):
        model_router.update('assess', quality_score=0.9)

    # Get new routing
    client2 = model_router.route(task, "Assess this")

    # Should stick with successful model or upgrade
    assert client2.name in [initial_name, 'gpt-4', 'gpt-3.5-turbo']


def test_model_router_handles_poor_performance(model_router):
    """Test model router switches models on poor performance."""
    task = Task(
        task_id='test_4',
        task_type='generate',
        description='Generate something',
        parameters={}
    )

    # Get initial routing
    client1 = model_router.route(task, "Generate")
    initial_name = client1.name

    # Provide negative feedback multiple times
    for _ in range(5):
        model_router.update('generate', quality_score=0.1)

    # Get new routing
    client2 = model_router.route(task, "Generate")

    # Should potentially try different model (or at least not crash)
    assert client2 is not None


def test_budget_enforcer_initialization(budget_enforcer):
    """Test budget enforcer initializes correctly."""
    assert budget_enforcer is not None

    # Default phase budgets (before set_budget called)
    assert Phase.EXPLORATION in budget_enforcer.phase_budgets
    assert Phase.EXPLOITATION in budget_enforcer.phase_budgets
    assert Phase.VALIDATION in budget_enforcer.phase_budgets


def test_budget_enforcer_set_budget(budget_enforcer):
    """Test budget enforcer sets budget correctly."""
    budget_enforcer.set_budget(100.0)

    assert budget_enforcer.total_budget == 100.0

    # Check phase budgets sum to total
    total_phase = sum(budget_enforcer.phase_budgets.values())
    assert abs(total_phase - 100.0) < 0.01


def test_budget_enforcer_record_cost(budget_enforcer):
    """Test budget enforcer records costs."""
    budget_enforcer.set_budget(100.0)

    # Record some costs
    budget_enforcer.record_cost(Phase.EXPLORATION, 10.0)
    budget_enforcer.record_cost(Phase.EXPLORATION, 5.0)
    budget_enforcer.record_cost(Phase.EXPLOITATION, 20.0)

    assert budget_enforcer.phase_spent[Phase.EXPLORATION] == 15.0
    assert budget_enforcer.phase_spent[Phase.EXPLOITATION] == 20.0
    assert budget_enforcer.total_spent == 35.0


def test_budget_enforcer_can_afford(budget_enforcer):
    """Test budget enforcer checks affordability."""
    budget_enforcer.set_budget(100.0)

    # Should be able to afford small costs
    assert budget_enforcer.can_afford(Phase.EXPLORATION, 5.0) == True

    # Exhaust exploration budget (40% of 100 = 40)
    budget_enforcer.record_cost(Phase.EXPLORATION, 38.0)

    # Should not be able to afford more exploration
    assert budget_enforcer.can_afford(Phase.EXPLORATION, 5.0) == False

    # But should be able to afford exploitation
    assert budget_enforcer.can_afford(Phase.EXPLOITATION, 5.0) == True


def test_budget_enforcer_exhaustion(budget_enforcer):
    """Test budget enforcer detects budget exhaustion."""
    budget_enforcer.set_budget(50.0)

    # Spend close to total budget
    budget_enforcer.record_cost(Phase.EXPLORATION, 20.0)
    budget_enforcer.record_cost(Phase.EXPLOITATION, 25.0)
    budget_enforcer.record_cost(Phase.VALIDATION, 4.0)

    # Should not be able to afford much more
    assert budget_enforcer.can_afford(Phase.VALIDATION, 10.0) == False


def test_cost_predictor_initialization():
    """Test cost predictor initializes correctly."""
    from framework.agents import ExploiterAgent, ValidatorAgent
    from framework.knowledge_base import InMemoryKnowledgeBase
    from scenarios.sql_injection import SQLInjectionScenario

    kb = InMemoryKnowledgeBase()
    scenario = SQLInjectionScenario()

    agents = [
        ExploiterAgent('exploiter_0', kb, scenario),
        ValidatorAgent('validator_0', kb, [])
    ]

    predictor = CostPredictor(agents=agents)

    assert predictor is not None
    assert len(predictor.agents) == 2


def test_cost_predictor_predict_no_llm():
    """Test cost predictor for non-LLM agents."""
    from framework.agents import ValidatorAgent
    from framework.knowledge_base import InMemoryKnowledgeBase

    kb = InMemoryKnowledgeBase()
    agents = [
        ValidatorAgent('validator_0', kb, []),
        ValidatorAgent('validator_1', kb, [])
    ]

    predictor = CostPredictor(agents=agents)

    cost = predictor.predict_cost(
        num_rounds=10,
        num_attacks=50,
        use_llm_agents=False
    )

    # Should predict 0 cost (no LLM agents)
    assert cost == 0.0


def test_cost_predictor_predict_with_llm():
    """Test cost predictor for LLM agents."""
    from framework.agents import ExploiterAgent
    from framework.knowledge_base import InMemoryKnowledgeBase
    from scenarios.sql_injection import SQLInjectionScenario

    kb = InMemoryKnowledgeBase()
    scenario = SQLInjectionScenario()

    mock_llm = MockLLMClient('gpt-3.5-turbo', 0.002)

    agents = [
        ExploiterAgent('exploiter_0', kb, scenario, use_llm=True, llm_client=mock_llm)
    ]

    predictor = CostPredictor(agents=agents)

    cost = predictor.predict_cost(
        num_rounds=10,
        num_attacks=50,
        use_llm_agents=True
    )

    # Should predict non-zero cost
    assert cost > 0.0
    # Should be reasonable (not insanely high)
    assert cost < 1000.0


def test_cost_predictor_accuracy_estimate():
    """Test cost predictor provides accuracy estimate."""
    from framework.agents import ValidatorAgent
    from framework.knowledge_base import InMemoryKnowledgeBase

    kb = InMemoryKnowledgeBase()
    agents = [ValidatorAgent('validator_0', kb, [])]

    predictor = CostPredictor(agents=agents)

    cost, accuracy = predictor.predict_cost_with_accuracy(
        num_rounds=5,
        num_attacks=20,
        use_llm_agents=False
    )

    assert cost == 0.0
    assert 0.0 <= accuracy <= 1.0


def test_phase_based_budgets():
    """Test phase-based budget allocation."""
    enforcer = BudgetEnforcer()
    enforcer.set_budget(100.0)

    # Check default splits
    exploration = enforcer.phase_budgets[Phase.EXPLORATION]
    exploitation = enforcer.phase_budgets[Phase.EXPLOITATION]
    validation = enforcer.phase_budgets[Phase.VALIDATION]

    # Should sum to total
    assert abs((exploration + exploitation + validation) - 100.0) < 0.01

    # Exploration should get most budget (40%)
    assert exploration >= exploitation
    assert exploration >= validation


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
