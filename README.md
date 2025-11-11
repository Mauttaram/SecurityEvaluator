# Security Evaluator - Production-Ready Cyber Security Evaluation Framework

**Version:** 2.4
**Status:** ✅ Production Ready
**License:** See [LICENSE](LICENSE)

---

## 🚀 Quick Start & Setup

### Installation

```bash
# 1. Clone the repository
cd /path/to/SecurityEvaluator

# 2. Install core dependencies (required)
python3 -m pip install --user --break-system-packages \
  numpy scipy scikit-learn pydantic python-dotenv httpx

# 3. Setup API keys (optional, for LLM features)
cp .env.example .env
# Edit .env and add your API keys (OpenAI, Anthropic, Google)

# 4. Verify installation
python3 -c "from framework.scenarios import SQLInjectionScenario; print('✅ Framework ready')"
```

### Testing

**ONE script for all testing:** `run_evaluation_tests.py`

#### **1. Validate Framework (Test the Green Agent)**

```bash
python3 run_evaluation_tests.py --validate
```
**What it does:** Verifies the Green Agent framework components are working:
- All 7 agents initialized and functional
- Orchestrator coordinating properly
- LLM integration working (mock)
- Attack generation and execution
- Metrics calculation

**Duration:** ~3-5 seconds
**Result:** ✅ Framework validation passed

#### **2. Evaluate Purple Agents (Use the Green Agent)**

```bash
# Test prompt injection detection with 10 rounds
python3 run_evaluation_tests.py --scenario prompt --max-rounds 10

# Test SQL injection detection with LLM support
python3 run_evaluation_tests.py --scenario sql --llm --max-rounds 5

# Quick test all scenarios (2 rounds each)
python3 run_evaluation_tests.py --scenario all --quick
```
**What it does:** Uses the Green Agent to evaluate Purple Agent detectors:
- Generates attacks across multiple techniques
- Tests Purple Agent detection
- Calculates F1, Precision, Recall, Accuracy
- Reports per-technique performance

**Duration:** ~30-60 seconds (depends on rounds)
**Result:** Detailed metrics on Purple Agent performance

### Production Deployment

```bash
# 1. Start CyberSecurityEvaluator (Full A2A Protocol)
python3 green_agents/cybersecurity_evaluator.py --host 127.0.0.1 --port 9010

# 2. Submit evaluation via HTTP/A2A Protocol
curl -X POST http://127.0.0.1:9010/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "purple_agent_id": "my_detector",
      "purple_agent_endpoint": "http://127.0.0.1:8000",
      "config": {
        "scenario": "sql_injection",
        "use_sandbox": true
      }
    }
  }'
```

**✅ Framework Features:**
- A2A Protocol (AgentBeats compliant)
- Sandbox isolation (enabled by default)
- Multi-agent framework (7 specialized agents)
- MITRE ATT&CK coverage tracking
- Cost optimization
- Production-safe

---

## 📖 What is This?

**Security Evaluator** is a production-ready framework for evaluating cybersecurity detection systems (Purple Agents) using advanced multi-agent techniques.

### Key Components:

```
┌─────────────────────────────────────────────────────────────┐
│           PRODUCTION ARCHITECTURE                            │
└─────────────────────────────────────────────────────────────┘

              CyberSecurityEvaluator
              (Green Agent - A2A Protocol)
              ├─> HTTP API Server
              ├─> AgentBeats Integration
              └─> Wraps ↓

              UnifiedEcosystem
              (Evaluation Engine)
              ├─> MetaOrchestrator
              ├─> 7 Specialized Agents
              ├─> Sandbox (Docker isolation)
              ├─> Cost Optimizer
              └─> Coverage Tracker (MITRE)
```

### Production Features:

✅ **Sandbox Isolation** - Docker containers with resource limits, network disabled, read-only filesystem
✅ **A2A Protocol** - Full AgentBeats compliance for ecosystem integration
✅ **Multi-Agent Framework** - 7 specialized agents (BoundaryProber, Exploiter, Mutator, Validator, etc.)
✅ **MITRE ATT&CK Tracking** - Comprehensive technique coverage reporting
✅ **Cost Optimization** - Smart LLM routing (30-60% cost savings)
✅ **Scalable** - Supports multiple attack types (SQL injection, XSS, Command Injection, etc.)

