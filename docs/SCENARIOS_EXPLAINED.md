# Scenarios vs Agents - Clear Explanation

**Last Updated:** November 2025

---

## ⚡ Quick Summary

```
┌────────────────────────────────────────────────────────────────┐
│  ONE Green Agent (CyberSecurityEvaluator)                      │
│  └─> Supports MULTIPLE Scenarios (sql_injection, prompt_injection, etc.) │
│      └─> Evaluates MULTIPLE Purple Agents (detectors)         │
└────────────────────────────────────────────────────────────────┘
```

---

## 🟢 Green Agent (ONE)

**File:** `green_agents/cybersecurity_evaluator.py`

**What it is:**
- A **single HTTP/A2A server** that runs on port 9010
- Evaluates security detectors (Purple Agents)
- Exposes `/card` and `/tasks` endpoints

**Supported Scenarios:**
- ✅ `sql_injection` - SQL injection detection
- ✅ `prompt_injection` - LLM prompt injection detection
- 🚧 `xss` - Cross-site scripting (planned)
- 🚧 `command_injection` - OS command injection (planned)

**How to use:**
```bash
# Start the Green Agent (supports ALL scenarios)
python green_agents/cybersecurity_evaluator.py --port 9010

# Check capabilities (shows ALL supported scenarios)
curl http://127.0.0.1:9010/card
```

**AgentCard Response:**
```json
{
  "name": "Cyber Security Evaluator",
  "version": "2.0.0",
  "skills": [{
    "id": "cybersecurity_evaluation",
    "name": "Cyber Security Detection Evaluation",
    "tags": [
      "sql-injection",           ← Supports SQL injection scenario
      "prompt-injection",        ← Supports prompt injection scenario
      "llm-security",
      "jailbreak-detection",
      ...
    ],
    "examples": [
      "scenario: sql_injection",    ← Example 1
      "scenario: prompt_injection"  ← Example 2
    ]
  }]
}
```

---

## 📜 Scenarios (Multiple per Green Agent)

**What they are:**
- **Attack type definitions** that the Green Agent can evaluate
- Located in `scenarios/` directory
- Each defines attack templates, validation rules, MITRE mappings, mutations

**Available Scenarios:**

### 1. SQL Injection (`scenarios/sql_injection.py`)
```python
class SQLInjectionScenario(SecurityScenario):
    """Defines SQL injection attacks (7 categories)"""

    def get_attack_templates(self) -> List[Attack]:
        # Returns SQL injection attack templates

    def get_mitre_techniques(self) -> List[str]:
        # Returns ["T1190", "T1078", ...]
```

### 2. Prompt Injection (`scenarios/prompt_injection.py`)
```python
class PromptInjectionScenario(SecurityScenario):
    """Defines prompt injection attacks (7 categories)"""

    def get_attack_templates(self) -> List[Attack]:
        # Returns jailbreak, prompt leaking, role manipulation, etc.

    def get_mitre_techniques(self) -> List[str]:
        # Returns ["T1059", "T1036", "LLM01", "LLM02", ...]
```

**How scenarios are selected:**
```bash
# When submitting a task, specify which scenario to test
curl -X POST http://127.0.0.1:9010/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "purple_agent_id": "my_detector",
      "purple_agent_endpoint": "http://127.0.0.1:8000",
      "config": {
        "scenario": "sql_injection"    # ← SELECT SCENARIO HERE
      }
    }
  }'

# Or test a different scenario with the SAME Green Agent
curl -X POST http://127.0.0.1:9010/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "purple_agent_id": "my_llm_detector",
      "purple_agent_endpoint": "http://127.0.0.1:8001",
      "config": {
        "scenario": "prompt_injection"  # ← DIFFERENT SCENARIO
      }
    }
  }'
```

---

## 🟣 Purple Agents (Multiple, evaluated by Green Agent)

**What they are:**
- **Security detectors** that the Green Agent evaluates
- Can be ANY detector that implements the `/detect` endpoint
- Each purple agent can support one or more attack types

