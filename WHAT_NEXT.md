# What to Do Next - Your System is Running!

## ✅ What You Have Running

- **Terminal 1**: Purple Agent (Detector) on `http://127.0.0.1:8000`
- **Terminal 2**: Green Agent (Judge) on `http://127.0.0.1:9010`
- **Both are healthy and responding!** ✓

---

## 🎯 Things You Can Do Right Now

### 1. **Run the Quick Evaluation Test**

```bash
# In Terminal 3
cd /Users/raj/Documents/Projects/SecurityEvaluator
source venv/bin/activate
python test_evaluation.py
```

**What it does:**
- Tests 10 diverse code samples
- Shows detection results (TP, TN, FP, FN)
- Calculates F1, Precision, Recall
- Identifies weak categories
- **Takes ~2 seconds**

**Output you'll see:**
```
Overall Performance:
  • F1 Score:          0.769
  • Precision:         1.000  (No false alarms!)
  • Recall:            0.625  (Caught 5/8 vulnerabilities)

Weak Categories (F1 < 0.6):
  • stored_procedure
  • orm_injection
  • second_order
```

---

### 2. **See Detection Capabilities**

```bash
python demo_detections.py
```

**Shows:**
- What patterns the Purple Agent can detect
- What patterns it recognizes as safe
- Confidence scores for each detection

---

### 3. **Test Your Own Code**

```bash
curl -X POST http://127.0.0.1:8000/detect \
  -H "Content-Type: application/json" \
  -d '{
    "test_case_id": "my_test",
    "code": "YOUR_CODE_HERE",
    "language": "python",
    "category": "classic_sqli"
  }'
```

**Examples to try:**

**Vulnerable:**
```bash
# F-string injection
curl -X POST http://127.0.0.1:8000/detect \
  -H "Content-Type: application/json" \
  -d '{
    "code": "query = f\"SELECT * FROM users WHERE email={email}\"",
    "language": "python",
    "test_case_id": "test1",
    "category": "classic_sqli"
  }'
```

**Secure:**
```bash
# Parameterized query
curl -X POST http://127.0.0.1:8000/detect \
  -H "Content-Type: application/json" \
  -d '{
    "code": "cursor.execute(\"SELECT * FROM users WHERE email=?\", (email,))",
    "language": "python",
    "test_case_id": "test2",
    "category": "classic_sqli"
  }'
```

---

### 4. **View the Agent Cards**

```bash
# Purple Agent info
curl http://127.0.0.1:8000/ | python -m json.tool

# Green Agent card (A2A protocol)
curl http://127.0.0.1:9010/card | python -m json.tool
```

---

### 5. **Run Full Test Suite**

```bash
python -m pytest tests/ -v
```

**Tests:**
- Dataset Manager (7 tests)
- Scoring Engine (8 tests)
- Baseline Detector (10 tests)
- **All 25 should pass!**

---

## 📊 Understanding the Results

### **Metrics Explained:**

| Metric | What It Means | Good Value |
|--------|---------------|------------|
| **F1 Score** | Overall balanced performance | > 0.8 |
| **Precision** | Of all "vulnerable" calls, how many were right? | > 0.9 |
| **Recall** | Of all vulnerabilities, how many did we find? | > 0.8 |
| **FPR** | False alarm rate | < 0.1 |
| **FNR** | Miss rate (dangerous!) | < 0.1 |

### **Confusion Matrix:**

```
                Actually Vulnerable    Actually Secure
Predicted Vuln       TP (Good!)           FP (False Alarm)
Predicted Safe       FN (Missed!)         TN (Good!)
```

**What you want:**
- High TP: Catch real vulnerabilities ✓
- High TN: Don't flag secure code ✓
- Low FP: Minimize false alarms ✓
- Low FN: Don't miss vulnerabilities ✓

---

## 🚀 Advanced: Understanding Adaptive Testing

The system has two modes:

### **Fixed Mode** (Traditional)
```
Sample 100 tests → Execute all → Calculate metrics → Done
```

### **Adaptive Mode** (Intelligent)
```
Round 1: EXPLORATION
├─ Sample 20 diverse tests
├─ Execute and analyze
├─ Identify weak categories (F1 < 0.6)
└─ DECISION: Move to exploitation

Round 2-4: EXPLOITATION
├─ Allocate 60% tests to weak categories
├─ 40% to other categories (maintenance)
├─ Execute and analyze
└─ DECISION: Performance improving

Round 5: VALIDATION
├─ Test with fresh, untested samples
├─ Verify performance is stable
└─ DECISION: Terminate
```

