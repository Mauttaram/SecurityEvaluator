#!/bin/bash
# Simple AgentBeats deployment - just expose agents directly via Cloudflare
# Use SAME URL for both launcher and endpoint (like the official tutorial)

set -e

echo "=========================================="
echo "AgentBeats Simple Deployment"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
NC='\033[0m'

# Start Green Agent directly
echo "1. Starting Green Agent (port 9010)..."
PYTHONPATH=.:src python3 green_agents/cybersecurity_evaluator.py \
    --host 0.0.0.0 \
    --port 9010 \
    --enable-llm > /tmp/green_agent.log 2>&1 &

GREEN_PID=$!
echo "   Agent PID: $GREEN_PID"

# Start Purple Agent directly
echo ""
echo "2. Starting Purple Agent (port 8000)..."
PYTHONPATH=.:src python3 purple_agents/home_automation_agent.py \
    --host 0.0.0.0 \
    --port 8000 > /tmp/purple_agent.log 2>&1 &

PURPLE_PID=$!
echo "   Agent PID: $PURPLE_PID"

# Wait for agents to start
echo ""
echo "3. Waiting for agents to initialize (15 seconds)..."
sleep 15

# Start Cloudflare Tunnels - ONE per agent
echo ""
echo "4. Starting Cloudflare Tunnels..."

cloudflared tunnel --url http://localhost:9010 > /tmp/green_tunnel.log 2>&1 &
GREEN_TUNNEL_PID=$!

cloudflared tunnel --url http://localhost:8000 > /tmp/purple_tunnel.log 2>&1 &
PURPLE_TUNNEL_PID=$!

# Wait for tunnels
echo ""
echo "5. Waiting for tunnels to establish (10 seconds)..."
sleep 10

# Extract URLs
GREEN_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /tmp/green_tunnel.log | head -1)
PURPLE_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /tmp/purple_tunnel.log | head -1)

echo ""
echo "=========================================="
echo "AGENTBEATS REGISTRATION"
echo "=========================================="
echo ""

if [ -n "$GREEN_URL" ]; then
    echo -e "${GREEN}Green Agent (Cyber Security Evaluator)${NC}"
    echo "  Launcher URL: $GREEN_URL"
    echo "  Endpoint URL: $GREEN_URL"
    echo "  (Use SAME URL for both!)"
    echo ""
    echo "  Agent Card: $GREEN_URL/.well-known/agent-card.json"
    echo ""
fi

if [ -n "$PURPLE_URL" ]; then
    echo -e "${GREEN}Purple Agent (Home Automation Agent)${NC}"
    echo "  Launcher URL: $PURPLE_URL"
    echo "  Endpoint URL: $PURPLE_URL"
    echo "  (Use SAME URL for both!)"
    echo ""
    echo "  Agent Card: $PURPLE_URL/.well-known/agent-card.json"
    echo ""
fi

echo "=========================================="
echo ""
echo "Process IDs:"
echo "  Green Agent: $GREEN_PID"
echo "  Purple Agent: $PURPLE_PID"
echo "  Green Tunnel: $GREEN_TUNNEL_PID"
echo "  Purple Tunnel: $PURPLE_TUNNEL_PID"
echo ""
echo "To stop: kill $GREEN_PID $PURPLE_PID $GREEN_TUNNEL_PID $PURPLE_TUNNEL_PID"
echo ""
echo "Press Ctrl+C to stop all services..."

# Save PIDs
echo "$GREEN_PID $PURPLE_PID $GREEN_TUNNEL_PID $PURPLE_TUNNEL_PID" > /tmp/agentbeats_pids.txt

# Wait
trap "echo ''; echo 'Stopping...'; kill $GREEN_PID $PURPLE_PID $GREEN_TUNNEL_PID $PURPLE_TUNNEL_PID 2>/dev/null; rm /tmp/agentbeats_pids.txt; echo 'Done.'; exit 0" INT

wait
