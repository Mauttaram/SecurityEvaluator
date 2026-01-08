# AgentBeats Deployment URLs

## Overview

This document tracks the current AgentBeats deployment URLs. URLs are temporary when using Cloudflare's free tunnels and will change on each deployment.

## Current Deployment

Use `deploy_separate_urls.sh` for proper AgentBeats integration with separate launcher and endpoint URLs.

### Deployment Command

```bash
PYTHONPATH=.:src ./deploy_separate_urls.sh
```

This creates:
- **Launcher URL**: Controller (port 9000/8100) - handles lifecycle, reset, health checks
- **Endpoint URL**: Direct agent (port 9010/8000) - handles A2A protocol, agent card

### URL Pattern

After deployment, you'll see output like:

```
Green Agent (Cyber Security Evaluator)
  Launcher URL: https://[random-words].trycloudflare.com
  Endpoint URL: https://[random-words].trycloudflare.com
```

## Registration on AgentBeats

### Green Agent

```
Agent Name: Cyber Security Evaluator
Agent Type: Green Agent
Launcher URL: [from deployment output]
Endpoint URL: [from deployment output]
```

### Purple Agent

```
Agent Name: HomeAutomationAgent  
Agent Type: Purple Agent
Launcher URL: [from deployment output]
Endpoint URL: [from deployment output]
```

## Architecture

**Launcher URL** → AgentBeats Controller → Lifecycle management, /reset endpoint  
**Endpoint URL** → Direct Agent → A2A protocol, agent card, evaluations

## Persistent URLs (Optional)

For production, create named Cloudflare tunnels:

```bash
cloudflared tunnel create agentbeats-green
cloudflared tunnel route dns agentbeats-green green.yourdomain.com
```

## Stopping Deployment

The deployment script outputs PIDs for easy cleanup:

```bash
# PIDs displayed in deployment output
kill [controller_pids] [tunnel_pids]
```

Or press Ctrl+C in the deployment terminal.

## Logs

View logs for troubleshooting:

```bash
tail -f /tmp/green_controller.log    # Green controller
tail -f /tmp/purple_controller.log   # Purple controller  
tail -f /tmp/green_endpoint.log      # Green tunnel
tail -f /tmp/purple_endpoint.log     # Purple tunnel
```
