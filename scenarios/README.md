# ⚠️ DEPRECATED - Legacy Scenarios

**This directory contains legacy code and is deprecated.**

## Migration Notice

All scenarios have been moved to the centralized location:

```
/framework/scenarios/  ← NEW centralized location for ALL scenarios
```

## What's Here

### `/scenarios/security/` - Legacy SQLInjectionJudge

This is the **original SQLInjectionJudge** implementation (Green Agent v1.0).

**Status:** Deprecated - kept only for backwards compatibility with existing tests

**Files:**
- `sql_injection_judge.py` - Original Green Agent implementation
- `dataset_manager.py` - Dataset handling
- `scoring_engine.py` - Metrics calculation
- `models.py` - Data models
- `adaptive_planner.py` - Test allocation
- `llm_judge.py` - LLM-based judging

**Migration Path:**
- **For new projects:** Use `/framework/scenarios/sql_injection.py`
- **For existing tests:** These still reference `scenarios.security.*`
  - Will be migrated in future cleanup

## New Centralized Location

**All new scenarios should go in:**

```
/framework/scenarios/
├── sql_injection.py       ← SQL Injection (complete)
├── prompt_injection.py    ← Prompt Injection (complete)
│
├── web_attacks/           ← Future: XSS, CSRF, etc.
├── network_attacks/       ← Future: DDoS, Port Scanning, etc.
└── mitre/                 ← Future: 200+ MITRE ATT&CK scenarios
```

## Why the Change?

1. **Centralization:** One location for all scenarios
2. **Scalability:** Better organization for 100+ MITRE scenarios
3. **Consistency:** All scenarios follow SecurityScenario interface
4. **Modularity:** Clear separation from legacy code

## For Developers

**Adding a new scenario:**
```bash
# Add to the centralized location
touch framework/scenarios/xss.py

# NOT here in /scenarios/
```

**See documentation:**
- `/framework/scenarios/README.md` - Scenario structure guide
- `/framework/docs/FUTURE_IMPROVEMENTS.md` - How to add scenarios
- `/framework/docs/SCALABILITY_GUIDE.md` - Multi-attack scalability

---

**Last Updated:** 2025-11-09
**Migration Status:** In Progress
