# What is Called When `/card` is Invoked?

**Quick Answer:** An **AgentCard** is returned - it's the A2A protocol's way of describing what the agent can do.

---

## 📋 Simple Explanation

**Request:**
```bash
curl http://127.0.0.1:9010/card
```

**Returns:** **AgentCard** (JSON document)

**What it's called:**
- Technical name: **AgentCard**
- Protocol: **A2A (Agent-to-Agent)**
- Purpose: **Capability Discovery**

Think of it like a **business card** for your AI agent - it tells others:
- Who the agent is
- What it can do
- How to use it
- What skills it has

---

## ✅ Has It Been Enhanced for the New Framework?

**YES! ✅ Fully Enhanced**

### What We Enhanced

#### 1. **Description Now Lists All 7 Agents**
```
Before: "Uses advanced multi-agent framework"
After:  "Uses 7-agent framework: BoundaryProber (Thompson Sampling),
         Exploiter, Mutator (Novelty Search), Validator, Perspective,
         LLMJudge (Dawid-Skene), Counterfactual"
```

#### 2. **Tags Expanded: 14 → 26 Tags**
```
NEW Tags Added:
- prompt-injection
- llm-security
- jailbreak-detection
- multi-agent-system
- unified-ecosystem
- meta-orchestrator
- thompson-sampling
- novelty-search
- dawid-skene-consensus
- counterfactual-analysis
- purple-team
- security-benchmarking
```

#### 3. **Examples Show Both Scenarios**
```
Example 1: SQL injection evaluation
Example 2: Prompt injection evaluation (NEW!)
```

#### 4. **Framework Components Named**
```
Now explicitly mentions:
- UnifiedEcosystem
- MetaOrchestrator
- All 7 specialized agents
- Specific techniques (Thompson Sampling, Novelty Search, Dawid-Skene)
```

#### 5. **Production Features Detailed**
```
Now includes:
- Docker sandbox isolation
- MITRE ATT&CK coverage tracking
- Cost-optimized LLM routing (30-60% savings)
- Comprehensive metrics (F1, Precision, Recall, evasions)
```

---

## 📊 Before vs After

### Before (Generic)
```json
{
  "name": "Cyber Security Evaluator",
  "description": "Evaluates security detectors",
  "tags": ["security", "vulnerability-detection", "benchmark"],
  "examples": ["..."]
}
```

### After (✅ Enhanced!)
```json
{
  "name": "Cyber Security Evaluator",
  "description": "Production Green Agent with 7-agent UnifiedEcosystem framework. Evaluates security detectors (Purple Agents) using MetaOrchestrator-coordinated coalitions: BoundaryProber (Thompson Sampling for weak areas), Exploiter (hybrid attack generation), Mutator (Novelty Search for evasion discovery), Validator (quality assurance), Perspective (multi-viewpoint analysis), LLMJudge (Dawid-Skene consensus), Counterfactual (remediation suggestions). Supports SQL injection, prompt injection (jailbreak/LLM security), and extensible to XSS, command injection, etc. Production-ready: Docker sandbox, MITRE ATT&CK tracking, cost-optimized LLM routing. A2A protocol compliant for AgentBeats integration.",
  "tags": [
    "sql-injection",
    "prompt-injection",
    "llm-security",
    "jailbreak-detection",
    "multi-agent-system",
    "unified-ecosystem",
    "meta-orchestrator",
    "thompson-sampling",
    "novelty-search",
    "dawid-skene-consensus",
    "counterfactual-analysis",
    ...
  ],
  "examples": [
    "SQL injection evaluation",
    "Prompt injection evaluation"
  ]
}
```

---

## 🎯 Why This Matters

### For AgentBeats Platform
- **Discovery**: Users can find your agent by searching "thompson-sampling" or "novelty-search"
- **Understanding**: Users immediately see it's a 7-agent framework
- **Trust**: Production features (Docker sandbox, cost optimization) build confidence

### For Integration
- **API Clients**: Know exactly what the agent can do
- **Other Agents**: Can discover and invoke your agent
- **Developers**: See complete capability list before integrating

### For Documentation
- **Self-Documenting**: AgentCard serves as live documentation
- **Always Accurate**: Updated with the code, never out of sync
- **Standardized**: Follows A2A protocol standard

---

## 🔍 See It Yourself

```bash
# Start Green Agent
python green_agents/cybersecurity_evaluator.py --port 9010

# Get enhanced AgentCard
curl http://127.0.0.1:9010/card | jq

# Check it mentions all 7 agents
curl http://127.0.0.1:9010/card | jq '.skills[0].description' | grep -o "BoundaryProber\|Exploiter\|Mutator\|Validator\|Perspective\|LLMJudge\|Counterfactual"

# Check it mentions both scenarios
curl http://127.0.0.1:9010/card | jq '.skills[0].tags' | grep -o "sql-injection\|prompt-injection"
```

---

## 📚 Complete Details

For complete technical details, see:
- **[AGENTCARD_EXPLAINED.md](AGENTCARD_EXPLAINED.md)** - Comprehensive explanation
- **[examples/verify_agentcard.md](../examples/verify_agentcard.md)** - Verification guide
- **Code**: `green_agents/agent_card.py`

---

## ✅ Summary

**What `/card` returns:** **AgentCard** (A2A protocol capability document)

**Is it enhanced?** **YES! ✅**
- Lists all 7 agents by name
- Mentions specific techniques (Thompson Sampling, Novelty Search, Dawid-Skene)
- Shows both scenarios (SQL injection, prompt injection)
- Details production features (Docker sandbox, cost optimization)
- Expanded tags for better discoverability (14 → 26 tags)

**Status:** Fully enhanced and production-ready! 🎉
