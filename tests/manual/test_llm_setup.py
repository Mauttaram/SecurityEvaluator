#!/usr/bin/env python3
"""
Test LLM integration with Green Agent.
Verifies OpenAI API is accessible and working.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))


def test_llm_client():
    """Test LLM client initialization and basic functionality."""
    print("=" * 70)
    print("Testing LLM Integration")
    print("=" * 70)

    # Step 1: Check .env file
    print("\n1. Checking .env file...")
    env_path = Path(__file__).parent / '.env'
    if not env_path.exists():
        print("❌ .env file not found")
        print("\nCreate it with:")
        print("  cp .env.example .env")
        print("  # Then edit .env and add your OPENAI_API_KEY")
        return False
    print("✅ .env file exists")

    # Step 2: Check API key
    print("\n2. Checking OPENAI_API_KEY...")
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not set in .env")
        print("\nAdd to .env:")
        print("  OPENAI_API_KEY=sk-your-actual-key-here")
        return False

    if api_key.startswith("sk-your"):
        print("❌ OPENAI_API_KEY is placeholder value")
        print("\nReplace with your actual API key from:")
        print("  https://platform.openai.com/api-keys")
        return False

    print(f"✅ OPENAI_API_KEY set ({api_key[:10]}...)")

    # Step 3: Initialize LLM client
    print("\n3. Initializing LLM client...")
    try:
        from llm import LLMClient
        client = LLMClient()
        print("✅ LLM client initialized")
        print(f"   Model: {client.model}")
        print(f"   Temperature: {client.temperature}")
        print(f"   Max tokens: {client.max_tokens}")
    except ValueError as e:
        print(f"❌ LLM client initialization failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

    # Step 4: Test API call
    print("\n4. Testing OpenAI API...")
    try:
        response = client.generate(
            prompt="Say 'Hello from Green Agent!' in exactly 5 words.",
            max_tokens=20
        )
        print("✅ OpenAI API accessible")
        print(f"   Response: {response.content}")
        print(f"   Tokens: {response.usage.get('total_tokens', 0)}")
        print(f"   Latency: {response.latency_ms:.0f}ms")
    except Exception as e:
        print(f"❌ API call failed: {e}")
        print("\nPossible causes:")
        print("  - Invalid API key")
        print("  - Network issues")
        print("  - Rate limit exceeded")
        return False

    # Step 5: Test with Green Agent
    print("\n5. Testing Green Agent LLM flag...")
    try:
        from green_agents.cybersecurity_evaluator import CyberSecurityEvaluator

        # Test without LLM
        agent_no_llm = CyberSecurityEvaluator(enable_llm=False)
        if agent_no_llm.llm_enabled:
            print("❌ LLM should be disabled")
            return False
        print("✅ Green Agent (LLM disabled) works")

        # Test with LLM
        agent_with_llm = CyberSecurityEvaluator(enable_llm=True)
        if not agent_with_llm.llm_enabled:
            print("❌ LLM should be enabled")
            return False
        print("✅ Green Agent (LLM enabled) works")
        print(f"   LLM clients: {len(agent_with_llm.llm_clients)}")

    except Exception as e:
        print(f"❌ Green Agent test failed: {e}")
        return False

    # Success!
    print("\n" + "=" * 70)
    print("✅ All LLM integration tests passed!")
    print("=" * 70)
    print("\nYou can now run the Green Agent with LLM:")
    print("  python green_agents/cybersecurity_evaluator.py --port 9010 --enable-llm")
    print()
    return True


if __name__ == "__main__":
    success = test_llm_client()
    sys.exit(0 if success else 1)
