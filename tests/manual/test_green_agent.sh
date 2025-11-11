#!/bin/bash

# Test Green Agent /tasks endpoint

echo "==================================================================="
echo "Step 1: Check if Green Agent is running on port 9010"
echo "==================================================================="

# Check if agent is running
if curl -s http://127.0.0.1:9010/card > /dev/null 2>&1; then
    echo "✅ Green Agent is running"
else
    echo "❌ Green Agent not running. Start it with:"
    echo "   python green_agents/cybersecurity_evaluator.py --port 9010"
    exit 1
fi

echo ""
echo "==================================================================="
echo "Step 2: Get AgentCard"
echo "==================================================================="
curl -s http://127.0.0.1:9010/card | jq .

echo ""
echo "==================================================================="
echo "Step 3: Submit Task to /tasks (SQL Injection)"
echo "==================================================================="

TASK_RESPONSE=$(curl -s -X POST http://127.0.0.1:9010/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "purple_agent_id": "test_detector",
      "purple_agent_endpoint": "http://127.0.0.1:8000",
      "config": {
        "scenario": "sql_injection",
        "max_rounds": 2,
        "use_sandbox": false
      }
    }
  }')

echo "$TASK_RESPONSE" | jq .

# Extract task ID
TASK_ID=$(echo "$TASK_RESPONSE" | jq -r '.id // .task_id // "unknown"')

if [ "$TASK_ID" != "unknown" ]; then
    echo ""
    echo "==================================================================="
    echo "Step 4: Check Task Status"
    echo "==================================================================="
    echo "Task ID: $TASK_ID"

    sleep 2

    curl -s http://127.0.0.1:9010/tasks/$TASK_ID | jq .
fi
