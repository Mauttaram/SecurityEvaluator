# SQL Injection Detection - LLM as Judge

An advanced evaluation framework that uses Large Language Models (LLMs) to provide qualitative assessment of security detection tools, going beyond simple binary classification to evaluate explanation quality, technical correctness, and actionability.

---

## 🎯 Overview

Traditional security benchmarks evaluate tools on **what** they detect (accuracy, F1 score). The LLM Judge evaluates **how well** they explain their findings - critical for real-world security tools where developers need clear, actionable guidance.

### Why LLM as Judge?

**Traditional Binary Judge:**
- ✅ Did you detect the vulnerability? (YES/NO)
- Metrics: Precision, Recall, F1 Score

**LLM Judge:**
- ✅ Did you detect the vulnerability? (YES/NO)
- 📊 How clear is your explanation? (0.0-1.0)
- 🔬 How technically correct is your analysis? (0.0-1.0)
- 🛠️ How actionable are your recommendations? (0.0-1.0)
- ✨ How complete is your coverage? (0.0-1.0)

---

## 🚀 Key Features

### Multi-Dimensional Evaluation

The LLM Judge scores purple agents on **5 criteria**:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Vulnerability Detection Accuracy** | 40% | Correctly identified vulnerable/secure code |
| **Technical Correctness** | 25% | Accurate technical details and reasoning |
| **Explanation Quality** | 20% | Clear, well-structured, helpful explanations |
| **Actionability** | 10% | Provides actionable insights for fixing issues |
| **Completeness** | 5% | Identifies all relevant aspects of vulnerabilities |

### Multi-Provider Support

Choose your preferred LLM provider:

- **🤖 Anthropic** - Claude 3.5 Sonnet (default)
- **🧠 OpenAI** - GPT-4 Turbo
- **🔷 Google** - Gemini Pro

### Comprehensive Metrics

Get both traditional and quality metrics:

```json
{
  "f1_score": 0.87,
  "precision": 0.89,
  "recall": 0.85,
  "average_llm_score": 0.82,
  "average_explanation_quality": 0.78,
  "average_technical_correctness": 0.85,
  "average_actionability": 0.73
}
```

### Detailed Feedback

