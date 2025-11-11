# Verify AgentCard Shows Both Scenarios

This guide verifies that the Green Agent's `/card` endpoint properly advertises both SQL injection and prompt injection capabilities.

---

## ✅ Verification Steps

### Step 1: Start the Green Agent

```bash
python green_agents/cybersecurity_evaluator.py --port 9010
```

Expected output:
```
======================================================================
Cyber Security Evaluator - Green Agent
======================================================================
Host: 127.0.0.1
Port: 9010
LLM: Disabled
======================================================================

✅ Agent card registered at: http://127.0.0.1:9010/card
✅ Submit tasks to: http://127.0.0.1:9010/tasks

Waiting for evaluation requests...
```

---

### Step 2: Get AgentCard

```bash
curl http://127.0.0.1:9010/card | jq
```

---

### Step 3: Verify Response Contains Both Scenarios

**Expected Response Structure:**

```json
{
  "name": "Cyber Security Evaluator",
  "description": "Cyber Security Evaluator - Green Agent for evaluating security detection agents...",
  "url": "http://127.0.0.1:9010/card",
  "version": "2.0.0",
  "default_input_modes": ["text"],
  "default_output_modes": ["text"],
  "capabilities": {
    "streaming": true
  },
  "skills": [
    {
      "id": "cybersecurity_evaluation",
      "name": "Cyber Security Detection Evaluation",
      "description": "Evaluates Purple Agents on their ability to detect cybersecurity vulnerabilities across multiple attack types and techniques. Uses advanced multi-agent framework with adaptive testing, coalition-based attack generation, and comprehensive metrics. Supports SQL injection, prompt injection (LLM security), and more. Includes MITRE ATT&CK coverage tracking, cost optimization, and production-safe sandboxing.",
      "tags": [
        "security",
        "vulnerability-detection",
        "benchmark",
        "sql-injection",              ← SQL Injection supported ✅
        "prompt-injection",           ← Prompt Injection supported ✅
        "llm-security",
        "jailbreak-detection",
        "xss",
        "command-injection",
        "mitre-attack",
        "owasp-top-10",
        "adaptive-testing",
        "red-team"
      ],
      "examples": [
        "{\n  \"purple_agent_id\": \"my_sql_injection_detector\",\n  \"purple_agent_endpoint\": \"http://127.0.0.1:8000\",\n  \"config\": {\n    \"scenario\": \"sql_injection\",\n    ...\n  }\n}",
        "{\n  \"purple_agent_id\": \"my_prompt_injection_detector\",\n  \"purple_agent_endpoint\": \"http://127.0.0.1:8000\",\n  \"config\": {\n    \"scenario\": \"prompt_injection\",\n    ...\n  }\n}"
      ]
    }
  ]
}
```

---

### Step 4: Verify Tags

Check that the `tags` array contains:

```json
"tags": [
  ...
  "sql-injection",      ← ✅ SQL Injection
  "prompt-injection",   ← ✅ Prompt Injection
  "llm-security",       ← ✅ LLM Security
  "jailbreak-detection", ← ✅ Jailbreak Detection
  ...
]
```

---

### Step 5: Verify Examples

Check that the `examples` array contains TWO examples:

**Example 1: SQL Injection**
```json
{
  "purple_agent_id": "my_sql_injection_detector",
  "purple_agent_endpoint": "http://127.0.0.1:8000",
  "config": {
    "scenario": "sql_injection",
    "max_rounds": 10,
    "budget_usd": 50.0,
    "use_sandbox": true,
    ...
  }
}
```

**Example 2: Prompt Injection**
```json
{
  "purple_agent_id": "my_prompt_injection_detector",
  "purple_agent_endpoint": "http://127.0.0.1:8000",
  "config": {
    "scenario": "prompt_injection",
    "max_rounds": 10,
    "budget_usd": 50.0,
    "use_sandbox": true,
    ...
  }
}
```

---

## ✅ Expected Behavior

When a client (or AgentBeats platform) calls `/card`, they will see:

1. ✅ **Single Green Agent** named "Cyber Security Evaluator"
2. ✅ **Version 2.0.0**
3. ✅ **Tags** including both `sql-injection` and `prompt-injection`
4. ✅ **Two examples** showing how to evaluate both attack types
5. ✅ **Description** mentioning support for multiple scenarios

This proves that:
- **ONE Green Agent** supports **MULTIPLE scenarios**
- Clients can select which scenario to test via the `config.scenario` parameter
- The AgentCard properly advertises all capabilities

---

## 🧪 Test Both Scenarios

### Test 1: SQL Injection Evaluation

```bash
# Start SQL injection detector (purple agent)
python purple_agents/baseline/sql_injection_detector.py --port 8000

# Submit SQL injection evaluation
curl -X POST http://127.0.0.1:9010/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "purple_agent_id": "test_sql_detector",
      "purple_agent_endpoint": "http://127.0.0.1:8000",
      "config": {
        "scenario": "sql_injection"
      }
    }
  }' | jq
```

### Test 2: Prompt Injection Evaluation

```bash
# Stop SQL detector, start prompt injection detector
# (kill previous purple agent)
python purple_agents/prompt_injection_detector.py --port 8000

# Submit prompt injection evaluation (SAME Green Agent!)
curl -X POST http://127.0.0.1:9010/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "purple_agent_id": "test_prompt_detector",
      "purple_agent_endpoint": "http://127.0.0.1:8000",
      "config": {
        "scenario": "prompt_injection"
      }
    }
  }' | jq
```

---

## 📊 Summary

| Check | Expected | Verified |
|-------|----------|----------|
| Single Green Agent | ✅ Yes | ✅ |
| AgentCard version 2.0.0 | ✅ Yes | ✅ |
| Tag: `sql-injection` | ✅ Present | ✅ |
| Tag: `prompt-injection` | ✅ Present | ✅ |
| Tag: `llm-security` | ✅ Present | ✅ |
| Example 1: sql_injection | ✅ Present | ✅ |
| Example 2: prompt_injection | ✅ Present | ✅ |
| Can evaluate SQL detectors | ✅ Yes | ✅ |
| Can evaluate prompt detectors | ✅ Yes | ✅ |

---

**Result:** The Green Agent properly advertises support for BOTH sql_injection and prompt_injection scenarios through its AgentCard! 🎉
