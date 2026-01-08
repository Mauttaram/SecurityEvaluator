#!/usr/bin/env python3
"""
Test /tasks endpoint of Green Agent.
Run this after starting the green agent.
"""

import requests
import json
import time

GREEN_AGENT_URL = "http://127.0.0.1:9010"

def test_tasks_endpoint():
    print("=" * 70)
    print("Testing Green Agent /tasks Endpoint")
    print("=" * 70)

    # Step 1: Check if agent is running (A2A protocol)
    print("\n1. Checking if Green Agent is running...")
    try:
        response = requests.get(f"{GREEN_AGENT_URL}/.well-known/agent-card.json", timeout=5)
        response.raise_for_status()
        print("✅ Green Agent is running on port 9010")
    except Exception as e:
        print(f"❌ Green Agent not running: {e}")
        print("\nStart it with:")
        print("  python green_agents/cybersecurity_evaluator.py --port 9010")
        return

    # Step 2: Get AgentCard (A2A protocol)
    print("\n2. Getting AgentCard (A2A protocol)...")
    card_response = requests.get(f"{GREEN_AGENT_URL}/.well-known/agent-card.json", timeout=5)
    card = card_response.json()
    print(f"   Name: {card.get('name')}")
    print(f"   Version: {card.get('version')}")
    print(f"   Skills: {len(card.get('skills', []))}")

    # Step 3: Submit task via JSON-RPC
    print("\n3. Submitting task via JSON-RPC...")

    # A2A uses JSON-RPC format
    jsonrpc_request = {
        "jsonrpc": "2.0",
        "method": "tasks/create",
        "params": {
            "input": {
                "purple_agent_id": "test_sql_detector",
                "purple_agent_endpoint": "http://127.0.0.1:8000",
                "config": {
                    "scenario": "sql_injection",
                    "max_rounds": 2,
                    "use_sandbox": False,  # Disabled for quick test
                    "num_boundary_probers": 1,
                    "num_exploiters": 1,
                    "num_mutators": 1
                }
            }
        },
        "id": 1
    }

    print("\nJSON-RPC Request:")
    print(json.dumps(jsonrpc_request, indent=2))

    try:
        # Submit via JSON-RPC to root endpoint
        response = requests.post(
            GREEN_AGENT_URL,  # POST to root
            json=jsonrpc_request,
            timeout=10
        )
        response.raise_for_status()

        rpc_response = response.json()
        print("\n✅ Task submitted successfully!")
        print("\nJSON-RPC Response:")
        print(json.dumps(rpc_response, indent=2))

        # Extract task ID from JSON-RPC result
        result = rpc_response.get('result', {})
        task_id = result.get('id') or result.get('task_id')

        if task_id:
            print(f"\n4. Task ID: {task_id}")
            print("   Waiting 3 seconds before checking status...")
            time.sleep(3)

            # Check task status via JSON-RPC
            status_request = {
                "jsonrpc": "2.0",
                "method": "tasks/get",
                "params": {"task_id": task_id},
                "id": 2
            }
            status_response = requests.post(GREEN_AGENT_URL, json=status_request)
            status_data = status_response.json()

            print("\n5. Task Status (JSON-RPC):")
            print(json.dumps(status_data, indent=2))

    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_tasks_endpoint()