**Why adaptive is better:**
- Finds weak spots automatically
- Focuses testing where needed
- More efficient use of test budget
- Better insights into strengths/weaknesses

---

## 🔧 What You Can Modify

### **1. Add More Test Samples**

Edit `datasets/sql_injection/vulnerable_code/python_sqli.json`:
```json
{
  "language": "python",
  "samples": [
    {
      "id": "your_new_test",
      "category": "classic_sqli",
      "code": "your vulnerable code here",
      "is_vulnerable": true,
      "severity": "critical",
      "description": "What's wrong with it",
      "remediation": "How to fix it"
    }
  ]
}
```

Then restart the Green Agent to reload datasets.

### **2. Improve the Purple Agent**

Edit `purple_agents/baseline/sql_detector.py`:
- Add more patterns to `VULNERABLE_PATTERNS`
- Add more patterns to `SAFE_PATTERNS`
- Improve confidence scoring logic

### **3. Change Evaluation Parameters**

Edit `scenarios/security/config.yaml`:
```yaml
evaluation:
  mode: "adaptive"  # or "fixed"
  test_budget: 100  # Number of tests

adaptive:
  weak_threshold: 0.6      # F1 below this = weak
  focus_percentage: 0.6    # 60% to weak areas
  max_rounds: 5            # Maximum rounds
```

---

## 📖 Understanding the Code

**Want to dive deeper?** See `README_IMPLEMENTATION.md` for:
- Architecture overview
- File-by-file explanations
- Data flow diagrams
- How adaptive testing works
- How to extend the system

**Quick file guide:**
```
scenarios/security/
├── models.py              # All data structures
├── dataset_manager.py     # Loads & samples tests
├── scoring_engine.py      # Calculates metrics
├── adaptive_planner.py    # Makes autonomous decisions
└── sql_injection_judge.py # Main Green Agent

purple_agents/baseline/
└── sql_detector.py        # The detector being tested

datasets/sql_injection/
├── vulnerable_code/       # Vulnerable samples
└── secure_code/           # Secure samples
```

---

## 🎯 Next Steps

1. **Explore the test samples**: Look at `datasets/sql_injection/*.json`
2. **Try the evaluation test**: `python test_evaluation.py`
3. **Check the code**: Read through the implementations
4. **Add more samples**: Expand the dataset
5. **Improve the detector**: Make the Purple Agent smarter

---

## ❓ Common Questions

**Q: How do I stop the servers?**
A: Press `Ctrl+C` in each terminal

**Q: Can I change the ports?**
A: Yes! Use `--port` flag when starting:
```bash
python purple_agents/baseline/sql_detector.py --port 8001
python scenarios/security/sql_injection_judge.py --port 9011
```

**Q: Where are the logs?**
A: In the terminal output of each running server

**Q: How do I add more languages?**
A: Add `javascript_sqli.json`, `java_sqli.json`, etc. to datasets, then update the Purple Agent patterns

**Q: Can I use this with real Purple Agents?**
A: Yes! Any Purple Agent that implements the A2A protocol can be evaluated

---

## 🆘 Troubleshooting

**Purple Agent not responding:**
```bash
# Check if it's running
curl http://127.0.0.1:8000/health

# Check logs in Terminal 1
```

**Green Agent not starting:**
```bash
# Check if port is in use
lsof -i :9010

# Try a different port
python scenarios/security/sql_injection_judge.py --port 9011
```

**Import errors:**
```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall if needed
pip install -e .
```

---

## ✨ Summary

You now have a fully functional SQL injection detection evaluation system!

**What it can do:**
- ✅ Evaluate security detectors automatically
- ✅ Calculate comprehensive metrics
- ✅ Identify weak categories
- ✅ Adapt testing strategy autonomously
- ✅ Provide detailed reports

**What you learned:**
- How the Green Agent evaluates Purple Agents
- How metrics like F1, Precision, Recall work
- How adaptive testing finds weak spots
- How the A2A protocol enables agent communication

**Ready to contribute to AgentBeats Phase 1!** 🚀
