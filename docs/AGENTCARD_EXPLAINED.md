# AgentCard Explained - What `/card` Returns

**Last Updated:** November 2025
**Status:** ✅ Enhanced for Advanced Framework

---

## 📋 What is an AgentCard?

When you call `GET /card`, the Green Agent returns an **AgentCard** - a standardized A2A (Agent-to-Agent) protocol document.

**Purpose:**
- Describes agent capabilities for discovery
- Enables AgentBeats platform integration
- Provides usage examples
- Lists supported skills and tags

**Standard:** A2A Protocol (AgentBeats)

---

## 🔍 What's Returned When `/card` is Called

### Request
```bash
curl http://127.0.0.1:9010/card
```

### Response Structure
```json
{
  "name": "Cyber Security Evaluator",
  "description": "...",
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
      "description": "...",
      "tags": [...],
      "examples": [...]
    }
  ]
}
```

---

## ✨ Enhanced Description (NEW!)

### Before (Generic)
```
"Evaluates Purple Agents on their ability to detect cybersecurity
vulnerabilities across multiple attack types and techniques."
```

### After (Detailed - ✅ Enhanced!)
```
"Evaluates Purple Agents (security detectors) using an advanced
7-agent framework with UnifiedEcosystem.

Specialized agents:
- BoundaryProber (Thompson Sampling)
- Exploiter (hybrid attack generation)
- Mutator (Novelty Search evolution)
- Validator (syntax/semantic checks)
- Perspective (multi-viewpoint analysis)
- LLMJudge (Dawid-Skene consensus)
- Counterfactual (remediation suggestions)

MetaOrchestrator coordinates coalition-based attack generation
with adaptive testing.

Supports multiple scenarios: SQL injection, prompt injection
(jailbreak/LLM security), and more.

Production features: Docker sandbox isolation, MITRE ATT&CK
coverage tracking, cost-optimized LLM routing (30-60% savings).

Returns comprehensive metrics: F1/Precision/Recall, evasion
analysis, and counterfactual fixes."
```

**What's NEW:**
✅ Lists all 7 specialized agents by name
✅ Explains specific techniques (Thompson Sampling, Novelty Search, Dawid-Skene)
✅ Mentions UnifiedEcosystem and MetaOrchestrator
✅ Details production features (Docker sandbox, cost optimization)
✅ Describes output metrics (F1, evasions, counterfactuals)
✅ Lists supported scenarios (SQL injection, prompt injection)

---

## 🏷️ Enhanced Tags (NEW!)

### Before (14 tags)
```json
[
  "security",
  "vulnerability-detection",
  "benchmark",
  "sql-injection",
  "xss",
  "command-injection",
  "mitre-attack",
  "adaptive-testing",
  "red-team"
]
```

### After (26 tags - ✅ Enhanced!)
```json
{
  "tags": [
    // Attack Types
    "security",
    "vulnerability-detection",
    "benchmark",
    "sql-injection",
    "prompt-injection",           // ← NEW
    "llm-security",               // ← NEW
    "jailbreak-detection",        // ← NEW
    "xss",
    "command-injection",

    // Framework & Architecture
    "multi-agent-system",         // ← NEW
    "unified-ecosystem",          // ← NEW
    "meta-orchestrator",          // ← NEW
    "coalition-based",            // ← NEW
    "7-agent-framework",          // ← NEW

    // Advanced Techniques
    "thompson-sampling",          // ← NEW
    "novelty-search",             // ← NEW
    "dawid-skene-consensus",      // ← NEW
    "adaptive-testing",
    "evasion-detection",          // ← NEW
    "counterfactual-analysis",    // ← NEW

    // Standards & Compliance
    "mitre-attack",
    "owasp-top-10",               // ← NEW
    "a2a-protocol",               // ← NEW

    // Use Cases
    "red-team",
    "purple-team",                // ← NEW
    "security-benchmarking"       // ← NEW
  ]
}
```

**Benefits:**
- Better discoverability in AgentBeats platform
- Searchable by technique (thompson-sampling, novelty-search)
- Searchable by framework (unified-ecosystem, meta-orchestrator)
- Searchable by attack type (prompt-injection, llm-security)

---

## 📚 Skills Section

### Skill: cybersecurity_evaluation

**What it describes:**
- The evaluation capability the Green Agent provides
- How it works (7 agents, MetaOrchestrator, etc.)
- What scenarios it supports
- What production features are available
- Example requests

**Structure:**
```json
{
  "id": "cybersecurity_evaluation",
  "name": "Cyber Security Detection Evaluation",
  "description": "Detailed explanation of 7-agent framework...",
  "tags": ["thompson-sampling", "novelty-search", ...],
  "examples": [
    "Example 1: SQL injection evaluation",
    "Example 2: Prompt injection evaluation"
  ]
}
```

---

## 📝 Usage Examples in AgentCard

### Example 1: SQL Injection Evaluation
```json
{
  "purple_agent_id": "my_sql_injection_detector",
  "purple_agent_endpoint": "http://127.0.0.1:8000",
  "config": {
    "scenario": "sql_injection",
    "max_rounds": 10,
    "budget_usd": 50.0,
    "use_sandbox": true,
    "use_cost_optimization": true,
    "use_coverage_tracking": true,
    "num_boundary_probers": 2,
    "num_exploiters": 3,
    "num_mutators": 2
  }
}
```

