#!/bin/bash
# Launch script for Green Agent (Cyber Security Evaluator)
# Used by AgentBeats Controller to start the agent

set -e

echo "Starting Cyber Security Evaluator (Green Agent)..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start the Green Agent
# Bind to 0.0.0.0 for external access
python3 green_agents/cybersecurity_evaluator.py \
    --host 0.0.0.0 \
    --port 9010 \
    --enable-llm

echo "Green Agent started on port 9010"