---

## 📚 Documentation

### Quick Start & Testing:
**👉 [HOW_TO_TEST_LOCALLY.md](HOW_TO_TEST_LOCALLY.md)** - ⭐ **START HERE** - Complete local testing guide
**👉 [GETTING_STARTED.md](GETTING_STARTED.md)** - Quick setup and testing (3 scenarios ready!)
**👉 [ARCHITECTURE.md](ARCHITECTURE.md)** - System design and architecture overview
**👉 [MULTI_LLM_GUIDE.md](MULTI_LLM_GUIDE.md)** - Multi-LLM consensus setup (optional)

### For Production Deployment:
**👉 [green_agents/README.md](green_agents/README.md)** - A2A protocol deployment guide
**👉 [framework/docs/PRODUCTION_GUIDE.md](framework/docs/PRODUCTION_GUIDE.md)** - Production deployment
**👉 [framework/docs/ARCHITECTURE_CLARIFICATION.md](framework/docs/ARCHITECTURE_CLARIFICATION.md)** - Architecture details

### For Understanding the Framework:
- **[QUICK_START_VISUAL.md](framework/docs/QUICK_START_VISUAL.md)** - 30-second visual overview
- **[README_ARCHITECTURE.md](framework/docs/README_ARCHITECTURE.md)** - Navigation hub
- **[ARCHITECTURE_FLOW.md](framework/docs/ARCHITECTURE_FLOW.md)** - Complete code flow

### Complete Documentation Index:
See [framework/docs/README.md](framework/docs/README.md) for all documentation.

---

## 🏗️ Project Structure

```
SecurityEvaluator/
├── green_agents/                      ← Production Green Agents (A2A servers)
│   ├── cybersecurity_evaluator.py    ← Main entry point ⭐
│   ├── agent_card.py                 ← AgentCard for A2A protocol
│   └── README.md                     ← Complete usage guide
│
├── framework/                         ← Core evaluation engine
│   ├── ecosystem.py                  ← UnifiedEcosystem (wrapped by Green Agent)
│   ├── orchestrator.py               ← MetaOrchestrator (coalition management)
│   ├── agents/                       ← 7 specialized agents
│   │   ├── boundary_prober.py
│   │   ├── exploiter.py
│   │   ├── mutator_agent.py
│   │   ├── validator.py
│   │   ├── perspective.py
│   │   ├── llm_judge.py
│   │   └── counterfactual.py
│   ├── scenarios/                    ← Attack scenarios
│   │   ├── sql_injection.py          ← SQL injection (7 techniques)
│   │   ├── prompt_injection.py       ← Prompt injection (7 techniques)
│   │   └── active_scanning.py        ← Active scanning (8 techniques)
│   ├── sandbox.py                    ← Container isolation
│   ├── cost_optimizer.py             ← LLM cost management
│   ├── coverage_tracker.py           ← MITRE ATT&CK tracking
│   └── docs/                         ← Complete documentation
│
├── purple_agents/                     ← Example purple agents
│   ├── prompt_injection_detector.py  ← Example prompt injection detector
│   └── baseline/                     ← Baseline detector examples
│
├── examples/                          ← Usage examples and demos
│   └── prompt_injection_demo.md      ← Complete prompt injection walkthrough
│
├── tests/                             ← Test suite (unit tests)
│
├── test_simple.py                     ← Quick framework test ⭐
├── test_direct_evaluation.py          ← Direct attack execution test ⭐
├── test_a2a_protocol.sh               ← A2A protocol test ⭐
├── green_agent_standalone.py          ← Standalone HTTP server ⭐
└── HOW_TO_TEST_LOCALLY.md             ← Complete local testing guide
```

---

## 🎯 Use Cases

### 1. Production Evaluation
Evaluate your security detection system in a production-safe environment:
```bash
python green_agents/cybersecurity_evaluator.py
```

### 2. AgentBeats Integration
Integrate with AgentBeats platform via A2A protocol:
```bash
curl http://127.0.0.1:9010/card  # Get AgentCard
```

