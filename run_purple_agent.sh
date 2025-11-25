#!/bin/bash
# Launch script for Purple Agent (Home Automation Agent)
# Used by AgentBeats Controller to start the agent

set -e

echo "Starting Home Automation Agent (Purple Agent)..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start the Purple Agent
# Bind to 0.0.0.0 for external access
python3 purple_agents/home_automation_agent.py \
    --host 0.0.0.0 \
    --port 8000

echo "Purple Agent started on port 8000"
