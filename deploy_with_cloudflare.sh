#!/bin/bash
# Deploy agents with Cloudflare Tunnel for AgentBeats
# This script starts both controllers and exposes them via Cloudflare Tunnel

set -e

echo "=========================================="
echo "AgentBeats Deployment with Cloudflare"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "Error: cloudflared is not installed"
    echo "Install with: brew install cloudflared"
    exit 1
fi

echo -e "${GREEN}✓${NC} Cloudflared is installed"
echo ""

# Start Green Agent Controller in background
echo "1. Starting Green Agent Controller (port 9000)..."
python3 src/agentbeats/controller.py \
    --agent-name "Cyber Security Evaluator" \
    --agent-port 9010 \
    --controller-port 9000 \
    --launch-script ./run_green_agent.sh \
    --working-dir . \
    --auto-start > /tmp/green_controller.log 2>&1 &

GREEN_PID=$!
echo "   Controller PID: $GREEN_PID"
echo "   Logs: tail -f /tmp/green_controller.log"

# Start Purple Agent Controller in background
echo ""
echo "2. Starting Purple Agent Controller (port 8100)..."
python3 src/agentbeats/controller.py \
    --agent-name "Home Automation Agent" \
    --agent-port 8000 \
    --controller-port 8100 \
    --launch-script ./run_purple_agent.sh \
    --working-dir . \
    --auto-start > /tmp/purple_controller.log 2>&1 &

PURPLE_PID=$!
echo "   Controller PID: $PURPLE_PID"
echo "   Logs: tail -f /tmp/purple_controller.log"

# Wait for controllers to start
echo ""
echo "3. Waiting for controllers to initialize (20 seconds)..."
sleep 20

# Check if controllers are running
echo ""
echo "4. Verifying controllers..."

if curl -s -f http://localhost:9000/health > /dev/null; then
    echo -e "${GREEN}✓${NC} Green Agent Controller is healthy"
else
    echo "Error: Green Agent Controller is not responding"
    kill $GREEN_PID $PURPLE_PID 2>/dev/null || true
    exit 1
fi

if curl -s -f http://localhost:8100/health > /dev/null; then
    echo -e "${GREEN}✓${NC} Purple Agent Controller is healthy"
else
    echo "Error: Purple Agent Controller is not responding"
    kill $GREEN_PID $PURPLE_PID 2>/dev/null || true
    exit 1
fi

# Start Cloudflare Tunnels
echo ""
echo "5. Starting Cloudflare Tunnels..."
echo ""

# Green Agent Tunnel
echo "   Starting tunnel for Green Agent (port 9000)..."
cloudflared tunnel --url http://localhost:9000 > /tmp/green_tunnel.log 2>&1 &
GREEN_TUNNEL_PID=$!
echo "   Tunnel PID: $GREEN_TUNNEL_PID"

# Purple Agent Tunnel  
echo ""
echo "   Starting tunnel for Purple Agent (port 8100)..."
cloudflared tunnel --url http://localhost:8100 > /tmp/purple_tunnel.log 2>&1 &
PURPLE_TUNNEL_PID=$!
echo "   Tunnel PID: $PURPLE_TUNNEL_PID"

# Wait for tunnels to establish
echo ""
echo "6. Waiting for tunnels to establish (10 seconds)..."
sleep 10

# Extract tunnel URLs from logs
echo ""
echo "=========================================="
echo "PUBLIC URLS FOR AGENTBEATS REGISTRATION"
echo "=========================================="
echo ""

# Get Green Agent URL
if [ -f /tmp/green_tunnel.log ]; then
    GREEN_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /tmp/green_tunnel.log | head -1)
    if [ -n "$GREEN_URL" ]; then
        echo -e "${GREEN}Green Agent (Cyber Security Evaluator)${NC}"
        echo "  Launcher URL: $GREEN_URL"
        echo "  Health Check: $GREEN_URL/health"
        echo "  Agent Card:   $GREEN_URL/.well-known/agent-card.json"
        echo ""
    else
        echo "Waiting for Green Agent tunnel URL..."
        sleep 5
        GREEN_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /tmp/green_tunnel.log | head -1)
        if [ -n "$GREEN_URL" ]; then
            echo -e "${GREEN}Green Agent (Cyber Security Evaluator)${NC}"
            echo "  Launcher URL: $GREEN_URL"
            echo ""
        fi
    fi
fi

# Get Purple Agent URL
if [ -f /tmp/purple_tunnel.log ]; then
    PURPLE_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /tmp/purple_tunnel.log | head -1)
    if [ -n "$PURPLE_URL" ]; then
        echo -e "${GREEN}Purple Agent (Home Automation Agent)${NC}"
        echo "  Launcher URL: $PURPLE_URL"
        echo "  Health Check: $PURPLE_URL/health"
        echo "  Agent Card:   $PURPLE_URL/.well-known/agent-card.json"
        echo ""
    else
        echo "Waiting for Purple Agent tunnel URL..."
        sleep 5
        PURPLE_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /tmp/purple_tunnel.log | head -1)
        if [ -n "$PURPLE_URL" ]; then
            echo -e "${GREEN}Purple Agent (Home Automation Agent)${NC}"
            echo "  Launcher URL: $PURPLE_URL"
            echo ""
        fi
    fi
fi

echo "=========================================="
echo ""
echo "Process IDs (for stopping later):"
echo "  Green Controller: $GREEN_PID"
echo "  Purple Controller: $PURPLE_PID"
echo "  Green Tunnel: $GREEN_TUNNEL_PID"
echo "  Purple Tunnel: $PURPLE_TUNNEL_PID"
echo ""
echo "To stop all services:"
echo "  kill $GREEN_PID $PURPLE_PID $GREEN_TUNNEL_PID $PURPLE_TUNNEL_PID"
echo ""
echo "Logs:"
echo "  Green Controller:  tail -f /tmp/green_controller.log"
echo "  Purple Controller: tail -f /tmp/purple_controller.log"
echo "  Green Tunnel:      tail -f /tmp/green_tunnel.log"
echo "  Purple Tunnel:     tail -f /tmp/purple_tunnel.log"
echo ""
echo "=========================================="
echo ""
echo -e "${YELLOW}NOTE:${NC} Cloudflare free tunnels generate new URLs on each restart."
echo "For persistent URLs, create a named tunnel with 'cloudflared tunnel create'"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Save PIDs to file for easy cleanup
echo "$GREEN_PID $PURPLE_PID $GREEN_TUNNEL_PID $PURPLE_TUNNEL_PID" > /tmp/agentbeats_pids.txt

# Wait for user interrupt
trap "echo ''; echo 'Stopping all services...'; kill $GREEN_PID $PURPLE_PID $GREEN_TUNNEL_PID $PURPLE_TUNNEL_PID 2>/dev/null; rm /tmp/agentbeats_pids.txt; echo 'Done.'; exit 0" INT

# Keep script running
wait
