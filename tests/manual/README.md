# Manual Test Scripts

This directory contains manual test scripts for interactive testing and verification.

## Scripts

### test_llm_setup.py
**Purpose:** Verify OpenAI API setup and credentials

**Usage:**
```bash
python tests/manual/test_llm_setup.py
```

**What it tests:**
- .env file exists
- OPENAI_API_KEY is set
- API key is valid (makes test call)

### test_evaluation.py
**Purpose:** Test Purple Agent evaluation locally (simulates Green Agent evaluation)

**Usage:**
```bash
python tests/manual/test_evaluation.py
```

**What it tests:**
- Dataset loading
- Purple Agent detection
- Scoring engine
- End-to-end evaluation flow

### test_tasks_endpoint.py
**Purpose:** Test Green Agent /tasks endpoint via HTTP

**Prerequisites:** Green Agent must be running on port 9010

**Usage:**
```bash
# Terminal 1: Start Green Agent
python green_agents/cybersecurity_evaluator.py --port 9010

# Terminal 2: Run test
python tests/manual/test_tasks_endpoint.py
```

**What it tests:**
- Agent is running
- AgentCard endpoint (A2A protocol)
- Task submission
- Task status checking

### test_green_agent.sh
**Purpose:** Shell script version of tasks endpoint test

**Prerequisites:** Green Agent must be running on port 9010

**Usage:**
```bash
# Terminal 1: Start Green Agent
python green_agents/cybersecurity_evaluator.py --port 9010

# Terminal 2: Run test
bash tests/manual/test_green_agent.sh
```

**What it tests:**
- Same as test_tasks_endpoint.py but using curl/jq
- Useful for quick command-line testing

## Automated Tests

For automated pytest tests, see the test files in the parent `tests/` directory:
```bash
# Run all pytest tests
pytest tests/

# Run specific test file
pytest tests/test_llm_integration.py -v
```

## Notes

- These manual scripts are for interactive testing during development
- They require manual setup (starting servers, checking output)
- For CI/CD, use the pytest tests in `tests/` directory instead
