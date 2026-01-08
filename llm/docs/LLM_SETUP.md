# LLM Setup Guide

## Overview

The Green Agent uses LLM (OpenAI) for 3 advanced agents:
- **Perspective Agent** - Multi-viewpoint analysis
- **LLM Judge** - Dawid-Skene consensus scoring
- **Counterfactual Agent** - Remediation suggestions

4 agents work **without LLM** (pure algorithmic):
- BoundaryProber, Exploiter, Mutator, Validator

## Quick Setup

### 1. Get OpenAI API Key

Get your API key from: https://platform.openai.com/api-keys

### 2. Create `.env` File

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Run Green Agent with LLM

```bash
python green_agents/cybersecurity_evaluator.py --port 9010 --enable-llm
```

You should see:
```
INFO: LLM integration enabled
```

## Configuration Options

All settings are optional (defaults shown):

```bash
# .env file
OPENAI_API_KEY=sk-...                  # Required
OPENAI_MODEL=gpt-4o-mini               # Default model
OPENAI_TEMPERATURE=0.7                 # Default temperature
OPENAI_MAX_TOKENS=2000                 # Default max tokens
OPENAI_TIMEOUT=30                      # Timeout in seconds
LLM_CACHE_ENABLED=true                 # Enable response caching
LLM_RETRY_ATTEMPTS=3                   # Retry failed requests
LLM_RETRY_DELAY=2.0                    # Delay between retries (seconds)
```

## Cost Estimates

Using `gpt-4o-mini` (default):
- **Input:** $0.15 per 1M tokens
- **Output:** $0.60 per 1M tokens

Typical evaluation (10 rounds):
- ~50,000 tokens total
- **Cost:** ~$0.03 per evaluation

Cost optimization features (enabled by default):
- Response caching (avoid redundant calls)
- Strategic LLM routing (30-60% savings)
- Adaptive sampling (reduce unnecessary tests)

## Verify LLM Integration

```bash
python test_llm_integration.py
```

Expected output:
```
✅ LLM client initialized
✅ OpenAI API accessible
✅ Model: gpt-4o-mini
```

## Troubleshooting

### "LLM integration disabled (no API key)"

**Cause:** Missing or invalid `OPENAI_API_KEY`

**Fix:**
1. Check `.env` file exists in project root
2. Verify API key starts with `sk-`
3. Test API key: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

### "Rate limit exceeded"

**Cause:** Too many requests to OpenAI API

**Fix:**
1. Wait 60 seconds
2. Reduce `max_rounds` in config
3. Upgrade OpenAI plan

### "Model not found"

**Cause:** Invalid model name in `.env`

**Fix:** Use supported models:
- `gpt-4o` (most capable, higher cost)
- `gpt-4o-mini` (default, best value)
- `gpt-4-turbo`
- `gpt-3.5-turbo` (cheapest, lower quality)

## Running Without LLM

Default mode (no `--enable-llm` flag):
```bash
python green_agents/cybersecurity_evaluator.py --port 9010
```

This works fine but uses only 4 agents:
- ✅ BoundaryProber (Thompson Sampling)
- ✅ Exploiter (Hybrid generation)
- ✅ Mutator (Novelty Search)
- ✅ Validator (Syntax checks)
- ❌ Perspective (needs LLM)
- ❌ LLMJudge (needs LLM)
- ❌ Counterfactual (needs LLM)

Results are still valid but less comprehensive.