### 3. Multi-Attack Type Testing
Test against multiple attack types:
```json
{
  "config": {
    "scenario": "sql_injection",     // SQL injection detection
    "scenario": "prompt_injection",  // LLM prompt injection detection
    // Future: "xss", "command_injection", "path_traversal", etc.
    "use_sandbox": true
  }
}
```

**Available Scenarios:**
- ✅ **sql_injection**: SQL injection attacks (7 techniques, 12+ attack templates)
- ✅ **prompt_injection**: LLM prompt injection attacks (7 techniques, 32+ attack templates)
- ✅ **active_scanning**: Active scanning/reconnaissance (8 techniques, MITRE T1595)
- 🚧 **xss**: Cross-site scripting (planned)
- 🚧 **command_injection**: OS command injection (planned)

### 4. MITRE ATT&CK Coverage
Track which techniques your detector covers:
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

## 🔐 Security & Safety

### Sandbox Isolation (Enabled by Default)

All evaluations run in isolated Docker containers:
- **CPU Limit:** 0.5 cores
- **Memory Limit:** 512MB
- **Timeout:** 30 seconds
- **Network:** DISABLED
- **Filesystem:** READ-ONLY
- **seccomp:** ENABLED

**⚠️ IMPORTANT:** Never disable sandbox in production!

---

## 📊 Evaluation Metrics

The framework provides comprehensive metrics:

| Metric | Description |
|--------|-------------|
| **F1 Score** | Harmonic mean of precision and recall |
| **Precision** | Percentage of correct detections |
| **Recall** | Percentage of attacks detected |
| **Accuracy** | Overall correctness |
| **FPR/FNR** | False positive/negative rates |
| **Evasions** | Attacks that bypassed detection |
| **Coverage** | MITRE ATT&CK technique coverage |

---

## 🧪 Testing

**Use ONE script for all testing:** `run_evaluation_tests.py`

### 1. Framework Validation

Verify that the Green Agent framework is working properly:

```bash
python3 run_evaluation_tests.py --validate
```

**What this tests:**
- All 7 agents initialized and functional
- Orchestrator coordination
- LLM integration (mock)
- Attack generation and execution
- Metrics calculation

**Duration:** ~3-5 seconds
**Expected result:** ✅ Framework validation passed

### 2. Purple Agent Evaluation

Use the Green Agent to evaluate Purple Agent detectors:

```bash
# Test prompt injection detection with 10 rounds
python3 run_evaluation_tests.py --scenario prompt --max-rounds 10

# Test SQL injection detection with LLM support
python3 run_evaluation_tests.py --scenario sql --llm --max-rounds 5

# Quick test all scenarios (2 rounds each)
python3 run_evaluation_tests.py --scenario all --quick
```

**What this tests:**
- Purple Agent detection capabilities
- F1 score, Precision, Recall, Accuracy
- Per-technique performance
- Attack evasion analysis

**Duration:** ~30-60 seconds (depends on rounds and scenario)
**Expected result:** Detailed metrics report

### Available Options

```bash
--validate              # Run framework validation tests
--scenario <name>       # Choose: sql, prompt, active_scan, all
--max-rounds <N>        # Number of evaluation rounds (default: 5)
--llm                   # Enable real LLM API calls (costs money)
--quick                 # Quick mode (2 rounds instead of 5)

---

## 🔧 Troubleshooting

### Installation Issues

**Error: "externally-managed-environment"**
```bash
# Solution: Use --user and --break-system-packages flags
python3 -m pip install --user --break-system-packages numpy scipy scikit-learn
```

**Error: "ModuleNotFoundError: No module named 'numpy'"**
```bash
# Solution: Install dependencies
python3 -m pip install --user --break-system-packages \
  numpy scipy scikit-learn pydantic python-dotenv httpx
```

### Testing Issues

**Zero attacks executed / F1 Score is 0**
```bash
# Run framework validation to check all components
python3 run_evaluation_tests.py --validate
```

**API keys not loading**
```bash
# Verify .env file exists and has keys
python3 verify_env.py
```

**Import errors in tests**
```bash
# Make sure you're running from project root
cd /path/to/SecurityEvaluator
python3 run_evaluation_tests.py --validate
```

### Quick Verification

```bash
# Verify framework is working
python3 -c "from framework.scenarios import SQLInjectionScenario; print('✅ Framework ready')"

