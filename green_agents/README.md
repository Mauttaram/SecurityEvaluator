# Green Agents - Production A2A Evaluators

This directory contains **Green Agents** - production-ready evaluators that implement the A2A (Agent-to-Agent) protocol for AgentBeats integration.

---

## 🎯 What is a Green Agent?

A **Green Agent** is an **evaluator** that tests Purple Agents (security detectors) on their ability to detect cybersecurity threats.

**Key Requirements:**
- ✅ Exposes HTTP API with A2A protocol
- ✅ Implements `/card` endpoint (AgentCard)
- ✅ Implements `/tasks` endpoint (evaluation tasks)
- ✅ Provides comprehensive evaluation metrics
- ✅ Production-safe (sandbox isolation)

---

## 📁 Files

```
green_agents/
├── __init__.py                        # Module exports
├── cybersecurity_evaluator.py         # Main Green Agent (A2A server)
├── agent_card.py                      # AgentCard for A2A protocol
└── README.md                          # This file
```

---

## 🚀 Quick Start

### **1. Start the Green Agent (Evaluator)**

```bash
# Basic usage
python green_agents/cybersecurity_evaluator.py

# With custom host/port
python green_agents/cybersecurity_evaluator.py \
    --host 127.0.0.1 \
    --port 9010

# With LLM features enabled (requires API key)
python green_agents/cybersecurity_evaluator.py \
    --host 127.0.0.1 \
    --port 9010 \
    --enable-llm
```

### **2. Check Agent Card (A2A Protocol)**

```bash
curl http://127.0.0.1:9010/card
```

**Response:**
```json
{
  "name": "Cyber Security Evaluator",
  "description": "Cyber Security Evaluator - Green Agent for evaluating security detection agents...",
  "version": "2.0.0",
  "skills": [
    {
      "id": "cybersecurity_evaluation",
      "name": "Cyber Security Detection Evaluation",
      "tags": ["security", "vulnerability-detection", "benchmark", ...]
    }
  ]
}
```

### **3. Submit Evaluation Task**

```bash
curl -X POST http://127.0.0.1:9010/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "purple_agent_id": "my_detector",
      "purple_agent_endpoint": "http://127.0.0.1:8000",
      "config": {
        "scenario": "sql_injection",
        "max_rounds": 10,
        "budget_usd": 50.0,
        "use_sandbox": true,
        "use_cost_optimization": true,
        "use_coverage_tracking": true
      }
    }
  }'
```

**Response:**
```json
{
  "id": "task-abc-123",
  "status": "running",
  "created_at": "2025-11-07T12:00:00Z"
}
```

### **4. Check Task Status**

```bash
curl http://127.0.0.1:9010/tasks/task-abc-123
```

**Response:**
```json
{
  "id": "task-abc-123",
  "status": "completed",
  "output": {
    "status": "completed",
    "purple_agent_id": "my_detector",
    "scenario": "sql_injection",
    "metrics": {
      "f1_score": 0.823,
      "precision": 0.891,
      "recall": 0.764,
      "accuracy": 0.856,
      "false_positive_rate": 0.067,
      "false_negative_rate": 0.236
    },
    "evasions_found": 18,
    "total_tests": 156,
    "coverage": {
      "percentage": 45.2,
      "covered_techniques": 5,
      "total_techniques": 11
    },
    "cost_usd": 7.90,
    "duration_seconds": 127.3
  }
}
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│               CyberSecurityEvaluator Architecture                │
└─────────────────────────────────────────────────────────────────┘

                  CyberSecurityEvaluator
                  (Green Agent - HTTP/A2A Server)
                  ├─> GET /card         (AgentCard)
                  ├─> POST /tasks       (Submit evaluation)
                  ├─> GET /tasks/{id}   (Get results)
                  └─> Wraps ↓

                  UnifiedEcosystem
                  (Evaluation Engine - framework/ecosystem.py)
                  ├─> MetaOrchestrator  (Coalition management)
                  ├─> 7 Specialized Agents
                  │   ├─> BoundaryProber (Thompson Sampling)
                  │   ├─> Exploiter      (Hybrid generation)
                  │   ├─> Mutator        (Novelty Search)
                  │   ├─> Validator      (Syntax checks)
                  │   ├─> Perspective    (Multi-viewpoint)
                  │   ├─> LLMJudge       (Consensus)
                  │   └─> Counterfactual (Remediation)
                  ├─> Knowledge Base     (Shared memory)
                  ├─> Sandbox            (Docker isolation) ✅
                  ├─> Cost Optimizer     (Smart LLM routing)
                  └─> Coverage Tracker   (MITRE ATT&CK)
```

---

## 🎯 Supported Attack Scenarios

The CyberSecurityEvaluator supports multiple attack types:

| Scenario | Status | Description |
|----------|--------|-------------|
| `sql_injection` | ✅ Ready | SQL injection detection (7 categories) |
| `prompt_injection` | ✅ Ready | LLM prompt injection detection (7 categories) |
| `xss` | 🚧 Planned | Cross-site scripting detection |
| `command_injection` | 🚧 Planned | OS command injection detection |
| `path_traversal` | 🚧 Planned | Path traversal detection |

---

## 📖 Usage Examples

### **Example 1: SQL Injection Detection**

```bash
# Terminal 1: Start Green Agent
python green_agents/cybersecurity_evaluator.py --port 9010

# Terminal 2: Start your SQL injection detector (purple agent)
python purple_agents/sql_injection_detector.py --port 8000

# Terminal 3: Submit evaluation
curl -X POST http://127.0.0.1:9010/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "purple_agent_id": "my_sql_detector",
      "purple_agent_endpoint": "http://127.0.0.1:8000",
      "config": {
        "scenario": "sql_injection",
        "max_rounds": 10,
        "use_sandbox": true
      }
    }
  }'
```