### Example 2: Prompt Injection Evaluation (NEW!)
```json
{
  "purple_agent_id": "my_prompt_injection_detector",
  "purple_agent_endpoint": "http://127.0.0.1:8000",
  "config": {
    "scenario": "prompt_injection",
    "max_rounds": 10,
    "budget_usd": 50.0,
    "use_sandbox": true,
    "use_cost_optimization": true,
    "use_coverage_tracking": true
  }
}
```

**Shows:**
- How to select different scenarios
- Configuration options available
- Agent coalition sizing (num_boundary_probers, num_exploiters, etc.)
- Production features (sandbox, cost optimization, coverage tracking)

---

## 🎯 What Makes This AgentCard Enhanced?

| Feature | Before | After | Status |
|---------|--------|-------|--------|
| **Description Depth** | Generic "multi-agent framework" | Lists all 7 agents by name + techniques | ✅ Enhanced |
| **Scenario Support** | Implied multiple | Explicitly lists: SQL injection, prompt injection | ✅ Enhanced |
| **Agent Details** | Not mentioned | Thompson Sampling, Novelty Search, Dawid-Skene | ✅ Enhanced |
| **Framework Names** | "framework" | UnifiedEcosystem, MetaOrchestrator | ✅ Enhanced |
| **Production Features** | Basic mention | Docker sandbox, cost optimization (30-60% savings) | ✅ Enhanced |
| **Output Metrics** | "comprehensive metrics" | F1/Precision/Recall, evasions, counterfactuals | ✅ Enhanced |
| **Tags Count** | 14 tags | 26 tags (categorized) | ✅ Enhanced |
| **Discoverability** | Basic | Searchable by technique, framework, attack type | ✅ Enhanced |
| **Examples** | 1 example | 2 examples (SQL + prompt injection) | ✅ Enhanced |

---

## 🔍 How Clients Use the AgentCard

### 1. Discovery (AgentBeats Platform)
```
User searches: "thompson-sampling"
→ Finds: Cyber Security Evaluator
→ Sees: Uses Thompson Sampling for boundary probing
→ Understands: Advanced 7-agent framework
```

### 2. Capability Check
```
Client: What can this agent do?
AgentCard: Evaluates security detectors with 7-agent framework
Client: What scenarios?
AgentCard: SQL injection, prompt injection, etc.
Client: What techniques?
AgentCard: Thompson Sampling, Novelty Search, Dawid-Skene
```

### 3. Usage Example
```
Client: How do I use this?
AgentCard: Here's an example for SQL injection
AgentCard: Here's an example for prompt injection
Client: *Uses example as template*
```

---

## 📊 Comparison: Generic vs Enhanced AgentCard

### Generic AgentCard (Before)
```json
{
  "name": "Security Evaluator",
  "description": "Evaluates security detectors",
  "tags": ["security", "testing"],
  "examples": ["..."]
}
```

**Problems:**
❌ No framework details
❌ No technique names
❌ No scenario list
❌ Limited discoverability

### Enhanced AgentCard (After - ✅)
```json
{
  "name": "Cyber Security Evaluator",
  "description": "7-agent framework with UnifiedEcosystem. BoundaryProber (Thompson Sampling), Exploiter, Mutator (Novelty Search), Validator, Perspective, LLMJudge (Dawid-Skene), Counterfactual. MetaOrchestrator coordination. SQL injection, prompt injection support...",
  "tags": [
    "7-agent-framework",
    "thompson-sampling",
    "novelty-search",
    "dawid-skene-consensus",
    "sql-injection",
    "prompt-injection",
    ...
  ],
  "examples": [
    "SQL injection evaluation",
    "Prompt injection evaluation"
  ]
}
```

**Benefits:**
✅ Complete framework description
✅ All 7 agents named with techniques
✅ Scenarios explicitly listed
✅ Highly discoverable
✅ Production features detailed

---

## 🚀 Try It Yourself

### Step 1: Start Green Agent
```bash
python green_agents/cybersecurity_evaluator.py --port 9010
```

### Step 2: Get Enhanced AgentCard
```bash
curl http://127.0.0.1:9010/card | jq
```

### Step 3: Check Enhanced Features
```bash
# Check description mentions all 7 agents
curl http://127.0.0.1:9010/card | jq '.skills[0].description'

# Check tags include advanced techniques
curl http://127.0.0.1:9010/card | jq '.skills[0].tags'

# Check examples show both scenarios
curl http://127.0.0.1:9010/card | jq '.skills[0].examples'
```

---

## 📝 Summary

**When `/card` is Called:**
- Returns: **AgentCard** (A2A protocol standard)
- Contains: Agent capabilities, skills, tags, examples
- Status: **✅ ENHANCED** for advanced framework

**Enhancements Made:**
1. ✅ Description lists all 7 agents + techniques
2. ✅ Tags expanded to 26 (framework, techniques, scenarios)
3. ✅ Examples show both SQL injection and prompt injection
4. ✅ Production features explicitly mentioned
5. ✅ Output metrics detailed (F1, evasions, counterfactuals)

**Result:**
The AgentCard now properly advertises the **advanced 7-agent framework with UnifiedEcosystem**, making it highly discoverable and informative for potential users! 🎉

---

## 🔗 See Also

- **AgentCard Source**: `green_agents/agent_card.py`
- **A2A Protocol**: AgentBeats documentation
- **Verification Guide**: `examples/verify_agentcard.md`
