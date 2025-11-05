# Quick Start Guide - Running Locally

## ✅ Prerequisites

Make sure you have the virtual environment set up:
```bash
cd /Users/raj/Documents/Projects/SecurityEvaluator
source venv/bin/activate
```

---

## 🚀 Option 1: Run Full System (Two Terminals)

### Terminal 1: Purple Agent (Detector)
```bash
cd /Users/raj/Documents/Projects/SecurityEvaluator
source venv/bin/activate
python purple_agents/baseline/sql_detector.py --host 127.0.0.1 --port 8000
```

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Terminal 2: Green Agent (Judge)
```bash
cd /Users/raj/Documents/Projects/SecurityEvaluator
source venv/bin/activate
python scenarios/security/sql_injection_judge.py --host 127.0.0.1 --port 9010 --dataset-root datasets/sql_injection
```

**Expected output:**
```
INFO - Loading datasets...
INFO - Loaded 27 samples across 1 languages
INFO - Categories: ['classic_sqli', 'blind_sqli', 'union_based', ...]
INFO - Vulnerable: 12, Secure: 15
INFO - Starting SQL Injection Judge on 127.0.0.1:9010
INFO:     Uvicorn running on http://127.0.0.1:9010 (Press CTRL+C to quit)
```

---

## 🧪 Option 2: Quick Test (Just Run Tests)

If you just want to verify everything works without running servers:

```bash
cd /Users/raj/Documents/Projects/SecurityEvaluator
source venv/bin/activate
python -m pytest tests/ -v
```

**Expected output:**
```
========================= 25 passed, 1 warning in 0.24s =========================
```

---

## 🔍 Option 3: Test Purple Agent Manually

With Purple Agent running (Terminal 1), test it with curl in Terminal 3:

```bash
# Test 1: Vulnerable code (should detect it)
curl -X POST http://127.0.0.1:8000/detect \
  -H "Content-Type: application/json" \
  -d '{
    "test_case_id": "test_001",
    "code": "query = f\"SELECT * FROM users WHERE id={user_id}\"",
    "language": "python",
    "category": "classic_sqli"
  }'
```

**Expected response:**
```json
{
  "test_case_id": "test_001",
  "is_vulnerable": true,
  "confidence": 0.95,
  "vulnerability_type": "SQL Injection",
  "explanation": "Detected 1 potential SQL injection(s): f-string SQL interpolation",
  "detected_patterns": ["f[\"'].*SELECT.*\\{.*\\}"],
  "line_numbers": [],
  "severity": "critical"
}
```

```bash
# Test 2: Secure code (should say it's safe)
curl -X POST http://127.0.0.1:8000/detect \
  -H "Content-Type: application/json" \
  -d '{
    "test_case_id": "test_002",
    "code": "cursor.execute(\"SELECT * FROM users WHERE id=?\", (user_id,))",
    "language": "python",
    "category": "classic_sqli"
  }'
```

**Expected response:**
```json
{
  "test_case_id": "test_002",
  "is_vulnerable": false,
  "confidence": 0.8,
  "vulnerability_type": null,
  "explanation": "Code uses parameterized queries or ORM safe methods",
  "detected_patterns": ["parameterized_query"],
  "line_numbers": [],
  "severity": null
}
```

---

## 📊 Check Agent Cards

### Purple Agent Card
```bash
curl http://127.0.0.1:8000/
```

### Green Agent Card
```bash
curl http://127.0.0.1:9010/card
```

---

## 🛑 Stopping the Servers

Press `Ctrl+C` in each terminal running a server.

---

## ❓ Troubleshooting

### Port Already in Use
If you get "Address already in use" errors:

```bash
# Check what's using the port
lsof -i :8000  # or :9010

# Kill the process
kill -9 <PID>
```

### Import Errors
Make sure virtual environment is activated:
```bash
source venv/bin/activate
```

### Missing Dependencies
Reinstall if needed:
```bash
pip install -e .
```

---

## 📝 What Each Component Does

- **Purple Agent (port 8000)**: The security detector being tested. Analyzes code for SQL injection.
- **Green Agent (port 9010)**: The evaluation system. Tests the Purple Agent and calculates metrics.
- **Datasets**: 27 code samples (12 vulnerable + 15 secure) used for testing.

---

## 🎯 Next Steps

Once both servers are running:
1. The Green Agent can evaluate the Purple Agent via A2A protocol
2. Check logs to see evaluation progress
3. View metrics and autonomous decisions in the results

For programmatic evaluation, you would send requests to the Green Agent endpoint according to the A2A protocol specification.
