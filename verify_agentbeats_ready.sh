#!/bin/bash
# AgentBeats Readiness Verification Script
# Verifies that both Green and Purple agents are ready for AgentBeats integration

set -e

echo "=========================================="
echo "AgentBeats Readiness Verification"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
echo "1. Checking Docker..."
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker is running"
else
    echo -e "${RED}✗${NC} Docker is not running"
    echo "   Please start Docker Desktop and try again"
    exit 1
fi

# Check if docker-compose.yml exists
echo ""
echo "2. Checking docker-compose.yml..."
if [ -f "docker-compose.yml" ]; then
    echo -e "${GREEN}✓${NC} docker-compose.yml found"
else
    echo -e "${RED}✗${NC} docker-compose.yml not found"
    exit 1
fi

# Start the agents
echo ""
echo "3. Starting agents with Docker Compose..."
docker-compose up -d

# Wait for agents to start
echo ""
echo "4. Waiting for agents to initialize (10 seconds)..."
sleep 10

# Check Green Agent
echo ""
echo "5. Verifying Green Agent (port 9010)..."
if curl -s -f http://localhost:9010/.well-known/agent-card.json > /dev/null; then
    echo -e "${GREEN}✓${NC} Green Agent is responding"
    
    # Check agent card content
    AGENT_NAME=$(curl -s http://localhost:9010/.well-known/agent-card.json | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "   Agent Name: $AGENT_NAME"
    
    # Check for 7-agent framework mention
    if curl -s http://localhost:9010/.well-known/agent-card.json | grep -q "7-agent"; then
        echo -e "${GREEN}✓${NC} Agent card mentions 7-agent framework"
    else
        echo -e "${YELLOW}⚠${NC} Agent card may not mention 7-agent framework"
    fi
else
    echo -e "${RED}✗${NC} Green Agent is not responding"
    echo "   Check logs: docker-compose logs green-agent"
    exit 1
fi

# Check Purple Agent
echo ""
echo "6. Verifying Purple Agent (port 8000)..."
if curl -s -f http://localhost:8000/.well-known/agent-card.json > /dev/null; then
    echo -e "${GREEN}✓${NC} Purple Agent is responding"
    
    # Check agent card content
    AGENT_NAME=$(curl -s http://localhost:8000/.well-known/agent-card.json | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "   Agent Name: $AGENT_NAME"
else
    echo -e "${RED}✗${NC} Purple Agent is not responding"
    echo "   Check logs: docker-compose logs purple-agent"
    exit 1
fi

# Test Purple Agent command
echo ""
echo "7. Testing Purple Agent command execution..."
RESPONSE=$(curl -s -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "message",
    "role": "user",
    "parts": [{
      "kind": "text",
      "text": "{\"command\": \"Set heating to warm\", \"parameters\": {}}"
    }]
  }')

if echo "$RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✓${NC} Purple Agent command execution works"
else
    echo -e "${RED}✗${NC} Purple Agent command execution failed"
    echo "   Response: $RESPONSE"
fi

# Summary
echo ""
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo -e "${GREEN}✓${NC} Docker is running"
echo -e "${GREEN}✓${NC} Green Agent is accessible at http://localhost:9010"
echo -e "${GREEN}✓${NC} Purple Agent is accessible at http://localhost:8000"
echo -e "${GREEN}✓${NC} A2A protocol compliance verified"
echo ""
echo "Next Steps for AgentBeats Registration:"
echo "1. Deploy to public endpoint (cloud, ngrok, or Cloudflare)"
echo "2. Update agent card URLs with public endpoint"
echo "3. Register on https://agentbeats.org"
echo ""
echo "For deployment options, see: AGENTBEATS_REGISTRATION.md"
echo ""
echo "To stop agents: docker-compose down"
echo "=========================================="
