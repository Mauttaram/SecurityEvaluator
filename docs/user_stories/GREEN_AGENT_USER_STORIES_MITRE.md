# Green Agent User Stories (MITRE/ATLAS Integrated)

Product: SecurityEvaluator – Green Agent (Security Evaluator)
Version: 1.1 (MITRE/ATLAS Integrated)
Date: November 2025
Audience: Competition Participants, Security Researchers, AI Safety Evaluators

---

## Executive Summary

This document focuses on the implemented pipeline that powers the Green Agent’s MITRE-driven evaluation:
1) Profile Purple Agent → 2) Select MITRE ATT&CK + ATLAS TTPs dynamically → 3) Generate attack payloads (template-first, LLM optional) → 4) Execute and record → 5) Dual-score Green and Purple perspectives → 6) Track coverage.

Backed by code:
- Profiler: `framework/profiler.py:AgentProfiler`
- TTP Selection: `framework/mitre/ttp_selector.py:MITRETTPSelector`
- Payloads: `framework/mitre/payload_generator.py:PayloadGenerator`
- Scenario wiring: `framework/scenarios/comprehensive_security.py`
- Agents: `framework/agents/boundary_prober.py`, `framework/agents/exploiter.py`
- Dual Scoring: `framework/scoring/dual_scoring_engine.py`

---

## End-to-End Workflow (Contract)

Inputs:
- Purple Agent endpoint (A2A agent card)
- Scenario + MITRE config (TOML)

Process:
- Profile → Dynamic TTP selection (ATT&CK + ATLAS, weighted) → Payload generation → Attack execution → Scoring + Coverage.

Outputs:
- Green metrics (F1, precision, recall, cost)
- Purple assessment (security score, risk, vulnerabilities)
- Coverage summary (techniques, categories)
- Reports (markdown + JSON)

Edge cases:
- No agent card → fallback profile
- No matching TTPs → generic techniques
- Template miss → generic payloads or LLM (if enabled)

---

## Story G1: Purple Agent Profiling (A2A)
As a Green Agent
I want to derive an actionable agent profile from the A2A agent card
So that I can select relevant TTPs and generate context-specific payloads.

Acceptance Criteria:
- Fetch `/.well-known/agent-card.json` (timeout + retry)
- Extract name, version, skills, capabilities
- Infer `is_ai_agent`, platforms, likely attack surface
- Persist profile for downstream steps

Implementation references:
- `framework/profiler.py:AgentProfiler`
- Tests: `tests/test_end_to_end_full.py` (phase: profiling)

---

## Story G2: Dynamic TTP Selection (ATT&CK + ATLAS)
As a Green Agent
I want to select MITRE techniques dynamically from ATT&CK and ATLAS
So that the attack plan matches the target’s profile and domain.

Acceptance Criteria:
- Use `MITRETTPSelector.select_techniques_for_profile(agent_profile, max_techniques)`
- Weight ATLAS higher for AI/automation agents (configurable)
- Return techniques with `selection_score`, `source` (atlas/attack), `tactics`, `platforms`
- Store selection in knowledge base for other agents (e.g., Exploiter)

Implementation references:
- `framework/mitre/ttp_selector.py:MITRETTPSelector`
- BoundaryProber integration stores selected TTPs
- Examples: `tests/test_final_comprehensive.py` (Phases 1–2)

---

## Story G3: Payload Generation (Template-first, LLM-optional)
As a Green Agent
I want to generate concrete attack payloads from selected TTPs
So that I can test the Purple Agent with realistic, labeled inputs.

Acceptance Criteria:
- Generate N payloads per technique using `PayloadGenerator`
- Prefer templates when available; fallback to generic; use LLM if enabled
- Add optional benign controls for FP measurement
- Emit `AttackPayload` with fields: `technique_id`, `technique_name`, `category`, `severity`, `platform`, `payload`, `is_malicious`

Implementation references:
- `framework/mitre/payload_generator.py:PayloadGenerator`
- Scenario wiring: `framework/scenarios/comprehensive_security.py`
- Exploiter path: `framework/agents/exploiter.py::_generate_from_mitre`