### **Example 2: Prompt Injection Detection**

```bash
# Terminal 1: Start Green Agent
python green_agents/cybersecurity_evaluator.py --port 9010

# Terminal 2: Start prompt injection detector (purple agent)
python purple_agents/prompt_injection_detector.py --port 8000 --sensitivity medium

# Terminal 3: Submit evaluation
curl -X POST http://127.0.0.1:9010/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "purple_agent_id": "my_llm_detector",
      "purple_agent_endpoint": "http://127.0.0.1:8000",
      "config": {
        "scenario": "prompt_injection",
        "max_rounds": 10,
        "use_sandbox": true
      }
    }
  }'
```

**See complete walkthrough:** [examples/prompt_injection_demo.md](../examples/prompt_injection_demo.md)

---

## ⚙️ Configuration

### **Evaluation Config**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `scenario` | string | `"sql_injection"` | Attack type: `sql_injection`, `prompt_injection` |
| `max_rounds` | int | `10` | Maximum evaluation rounds |
| `budget_usd` | float | `50.0` | Maximum budget in USD |
| `use_sandbox` | bool | `true` | **CRITICAL**: Enable container isolation |
| `use_cost_optimization` | bool | `true` | Enable smart LLM routing |
| `use_coverage_tracking` | bool | `true` | Enable MITRE ATT&CK tracking |
| `num_boundary_probers` | int | `2` | Number of boundary probing agents |
| `num_exploiters` | int | `3` | Number of attack generation agents |
| `num_mutators` | int | `2` | Number of mutation agents |
| `num_validators` | int | `1` | Number of validation agents |
| `random_seed` | int | `null` | Random seed for reproducibility |

**⚠️  IMPORTANT: Always use `use_sandbox: true` in production!**

---

## 🔐 Production Features

### **1. Sandbox Isolation (CRITICAL)**

✅ **Enabled by default** - Purple agent code executes in isolated Docker container

**Protection:**
- Container isolation (Docker)
- CPU limit: 0.5 cores
- Memory limit: 512MB
- Timeout: 30 seconds
- Network: DISABLED
- Filesystem: READ-ONLY
- seccomp: ENABLED

### **2. Cost Optimization**

Smart LLM routing reduces costs by 30-60%:
- GPT-4 for complex tasks
- GPT-3.5 for simple tasks
- Caching for repeated queries

### **3. MITRE ATT&CK Coverage**

Tracks which techniques are covered:
```json
{
  "coverage": {
    "percentage": 45.2,
    "covered_techniques": ["T1190", "T1078", ...],
    "total_techniques": 11
  }
}
```

---

## 📊 Evaluation Metrics

The Green Agent returns comprehensive metrics:

| Metric | Description | Range |
|--------|-------------|-------|
| **F1 Score** | Harmonic mean of precision and recall | 0.0 - 1.0 |
| **Precision** | True positives / (True positives + False positives) | 0.0 - 1.0 |
| **Recall** | True positives / (True positives + False negatives) | 0.0 - 1.0 |
| **Accuracy** | (TP + TN) / Total tests | 0.0 - 1.0 |
| **FPR** | False Positive Rate | 0.0 - 1.0 |
| **FNR** | False Negative Rate | 0.0 - 1.0 |

**Plus:**
- **Evasions Found**: Number of attacks that bypassed detection
- **Coverage**: MITRE ATT&CK technique coverage
- **Cost**: Total LLM API cost in USD
- **Duration**: Total evaluation time in seconds

---

## 🔧 Development

### **Import as Module**

```python
from green_agents import CyberSecurityEvaluator, cybersecurity_agent_card

# Create agent
agent = CyberSecurityEvaluator(enable_llm=False)

# Get agent card
card = cybersecurity_agent_card(
    agent_name="My Evaluator",
    card_url="http://localhost:9010/card"
)

# Register and start server
agent.register_card(card)
await agent.start_server(host="127.0.0.1", port=9010)
```

---

## 🆚 Comparison with Legacy

| Feature | CyberSecurityEvaluator | SQLInjectionJudge (Legacy) |
|---------|------------------------|----------------------------|
| A2A Protocol | ✅ YES | ✅ YES |
| Multi-Agent Framework | ✅ YES | ❌ NO |
| Sandbox Isolation | ✅ YES (default) | ❌ NO |
| Multiple Attack Types | ✅ YES | ❌ SQL only |
| MITRE ATT&CK Tracking | ✅ YES | ❌ NO |
| Cost Optimization | ✅ YES | ❌ NO |
| **Recommended for** | **PRODUCTION** | Demo/testing |

---

## 📚 Documentation

- **Architecture**: See `framework/docs/ARCHITECTURE_CLARIFICATION.md`
- **Agent Details**: See `framework/docs/ARCHITECTURE_FLOW.md`
- **Production Guide**: See `framework/docs/PRODUCTION_GUIDE.md`

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: httpx` | Install dependencies: `pip install -r requirements.txt` |
| `ModuleNotFoundError: scipy` | Install dependencies: `pip install scipy` |
| Connection refused to purple agent | Ensure purple agent is running on specified port |
| Sandbox not working | Install Docker: https://docs.docker.com/get-docker/ |
| High LLM costs | Set `use_cost_optimization: true` in config |

---

## 📝 License

See [LICENSE](../LICENSE) file.

---

**Created**: November 2025
**Version**: 2.0
**Status**: Production Ready ✅
