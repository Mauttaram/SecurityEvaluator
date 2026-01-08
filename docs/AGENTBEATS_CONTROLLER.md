# AgentBeats Controller Usage Guide

## Overview

The AgentBeats Controller is a wrapper component required by the AgentBeats platform for:
- **State Management**: Track and control agent process state
- **Reproducibility**: Reset agent to clean state before each assessment
- **Lifecycle Control**: Start, stop, and restart agent processes
- **Request Proxying**: Forward requests to the underlying agent

## Why It's Needed

AgentBeats requires the controller to ensure:
1. **Reproducible Assessments**: Each test starts with a clean agent state
2. **Process Management**: Platform can start/stop agents programmatically
3. **Standardized Interface**: Consistent API across all agents
4. **State Isolation**: Prevent state leakage between assessments

## Architecture

```
AgentBeats Platform
        ↓
AgentBeats Controller (Port 9000/8100)
        ↓
A2A Agent (Port 9010/8000)
```

## Usage

### 1. Start Green Agent with Controller

```bash
# Terminal 1: Start the controller (it will manage the agent)
python src/agentbeats/controller.py \
    --agent-name "Cyber Security Evaluator" \
    --agent-port 9010 \
    --controller-port 9000 \
    --launch-script ./run_green_agent.sh \
    --working-dir . \
    --auto-start
```

### 2. Start Purple Agent with Controller

```bash
# Terminal 2: Start the controller for Purple Agent
python src/agentbeats/controller.py \
    --agent-name "Home Automation Agent" \
    --agent-port 8000 \
    --controller-port 8100 \
    --launch-script ./run_purple_agent.sh \
    --working-dir . \
    --auto-start
```

### 3. Controller API Endpoints

Once running, the controller exposes:

```bash
# Check agent status
curl http://localhost:9000/status

# Start agent (if not auto-started)
curl -X POST http://localhost:9000/start

# Stop agent
curl -X POST http://localhost:9000/stop

# Reset agent to clean state (soft reset)
curl -X POST http://localhost:9000/reset \
  -H "Content-Type: application/json" \
  -d '{"hard_reset": false}'

# Reset agent (hard reset - restart process)
curl -X POST http://localhost:9000/reset \
  -H "Content-Type: application/json" \
  -d '{"hard_reset": true}'

# Proxy request to agent (transparent)
curl -X POST http://localhost:9000/ \
  -H "Content-Type: application/json" \
  -d '{...agent request...}'
```

## AgentBeats Platform Integration

When registering on AgentBeats, use the **controller URL** instead of the agent URL:

| Component | Without Controller | With Controller |
|-----------|-------------------|-----------------|
| Green Agent URL | `http://your-ip:9010` | `http://your-ip:9000` |
| Purple Agent URL | `http://your-ip:8000` | `http://your-ip:8100` |
| Agent Card | `http://your-ip:9010/.well-known/agent-card.json` | `http://your-ip:9000/.well-known/agent-card.json` (proxied) |

The controller transparently proxies all requests to the underlying agent.

## Configuration Options

### Command Line Arguments

- `--agent-name`: Name of the agent (required)
- `--agent-port`: Port where the agent runs (required)
- `--agent-host`: Host where agent runs (default: 127.0.0.1)
- `--controller-port`: Port for controller API (default: 9000)
- `--launch-script`: Path to launch script (e.g., run.sh)
- `--launch-command`: Direct command to start agent
- `--working-dir`: Working directory for agent process
- `--auto-start`: Auto-start agent when controller starts

### Launch Scripts

The controller uses launch scripts (`run_green_agent.sh`, `run_purple_agent.sh`) to start agents. These scripts:
- Activate virtual environment
- Set environment variables
- Start the agent with correct parameters

## Docker Deployment

For Docker deployment, you can wrap the controller in a container:

```dockerfile
# Example Dockerfile for controller + agent
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

# Start controller which manages the agent
CMD ["python", "src/agentbeats/controller.py", \
     "--agent-name", "Cyber Security Evaluator", \
     "--agent-port", "9010", \
     "--controller-port", "9000", \
     "--launch-command", "python green_agents/cybersecurity_evaluator.py --host 0.0.0.0 --port 9010", \
     "--auto-start"]
```

## Troubleshooting

### Controller can't start agent

Check:
1. Launch script exists and is executable: `chmod +x run_green_agent.sh`
2. Launch script path is correct
3. Working directory is set correctly
4. Agent dependencies are installed

### Agent not responding after start

Check:
1. Agent port is not already in use: `lsof -i :9010`
2. Firewall allows the port
3. Agent logs for errors: Check controller output

### Reset not working

The controller tries:
1. **Soft reset**: Call agent's `/reset` endpoint (if available)
2. **Hard reset**: Restart the agent process

If soft reset fails, it automatically falls back to hard reset.

## Production Deployment

For production AgentBeats deployment:

1. **Deploy controller + agent together**
2. **Use HTTPS**: Put controller behind reverse proxy with TLS
3. **Set public URL**: Use `--card-url` with your public HTTPS URL
4. **Monitor health**: Check `/status` endpoint regularly
5. **Auto-restart**: Use systemd or supervisor to keep controller running

## Example: Full AgentBeats Setup

```bash
# 1. Start Green Agent Controller
python src/agentbeats/controller.py \
    --agent-name "Cyber Security Evaluator" \
    --agent-port 9010 \
    --controller-port 9000 \
    --launch-script ./run_green_agent.sh \
    --auto-start &

# 2. Start Purple Agent Controller
python src/agentbeats/controller.py \
    --agent-name "Home Automation Agent" \
    --agent-port 8000 \
    --controller-port 8100 \
    --launch-script ./run_purple_agent.sh \
    --auto-start &

# 3. Wait for agents to start
sleep 10

# 4. Verify controllers are running
curl http://localhost:9000/status
curl http://localhost:8100/status

# 5. Test proxying to agents
curl http://localhost:9000/.well-known/agent-card.json
curl http://localhost:8100/.well-known/agent-card.json

# 6. Register controller URLs on AgentBeats platform
# Green Agent Controller: http://your-public-ip:9000
# Purple Agent Controller: http://your-public-ip:8100
```

## Summary

The AgentBeats Controller is **required** for AgentBeats platform integration. It provides:
- ✅ State management and reset capabilities
- ✅ Process lifecycle control
- ✅ Reproducibility for assessments
- ✅ Transparent request proxying

Use the controller URLs (not direct agent URLs) when registering on AgentBeats.