---

## Story G4: Attack Conversion and Execution
As a Green Agent
I want to convert payloads to framework `Attack` objects and execute
So that results and telemetry can be scored and reported.

Acceptance Criteria:
- Map `AttackPayload` → `Attack` with MITRE metadata preserved
- Execute via scenario runner; record responses and timings
- Persist interactions and outcomes

Implementation references:
- `framework/scenarios/comprehensive_security.py`
- `framework/models.py` (Attack, TestResult)
- Tests: `tests/test_end_to_end_full.py` (payload → interaction)

---

## Story G5: Dual Scoring (Green + Purple)
As a competition participant
I want dual-perspective scoring
So that I understand attacker effectiveness and defender posture.

Acceptance Criteria:
- Compute Green metrics: TP/FP/FN/TN, precision, recall, F1, cost
- Compute Purple assessment: security score, risk level, vulnerability counts
- Produce unified result via `DualScoringEngine.evaluate(...)`
- Include MITRE coverage summary if enabled

Implementation references:
- `framework/scoring/dual_scoring_engine.py`
- `framework/scoring/greenagent_scoring_engine.py`
- `framework/scoring/purpleagent_scoring_engine.py`

---

## Story G6: Coverage Tracking (MITRE)
As a security analyst
I want technique coverage tracked from MITRE metadata
So that I can identify testing gaps and priorities.

Acceptance Criteria:
- Extract technique ids from `attack.metadata['mitre_technique_id']`
- Summarize covered/remaining techniques
- Surface in reports when enabled

Implementation references:
- Coverage tracker integration (fixed to read metadata)
- Usage in LLM scenario: `home_automation_eval_llm.toml`

---

## Minimal Configuration (TOML)

```toml
[mitre]
enabled = true
auto_download = true
refresh_interval_hours = 168
use_bundled_fallback = true

[mitre.ttp_selection]
max_techniques = 25
include_atlas = true
include_attack = true
atlas_weight = 0.7
attack_weight = 0.3

[mitre.agent_profile]
mark_as_ai_agent = true
agent_type = "ai-automation"

[mitre.payload_generation]
payloads_per_technique = 2
include_benign_controls = true
benign_count = 3
```

---

## Example Flow (Backed by Tests)

1) Profile: `AgentProfiler` fetches agent card (HomeAutomationAgent)
2) Select TTPs: `MITRETTPSelector` returns mixed ATT&CK/ATLAS with scores
3) Generate payloads: `PayloadGenerator` creates template-based payloads, adds benign
4) Execute: Scenario runs attacks, records outcomes
5) Dual Score: `DualScoringEngine` produces Green/Purple results
6) Coverage: Techniques summarized from metadata

Evidence:
- `tests/test_final_comprehensive.py` (Phases 1–3 + scoring)
- `tests/test_end_to_end_full.py` (end-to-end with logs)
- `framework/scenarios/comprehensive_security.py` (wiring)

---

## Output Examples (From Recent Runs)

Green Agent (No LLM):
- F1: ~0.78, Precision: ~0.91, Recall: ~0.68
- Competition Score: ~75.6/100 (Grade C)

Purple Agent (No LLM):
- Security Score: ~68.5/100
- Risk Level: HIGH
- Vulnerabilities: 69 (High)

LLM Variant (With Coverage):
- F1: ~0.70, Precision: ~0.93, Recall: ~0.56
- Coverage: 3/7 techniques (42.9%) → AML.T0056, T1553.001, BENIGN

---

## Links to Code
- Profiler: `framework/profiler.py`
- Selector: `framework/mitre/ttp_selector.py`
- Payloads: `framework/mitre/payload_generator.py`
- Boundary Prober: `framework/agents/boundary_prober.py`
- Exploiter: `framework/agents/exploiter.py`
- Scenario: `framework/scenarios/comprehensive_security.py`
- Scoring: `framework/scoring/dual_scoring_engine.py`

---

Last Updated: November 15, 2025
Status: ✅ Aligned with current implementation