**Example Purple Agents:**

### 1. SQL Injection Detector
**File:** `purple_agents/baseline/sql_injection_detector.py` (example)

**What it does:**
- Detects SQL injection vulnerabilities in code
- Pattern-based detection
- Evaluated by Green Agent using `scenario: "sql_injection"`

**How to use:**
```bash
# Terminal 1: Start Purple Agent (SQL detector)
python purple_agents/baseline/sql_injection_detector.py --port 8000

# Terminal 2: Start Green Agent
python green_agents/cybersecurity_evaluator.py --port 9010

# Terminal 3: Evaluate the SQL detector
curl -X POST http://127.0.0.1:9010/tasks \
  -d '{"config": {"scenario": "sql_injection"}, ...}'
```

### 2. Prompt Injection Detector
**File:** `purple_agents/prompt_injection_detector.py` (example)

**What it does:**
- Detects prompt injection attacks against LLMs
- Pattern-based + heuristic detection
- Evaluated by Green Agent using `scenario: "prompt_injection"`

**How to use:**
```bash
# Terminal 1: Start Purple Agent (prompt injection detector)
python purple_agents/prompt_injection_detector.py --port 8000

# Terminal 2: Start Green Agent (SAME Green Agent as above!)
python green_agents/cybersecurity_evaluator.py --port 9010

# Terminal 3: Evaluate the prompt injection detector
curl -X POST http://127.0.0.1:9010/tasks \
  -d '{"config": {"scenario": "prompt_injection"}, ...}'
```

### 3. Multi-Purpose Detector (Your Custom Purple Agent)
**File:** Your implementation

**What it could do:**
- Detect BOTH SQL injection AND prompt injection
- Or specialize in just one type
- Implement `/detect` endpoint that receives attack payloads

**Example implementation:**
```python
from aiohttp import web
from agentbeats.purple_executor import PurpleAgent

class MyUniversalDetector(PurpleAgent):
    """Detects multiple attack types"""

    async def detect(self, attack):
        attack_type = attack.get('attack_type')

        if attack_type == 'sql_injection':
            return self.detect_sql_injection(attack)
        elif attack_type == 'prompt_injection':
            return self.detect_prompt_injection(attack)
        else:
            return {"is_vulnerable": False}

# Run as HTTP server on port 8000
```

---

## 🔄 Complete Evaluation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     EVALUATION FLOW                              │
└─────────────────────────────────────────────────────────────────┘

Client
  │
  │ POST /tasks {"scenario": "sql_injection"}
  ▼
Green Agent (CyberSecurityEvaluator) @ port 9010
  │
  │ Loads SQLInjectionScenario
  ▼
UnifiedEcosystem (framework)
  │
  │ Creates 7 specialized agents
  │ - BoundaryProber
  │ - Exploiter
  │ - Mutator
  │ - Validator
  │ - Perspective
  │ - LLMJudge
  │ - Counterfactual
  ▼
Generates SQL injection attacks
  │
  │ POST /detect (SQL attack payload)
  ▼
Purple Agent (SQL Detector) @ port 8000
  │
  │ Returns {"is_vulnerable": true/false}
  ▼
Green Agent
  │
  │ Aggregates results, calculates metrics
  ▼
Client receives evaluation report
```

---

## 📂 Directory Structure Explained

```
SecurityEvaluator/
│
├── green_agents/                           ← ONE GREEN AGENT
│   ├── cybersecurity_evaluator.py         ← HTTP server (port 9010)
│   ├── agent_card.py                      ← Lists ALL scenarios
│   └── README.md
│
├── scenarios/                              ← MULTIPLE SCENARIOS
│   ├── sql_injection.py                   ← Scenario 1
│   ├── prompt_injection.py                ← Scenario 2
│   └── (future: xss.py, command_injection.py, ...)
│
├── purple_agents/                          ← MULTIPLE PURPLE AGENTS (examples)
│   ├── prompt_injection_detector.py       ← Example purple agent 1
│   ├── baseline/
│   │   └── sql_injection_detector.py      ← Example purple agent 2
│   └── (your custom detectors here)
│
└── framework/                              ← SHARED BY ALL SCENARIOS
    ├── ecosystem.py                        ← UnifiedEcosystem
    ├── orchestrator.py                     ← MetaOrchestrator
    └── agents/                             ← 7 specialized agents
        ├── boundary_prober.py
        ├── exploiter.py
        ├── mutator_agent.py
        └── ...
