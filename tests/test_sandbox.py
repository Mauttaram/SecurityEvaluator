"""
Tests for Formal Sandbox (Enhancement 5).

Tests verify:
- Container isolation
- Security profile enforcement
- Resource limits
- Error handling
"""

import pytest
from datetime import datetime

from framework.sandbox import FormalSandbox, SandboxedPurpleAgent, SECCOMP_PROFILE
from framework.models import Attack, create_attack_id


@pytest.fixture
def sandbox():
    """Create sandbox instance for testing."""
    try:
        sandbox = FormalSandbox(
            image='python:3.10-slim',
            cpu_limit=0.5,
            memory_limit='512m',
            timeout_seconds=10,
            enable_network=False
        )
        return sandbox
    except Exception as e:
        pytest.skip(f"Docker not available: {e}")


@pytest.fixture
def simple_attack():
    """Create simple test attack."""
    return Attack(
        attack_id=create_attack_id('test', 'simple', datetime.now()),
        scenario='test',
        technique='simple_test',
        payload="' OR 1=1--",
        metadata={'test': True},
        is_malicious=True
    )


def test_sandbox_initialization(sandbox):
    """Test sandbox initializes correctly."""
    assert sandbox is not None
    assert sandbox.image == 'python:3.10-slim'
    assert sandbox.cpu_limit == 0.5
    assert sandbox.memory_limit == '512m'
    assert sandbox.timeout_seconds == 10
    assert sandbox.enable_network == False


def test_sandbox_execute_attack(sandbox, simple_attack):
    """Test sandbox can execute attacks."""
    # Simple detection function
    purple_agent_code = """
def detect(payload):
    dangerous_patterns = ["'", '"', 'OR', 'UNION', 'SELECT']
    detected = any(p.upper() in str(payload).upper() for p in dangerous_patterns)
    return {
        'is_vulnerable': detected,
        'confidence': 0.8 if detected else 0.2,
        'explanation': 'Pattern matching'
    }
"""

    result = sandbox.execute_attack(
        attack=simple_attack,
        purple_agent_code=purple_agent_code
    )

    assert result is not None
    assert result.attack_id == simple_attack.attack_id
    assert isinstance(result.detected, bool)
    assert 0.0 <= result.confidence <= 1.0


def test_sandbox_network_isolation(sandbox, simple_attack):
    """Test sandbox blocks network access."""
    # Code that tries to make network connection
    purple_agent_code = """
import socket

def detect(payload):
    try:
        # Try to connect to google.com (should fail)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('8.8.8.8', 53))
        sock.close()
        return {'is_vulnerable': True, 'confidence': 1.0, 'explanation': 'Network accessible!'}
    except Exception as e:
        # Network blocked (expected)
        return {'is_vulnerable': False, 'confidence': 0.5, 'explanation': f'Network blocked: {e}'}
"""

    result = sandbox.execute_attack(
        attack=simple_attack,
        purple_agent_code=purple_agent_code
    )

    # Should succeed but network should be blocked
    assert result is not None
    # Detection reason should mention network being blocked
    assert 'blocked' in result.detection_reason.lower() or 'error' in result.detection_reason.lower()


def test_sandbox_timeout(sandbox, simple_attack):
    """Test sandbox enforces timeout."""
    # Code that takes too long
    purple_agent_code = """
import time

def detect(payload):
    time.sleep(100)  # Longer than timeout
    return {'is_vulnerable': False, 'confidence': 0.5, 'explanation': 'Should not reach here'}
"""

    # Should timeout (sandbox timeout is 10s)
    result = sandbox.execute_attack(
        attack=simple_attack,
        purple_agent_code=purple_agent_code
    )

    # Should return error result
    assert result is not None
    # Conservative: assume evasion on timeout
    assert result.outcome.name == 'FALSE_NEGATIVE'


def test_sandbox_resource_limits(sandbox, simple_attack):
    """Test sandbox enforces resource limits."""
    # Code that tries to allocate too much memory
    purple_agent_code = """
def detect(payload):
    try:
        # Try to allocate 1GB (more than limit)
        large_list = [0] * (10**9)
        return {'is_vulnerable': True, 'confidence': 1.0, 'explanation': 'Should not reach here'}
    except MemoryError:
        return {'is_vulnerable': False, 'confidence': 0.5, 'explanation': 'Memory limit enforced'}
    except Exception as e:
        return {'is_vulnerable': False, 'confidence': 0.5, 'explanation': f'Error: {e}'}
"""

    result = sandbox.execute_attack(
        attack=simple_attack,
        purple_agent_code=purple_agent_code
    )

    assert result is not None
    # Should either get MemoryError or container kill
    assert result.detected == False


def test_seccomp_profile_structure():
    """Test seccomp profile has correct structure."""
    assert 'defaultAction' in SECCOMP_PROFILE
    assert SECCOMP_PROFILE['defaultAction'] == 'SCMP_ACT_ERRNO'

    assert 'architectures' in SECCOMP_PROFILE
    assert 'SCMP_ARCH_X86_64' in SECCOMP_PROFILE['architectures']

    assert 'syscalls' in SECCOMP_PROFILE
    assert len(SECCOMP_PROFILE['syscalls']) > 0

    # Check network syscalls are blocked
    blocked_network = False
    for rule in SECCOMP_PROFILE['syscalls']:
        if 'socket' in rule.get('names', []):
            assert rule['action'] == 'SCMP_ACT_ERRNO'
            blocked_network = True
    assert blocked_network, "Network syscalls should be blocked"


def test_sandboxed_purple_agent_wrapper(sandbox, simple_attack):
    """Test SandboxedPurpleAgent wrapper."""
    from scenarios.sql_injection import SimplePatternPurpleAgent

    # Create simple purple agent
    purple_agent = SimplePatternPurpleAgent(patterns=["'", '"', 'OR', 'UNION'])

    # Wrap in sandbox
    sandboxed_agent = SandboxedPurpleAgent(purple_agent, sandbox)

    assert sandboxed_agent.get_name() == f"{purple_agent.get_name()}_sandboxed"

    # Execute detection
    result = sandboxed_agent.detect(simple_attack)

    assert result is not None
    assert result.attack_id == simple_attack.attack_id
    assert isinstance(result.detected, bool)


def test_sandbox_handles_malformed_code(sandbox, simple_attack):
    """Test sandbox handles malformed code gracefully."""
    # Invalid Python code
    purple_agent_code = """
def detect(payload):
    this is not valid python
    return {}
"""

    result = sandbox.execute_attack(
        attack=simple_attack,
        purple_agent_code=purple_agent_code
    )

    # Should return error result, not crash
    assert result is not None
    assert 'error' in result.detection_reason.lower() or 'fail' in result.detection_reason.lower()


def test_sandbox_serialization_patterns(sandbox):
    """Test purple agent serialization works for pattern-based agents."""
    from scenarios.sql_injection import SimplePatternPurpleAgent

    purple_agent = SimplePatternPurpleAgent(patterns=["SELECT", "UNION", "DROP"])
    sandboxed = SandboxedPurpleAgent(purple_agent, sandbox)

    code = sandboxed._serialize_purple_agent()

    # Check code contains patterns
    assert "SELECT" in code
    assert "UNION" in code
    assert "DROP" in code
    assert "def detect(payload):" in code


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