For each test case, receive:
- **Overall Score** (0.0-1.0)
- **Criterion Breakdown** (5 separate scores)
- **Reasoning** (LLM's detailed analysis)
- **Identified Issues** (Problems in the analysis)
- **Strengths** (What the agent did well)
- **Confidence** (LLM's confidence in judgment)

---

## 📋 Prerequisites

### API Keys

You need an API key for your chosen LLM provider:

```bash
# Anthropic (default)
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenAI
export OPENAI_API_KEY="sk-..."

# Google
export GOOGLE_API_KEY="..."
```

### Dependencies

```bash
# Install required packages
uv sync

# Or with pip
pip install httpx pydantic agentbeats anthropic openai google-generativeai
```

### Dataset

Ensure you have the SQL injection dataset:

```
scenarios/security/datasets/sql_injection/
├── metadata.json
├── vulnerable_code/
│   ├── python_sqli.json
│   ├── javascript_sqli.json
│   └── ...
└── secure_code/
    ├── python_secure.json
    └── ...
```

---

## 🎮 Usage

### Basic Usage

**Start the LLM Judge server:**

```bash
python scenarios/security/llm_judge.py \
  --host 127.0.0.1 \
  --port 9011 \
  --dataset-root datasets/sql_injection
```

This uses **Anthropic Claude 3.5 Sonnet** by default.

### Using Different LLM Providers

**OpenAI GPT-4:**

```bash
python scenarios/security/llm_judge.py \
  --port 9011 \
  --llm-provider openai \
  --llm-model gpt-4-turbo-preview \
  --api-key sk-your-openai-key
```

**Google Gemini:**

```bash
python scenarios/security/llm_judge.py \
  --port 9011 \
  --llm-provider google \
  --llm-model gemini-1.5-pro
```

**Anthropic Claude (explicit):**

```bash
python scenarios/security/llm_judge.py \
  --port 9011 \
  --llm-provider anthropic \
  --llm-model claude-3-5-sonnet-20241022
```

### With Cloudflare Tunnel

Make your judge publicly accessible:

```bash
python scenarios/security/llm_judge.py \
  --port 9011 \
  --cloudflare-quick-tunnel
```

### Command-Line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--host` | 127.0.0.1 | Host to bind to |
| `--port` | 9011 | Port to bind to |
| `--dataset-root` | datasets/sql_injection | Path to dataset directory |
| `--llm-provider` | anthropic | LLM provider (anthropic/openai/google) |
| `--llm-model` | (auto) | Model name (auto-selected per provider) |
| `--api-key` | (env) | API key (or use environment variable) |
| `--card-url` | (auto) | External URL for agent card |
| `--cloudflare-quick-tunnel` | false | Use Cloudflare tunnel |

---

## 🔧 Configuration

### Evaluation Request

Send evaluation requests via A2A protocol:

```json
{
  "purple_agent_id": "my-sql-detector",
  "purple_agent_endpoint": "http://localhost:9019/analyze",
  "config": {
    "test_budget": 50,
    "timeout_seconds": 600,
    "per_test_timeout_seconds": 30.0,
    "random_seed": 42,
    "categories": ["classic_sqli", "blind_sqli"],
    "languages": ["python", "javascript"]
  }
}
```

### LLM Judge Configuration

Customize LLM behavior:

```python
from llm_judge import LLMJudgeConfig, LLMProvider

config = LLMJudgeConfig(
    provider=LLMProvider.ANTHROPIC,
    model="claude-3-5-sonnet-20241022",
    temperature=0.1,  # Lower = more deterministic
    max_tokens=2000,  # Max response length
    judge_timeout=30.0  # Timeout per LLM call
)
```

### Budget Considerations

**Default test budget: 50** (vs 100 for binary judge)

Why smaller? LLM judge is more expensive:

| Provider | Cost per Test | 50 Tests | 100 Tests |
|----------|---------------|----------|-----------|
| **Anthropic Claude** | ~$0.02 | ~$1.00 | ~$2.00 |
| **OpenAI GPT-4** | ~$0.03 | ~$1.50 | ~$3.00 |
| **Google Gemini** | ~$0.01 | ~$0.50 | ~$1.00 |

*Estimates include both purple agent analysis and LLM judging*

---

## 📊 Output Format

### Evaluation Response

```json
{
  "success": true,
  "tests_executed": 50,
  "execution_time_seconds": 245.3,
  "metrics": {
    "f1_score": 0.87,
    "precision": 0.89,
    "recall": 0.85,
    "accuracy": 0.88,
    "average_llm_score": 0.82,
    "average_explanation_quality": 0.78,
    "average_technical_correctness": 0.85,
    "average_actionability": 0.73,
    "confusion_matrix": {
      "true_positives": 22,
      "true_negatives": 22,
      "false_positives": 3,
      "false_negatives": 3
    }
  },
  "metadata": {
    "mode": "llm_judge",
    "llm_provider": "anthropic",
    "llm_model": "claude-3-5-sonnet-20241022"
  }
}
```

### Individual Test Result

```json
{
  "test_case_id": "py_classic_001",
  "ground_truth": true,
  "predicted": true,
  "outcome": "true_positive",
  "category": "classic_sqli",
  "language": "python",
  "confidence": 0.92,
  "llm_score": 0.85,
  "llm_judgment": {
    "criteria": {
      "vulnerability_detection_accuracy": 1.0,
      "explanation_quality": 0.8,
      "technical_correctness": 0.9,
      "actionability": 0.7,
      "completeness": 0.8
    },
    "overall_score": 0.85,
    "reasoning": "The agent correctly identified the SQL injection vulnerability...",
    "identified_issues": [
      "Explanation could mention specific line numbers",
      "Missing remediation example"
    ],
    "strengths": [
      "Correctly identified f-string concatenation risk",
      "Accurate severity assessment",
      "Clear explanation of the vulnerability mechanism"
    ],
    "confidence": 0.9
  }
}
```

---

## 🎯 Use Cases

### 1. Research & Development

Compare security tools on **explanation quality**, not just accuracy:

```bash
# Evaluate Tool A
curl -X POST http://localhost:9011/eval \
  -d '{"purple_agent_endpoint": "http://tool-a:9019"}'

# Evaluate Tool B
curl -X POST http://localhost:9011/eval \
  -d '{"purple_agent_endpoint": "http://tool-b:9019"}'

# Compare average_explanation_quality scores
```

### 2. Tool Improvement

Identify specific weaknesses:

- "High detection accuracy but poor actionability"
- "Strong technical correctness but unclear explanations"
- "Good completeness but missing remediation guidance"

### 3. Educational Evaluation

Assess learning tools for students:

- Are explanations clear for beginners?
- Do they provide actionable next steps?
- Is the technical reasoning sound?

### 4. Production Readiness

Evaluate if a tool is ready for developers:

```
Accuracy: 0.90 ✅
Explanation Quality: 0.85 ✅
Technical Correctness: 0.88 ✅
Actionability: 0.65 ⚠️  <- Needs improvement
```

---

## 🔬 How It Works

### Evaluation Pipeline

```
┌─────────────────┐
│  Code Sample    │
│  + Ground Truth │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Purple Agent   │
│  Analysis       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Judge      │
│  Evaluation     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Multi-dim      │
│  Scoring        │
└─────────────────┘
```

### LLM Prompt Structure

The LLM judge receives:

1. **Code Sample** - The actual code being analyzed
2. **Ground Truth** - Whether it's actually vulnerable
3. **Purple Agent's Analysis** - Detection, confidence, explanation, patterns
4. **Evaluation Criteria** - 5 dimensions to score (0-1 scale)

The LLM returns:
- Scores for each criterion
- Detailed reasoning
- Identified issues and strengths
- Confidence in judgment

### Scoring Formula

```
Overall Score =
  0.40 × Vulnerability Detection Accuracy +
  0.25 × Technical Correctness +
  0.20 × Explanation Quality +
  0.10 × Actionability +
  0.05 × Completeness
```

---

## 📈 Performance

### Speed

| Component | Time per Test |
|-----------|---------------|
| Purple Agent Call | 0.5-2s |
| LLM Judge Call | 2-5s |
| **Total** | **2.5-7s** |

**50 tests**: ~2-5 minutes
**100 tests**: ~5-10 minutes

### Cost Comparison

| Judge Type | 100 Tests | Pros | Cons |
|------------|-----------|------|------|
| **Binary** | Free | Fast, deterministic | Only accuracy metrics |
| **LLM Judge** | $1-3 | Quality metrics, feedback | Slower, costs money |

---

## 🐛 Troubleshooting

### Common Issues

**1. API Key Not Found**

```bash
Error: API key not found for provider anthropic
```

Solution:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# Or pass via command line
python llm_judge.py --api-key sk-ant-...
```

**2. Timeout Errors**

```bash
Error: Request timed out after 30.0 seconds
```

Solution:
```bash
# Increase timeout
python llm_judge.py --per-test-timeout-seconds 60.0
```

**3. Rate Limiting**

```bash
Error: 429 Too Many Requests
```

Solution:
- Reduce test budget: `--test-budget 25`
- Add delays between tests (code modification needed)
- Use higher tier API key

**4. JSON Parse Errors**

```bash
Error: Could not extract JSON from LLM response
```

Solution:
- Lower temperature: `temperature=0.0` in config
- Try different model
- Check LLM prompt formatting

---

## 🔐 Security Considerations

### API Key Safety

- Never commit API keys to version control
- Use environment variables
- Rotate keys regularly
- Use least-privilege API keys

### Data Privacy

- Code samples are sent to LLM provider
- Ensure compliance with data policies
- Consider self-hosted LLMs for sensitive code
- Review provider terms of service

---

## 📚 Examples

### Example 1: Basic Evaluation

```python
import asyncio
from llm_judge import SQLInjectionLLMJudge, LLMJudgeConfig, LLMProvider
from models import EvalRequest

# Configure LLM judge
llm_config = LLMJudgeConfig(
    provider=LLMProvider.ANTHROPIC,
    model="claude-3-5-sonnet-20241022"
)

# Create judge
judge = SQLInjectionLLMJudge("datasets/sql_injection", llm_config)

# Evaluation request
request = EvalRequest(
    purple_agent_id="my-detector",
    purple_agent_endpoint="http://localhost:9019",
    config={"test_budget": 30}
)

# Run evaluation
response = await judge.run_eval(request, updater)
print(f"F1 Score: {response.metrics.f1_score:.3f}")
print(f"LLM Quality Score: {response.metrics.average_llm_score:.3f}")
```

### Example 2: Comparing Providers

```bash
# Test with Claude
python llm_judge.py --llm-provider anthropic --port 9011 &

# Test with GPT-4
python llm_judge.py --llm-provider openai --port 9012 &

# Test with Gemini
python llm_judge.py --llm-provider google --port 9013 &

# Compare results across providers
```

### Example 3: Custom Weights

Modify weights in `JudgmentCriteria.overall_score`:

```python
@property
def overall_score(self) -> float:
    """Custom weighting: prioritize actionability."""
    return (
        self.vulnerability_detection_accuracy * 0.35 +
        self.explanation_quality * 0.20 +
        self.technical_correctness * 0.20 +
        self.actionability * 0.20 +  # Increased from 0.10
        self.completeness * 0.05
    )
```

---

## 🤝 Contributing

### Adding New Criteria

1. Update `JudgmentCriteria` model
2. Modify `_build_judge_prompt()` to include new criterion
3. Update `overall_score` property with new weight
4. Update `LLMEvaluationMetrics` to track new average

### Supporting New LLM Providers

1. Add to `LLMProvider` enum
2. Implement `_call_<provider>()` method in `LLMJudge`
3. Update API key handling in `__init__()`
4. Add default model in `main()`

---

## 📖 References

### Related Files

- [sql_injection_judge.py](sql_injection_judge.py) - Traditional binary judge
- [models.py](models.py) - Data models and schemas
- [dataset_manager.py](dataset_manager.py) - Dataset loading
- [scoring_engine.py](scoring_engine.py) - Metrics calculation

### Documentation

- [PROJECT_STRUCTURE.md](../../docs/PROJECT_STRUCTURE.md) - Overall project structure
- [SPECIFICATION.md](../../docs/SPECIFICATION.md) - Technical specification
- [DESIGN.md](../../docs/DESIGN.md) - System architecture

### LLM Provider Docs

- [Anthropic Claude API](https://docs.anthropic.com/claude/reference/messages_post)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [Google Gemini API](https://ai.google.dev/docs)

---

## 📝 License

MIT License - See [LICENSE](../../LICENSE) for details

---

## 💡 Tips

1. **Start Small**: Test with `--test-budget 10` first
2. **Monitor Costs**: Track API usage in provider dashboards
3. **Cache Results**: Store judgments to avoid re-evaluation
4. **Compare Judges**: Run both binary and LLM judge for insights
5. **Iterate on Prompts**: Customize `_build_judge_prompt()` for your needs

---

**Version:** 1.0
**Last Updated:** 2025-11-05
**Maintained By:** SecurityEvaluator Team