# Validate all components
python3 run_evaluation_tests.py --validate

# Run evaluation test
python3 run_evaluation_tests.py --scenario prompt --max-rounds 10
```

---

## 🤝 Contributing

1. Read the architecture documentation
2. Understand the production architecture ([ARCHITECTURE_CLARIFICATION.md](framework/docs/ARCHITECTURE_CLARIFICATION.md))
3. Write tests for new features
4. Follow code style guidelines
5. Submit pull request

---

## 📝 License

See [LICENSE](LICENSE) file for details.

---

## 🆚 Production vs Legacy

| Feature | CyberSecurityEvaluator (Production) | SQLInjectionJudge (Legacy) |
|---------|-------------------------------------|----------------------------|
| **A2A Protocol** | ✅ YES | ✅ YES |
| **Multi-Agent Framework** | ✅ YES | ❌ NO |
| **Sandbox Isolation** | ✅ YES (default) | ❌ NO |
| **Multiple Attack Types** | ✅ YES | ❌ SQL only |
| **MITRE Tracking** | ✅ YES | ❌ NO |
| **Cost Optimization** | ✅ YES | ❌ NO |
| **Recommended For** | **PRODUCTION** | Demo/testing |

---

## 🔗 Links

- **Documentation:** [framework/docs/](framework/docs/)
- **Production Architecture:** [ARCHITECTURE_CLARIFICATION.md](framework/docs/ARCHITECTURE_CLARIFICATION.md)
- **Usage Guide:** [green_agents/README.md](green_agents/README.md)
- **Scenarios:**
  - [SQL Injection](scenarios/sql_injection.py)
  - [Prompt Injection](scenarios/prompt_injection.py) - [Design Doc](docs/PROMPT_INJECTION_DESIGN.md)
- **Examples:**
  - [Prompt Injection Demo](examples/prompt_injection_demo.md) - Complete walkthrough

---

## 📧 Support

For questions and support:
- Check the documentation in [framework/docs/](framework/docs/)
- See usage examples in [green_agents/README.md](green_agents/README.md)
- Review the architecture guide in [ARCHITECTURE_CLARIFICATION.md](framework/docs/ARCHITECTURE_CLARIFICATION.md)

---

---

## ✅ Current Status & Features

### What's Working Now

| Component | Status | Tests |
|-----------|--------|-------|
| **Framework Core** | ✅ Working | `test_simple.py` |
| **Attack Generation** | ✅ Working | 52+ attack templates |
| **3 Scenarios** | ✅ Ready | SQL, Prompt, Active Scanning |
| **Direct Evaluation** | ✅ Working | `test_direct_evaluation.py` |
| **A2A Protocol** | ✅ Working | `test_a2a_protocol.sh` |
| **HTTP Server** | ✅ Working | `green_agent_standalone.py` |
| **Multi-Agent Framework** | ✅ Implemented | 7 specialized agents |
| **MITRE ATT&CK Tracking** | ✅ Implemented | T1595 + more |

### Quick Start Commands

```bash
# 1. Install (one-time setup)
python3 -m pip install --user --break-system-packages \
  numpy scipy scikit-learn pydantic python-dotenv httpx agentbeats a2a-sdk

# 2. Verify installation
python3 test_simple.py

# 3. Test evaluation
python3 test_direct_evaluation.py

# 4. Test A2A protocol
bash test_a2a_protocol.sh
```

### Attack Scenarios Available

- **SQL Injection**: 7 techniques (union-based, blind, time-based, etc.) - 12+ templates
- **Prompt Injection**: 7 techniques (jailbreak, prompt leak, role manipulation, etc.) - 32+ templates
- **Active Scanning**: 8 techniques (plugin discovery, API discovery, etc.) - 40+ paths

### Total Coverage

- **22 Attack Techniques** across 3 scenarios
- **52+ Attack Templates** ready to use
- **3 Test Scripts** for local validation
- **7 Specialized Agents** for evaluation
- **A2A Protocol** compliant

---

**Created:** November 2025
**Version:** 2.3
**Status:** ✅ Production Ready + Local Testing Suite
**Framework:** Multi-Agent Security Evaluation with A2A Protocol
