#!/bin/bash
# AgentBeats Docker Deployment
# Uses Docker for agents and Cloudflare for public URLs

set -e

echo "=========================================="
echo "AgentBeats Docker Deployment"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
NC='\033[0m'

# Stop existing containers
echo "1. Stopping existing containers..."
docker compose down

# Start containers
echo ""
echo "2. Starting agents with Docker Compose..."
docker compose up -d

# Wait for agents
echo ""
echo "3. Waiting for agents to initialize (20 seconds)..."
sleep 20

# Start Cloudflare Tunnels
echo ""
echo "4. Starting Cloudflare Tunnels..."

# Green Agent (Port 9010)
cloudflared tunnel --url http://localhost:9010 > /tmp/green_tunnel.log 2>&1 &
GREEN_TUNNEL_PID=$!

# Purple Agent (Port 8000)
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
echo "AGENTBEATS REGISTRATION (DOCKER)"
echo "=========================================="
echo ""

if [ -n "$GREEN_URL" ]; then
    echo -e "${GREEN}Green Agent (SecEval-Test-2024-11-24)${NC}"
    echo "  Launcher URL: $GREEN_URL"
    echo "  Endpoint URL: $GREEN_URL"
    echo "  (Use SAME URL for both!)"
    echo ""
    echo "  Agent Card: $GREEN_URL/.well-known/agent-card.json"
    echo ""
fi

if [ -n "$PURPLE_URL" ]; then
    echo -e "${GREEN}Purple Agent (HomeAutomation-Test-2024-11-24)${NC}"
    echo "  Launcher URL: $PURPLE_URL"
    echo "  Endpoint URL: $PURPLE_URL"
    echo "  (Use SAME URL for both!)"
    echo ""
    echo "  Agent Card: $PURPLE_URL/.well-known/agent-card.json"
    echo ""
fi

echo "=========================================="
echo ""
echo "Tunnel PIDs:"
echo "  Green Tunnel: $GREEN_TUNNEL_PID"
echo "  Purple Tunnel: $PURPLE_TUNNEL_PID"
echo ""
echo "To stop tunnels: kill $GREEN_TUNNEL_PID $PURPLE_TUNNEL_PID"
echo "To stop agents: docker compose down"
echo ""
echo "Press Ctrl+C to stop tunnels..."

# Wait
trap "echo ''; echo 'Stopping tunnels...'; kill $GREEN_TUNNEL_PID $PURPLE_TUNNEL_PID 2>/dev/null; echo 'Done.'; exit 0" INT

wait