```

---

## ❓ Common Questions

### Q: Is prompt_injection_detector.py a separate Green Agent?
**A:** No! It's an **example Purple Agent** (detector) that gets **evaluated BY** the Green Agent.

### Q: How many Green Agents do I need to run?
**A:** **ONE**. The single Green Agent (`cybersecurity_evaluator.py`) supports all scenarios.

### Q: How do I add a new attack type (e.g., XSS)?
**A:**
1. Create `scenarios/xss.py` (define attack templates)
2. Add to `scenario_map` in `cybersecurity_evaluator.py`
3. Update `agent_card.py` tags to include `'xss'`
4. Green Agent now supports XSS evaluation!

### Q: Can one Purple Agent support multiple scenarios?
**A:** Yes! Your purple agent's `/detect` endpoint can check the `attack_type` field and handle multiple types.

### Q: When I call GET /card, what will I see?
**A:** You'll see **ONE** AgentCard listing **ALL** supported scenarios (sql_injection, prompt_injection, etc.).

---

## ✅ Correct Usage Pattern

```bash
# 1. Start ONE Green Agent (supports ALL scenarios)
python green_agents/cybersecurity_evaluator.py --port 9010

# 2. Check what scenarios it supports
curl http://127.0.0.1:9010/card
# Response shows: sql-injection, prompt-injection, etc.

# 3. Start your Purple Agent (detector for SQL injection)
python purple_agents/baseline/sql_injection_detector.py --port 8000

# 4. Evaluate SQL injection detection
curl -X POST http://127.0.0.1:9010/tasks \
  -d '{"config": {"scenario": "sql_injection"}, ...}'

# 5. Later, test prompt injection with SAME Green Agent
#    (just change the purple agent and scenario)
python purple_agents/prompt_injection_detector.py --port 8001

curl -X POST http://127.0.0.1:9010/tasks \
  -d '{"config": {"scenario": "prompt_injection"}, ...}'
```

---

## 🚫 Incorrect Usage Pattern

```bash
# ❌ WRONG: Starting separate green agents for each scenario
python green_agents/sql_injection_evaluator.py --port 9010      # NO!
python green_agents/prompt_injection_evaluator.py --port 9011  # NO!

# ✅ CORRECT: One green agent, select scenario in config
python green_agents/cybersecurity_evaluator.py --port 9010     # YES!
# Then specify scenario: "sql_injection" or "prompt_injection" in task config
```

---

## 📊 Summary Table

| Component | Count | Purpose | Example |
|-----------|-------|---------|---------|
| **Green Agent** | 1 | Evaluator HTTP server | `cybersecurity_evaluator.py` |
| **Scenarios** | Multiple | Attack type definitions | `sql_injection.py`, `prompt_injection.py` |
| **Purple Agents** | Multiple | Detectors being evaluated | `sql_injection_detector.py`, `prompt_injection_detector.py` |
| **Framework** | 1 | Shared evaluation engine | `UnifiedEcosystem` (7 agents) |

---

## 🔗 See Also

- **AgentCard Implementation**: `green_agents/agent_card.py`
- **Scenario Definitions**: `scenarios/`
- **Example Purple Agents**: `purple_agents/`
- **Complete Architecture**: `framework/docs/ARCHITECTURE_CLARIFICATION.md`

---

**Key Takeaway:**
- **1 Green Agent** (CyberSecurityEvaluator)
- **Multiple Scenarios** (sql_injection, prompt_injection, ...)
- **Multiple Purple Agents** (whatever you want to evaluate)

The Green Agent is **universal** - it evaluates ANY security detector on ANY supported scenario!
