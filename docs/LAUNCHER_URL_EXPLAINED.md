# AgentBeats Launcher URL - Explained

## Quick Answer

**Yes, the AgentBeats Controller provides the Launcher URL.**

The **Launcher URL** is simply the **public URL of your AgentBeats Controller**.

## What is the Launcher URL?

The Launcher URL is the endpoint that the AgentBeats platform uses to:
1. **Health check** your agent (via `/health`)
2. **Send reset signals** before assessments (via `/reset`)
3. **Manage agent state** (start/stop via `/start`, `/stop`)
4. **Proxy requests** to your agent (all other requests)

## Controller = Launcher URL

```
AgentBeats Platform
        ↓
Launcher URL (Controller)
  http://your-domain:9000
        ↓
    Your Agent
  http://localhost:9010
```

## What to Register on AgentBeats

When registering your agent on the AgentBeats platform, use the **controller's public URL** as the Launcher URL:

### Green Agent
- **Launcher URL**: `https://your-domain:9000` (controller)
- **NOT**: `https://your-domain:9010` (direct agent)

### Purple Agent
- **Launcher URL**: `https://your-domain:8100` (controller)
- **NOT**: `https://your-domain:8000` (direct agent)

## Controller Endpoints for AgentBeats

The controller exposes these endpoints that AgentBeats uses:

| Endpoint | Purpose | Used By AgentBeats |
|----------|---------|-------------------|
| `GET /health` | Health check | ✅ Yes - to verify agent is online |
| `GET /status` | Get agent state | ✅ Yes - to monitor agent |
| `POST /reset` | Reset agent state | ✅ Yes - before each assessment |
| `POST /start` | Start agent | ✅ Yes - if agent is stopped |
| `POST /stop` | Stop agent | ⚠️ Maybe - for maintenance |
| `* /*` | Proxy to agent | ✅ Yes - all agent requests |

## How AgentBeats Uses the Launcher URL

### 1. Health Check
```bash
# AgentBeats checks if your agent is online
GET https://your-domain:9000/health

# Response if healthy:
{
  "status": "healthy",
  "agent_state": "running",
  "agent_accessible": true
}
```

### 2. Reset Before Assessment
```bash
# AgentBeats resets your agent before each test
POST https://your-domain:9000/reset
Content-Type: application/json

{
  "hard_reset": true
}
```

### 3. Proxy Agent Requests
```bash
# AgentBeats sends evaluation requests
POST https://your-domain:9000/
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "tasks/send",
  ...
}

# Controller forwards to agent at http://localhost:9010/
```

## Example: Full Registration

```
AgentBeats Registration Form:

Agent Name: Cyber Security Evaluator
Agent Type: Green Agent
Launcher URL: https://your-domain.com:9000  ← USE CONTROLLER URL
Description: AI Agent Security Evaluator...
```

## Verification

Test your Launcher URL before registering:

```bash
# 1. Start controller
python src/agentbeats/controller.py \
    --agent-name "Cyber Security Evaluator" \
    --agent-port 9010 \
    --controller-port 9000 \
    --launch-script ./run_green_agent.sh \
    --auto-start

# 2. Test health endpoint
curl http://localhost:9000/health

# Expected response:
# {"status": "healthy", "agent_state": "running", "agent_accessible": true}

# 3. Test agent card proxying
curl http://localhost:9000/.well-known/agent-card.json

# Should return your agent card
```

## Summary

✅ **Launcher URL = Controller URL**
- The controller IS the launcher
- Register controller's public URL on AgentBeats
- Controller handles health checks, resets, and proxying
- AgentBeats never talks directly to your agent

❌ **Don't use direct agent URL**
- AgentBeats needs the controller wrapper
- Direct agent URL won't provide reset/health endpoints
- Assessments won't be reproducible without controller

## Updated Controller Features

The controller now includes:
- ✅ `/health` endpoint for AgentBeats health checks
- ✅ Launcher URL displayed in startup logs
- ✅ Clear registration instructions
- ✅ All required AgentBeats functionality

Your controller is ready to serve as the Launcher URL! 🚀
