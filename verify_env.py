#!/usr/bin/env python3
"""
Verify .env file loading and API keys

Quick script to check if environment variables are loaded correctly.
"""

import os
from pathlib import Path

# Load .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'

    if not env_path.exists():
        print("❌ .env file not found!")
        print(f"   Expected location: {env_path}")
        print("\n💡 Copy .env.example to .env and add your API keys")
        exit(1)

    load_dotenv(dotenv_path=env_path)
    print(f"✅ Loaded .env from: {env_path}")
    print()

except ImportError:
    print("❌ python-dotenv not installed!")
    print("   Install with: pip install --user python-dotenv")
    exit(1)

# Check API keys
print("=" * 70)
print("API KEY STATUS")
print("=" * 70)
print()

keys_to_check = [
    ('OPENAI_API_KEY', 'OpenAI (GPT-4, GPT-3.5, etc.)'),
    ('ANTHROPIC_API_KEY', 'Anthropic (Claude)'),
    ('GOOGLE_API_KEY', 'Google (Gemini)'),
    ('TOGETHER_API_KEY', 'Together AI'),
]

found_keys = []
missing_keys = []

for key_name, description in keys_to_check:
    value = os.getenv(key_name, '')

    if value and not value.startswith('sk-your-') and not value.startswith('AIza-your-'):
        # Key is set and not placeholder
        # Show first 10 and last 10 characters
        masked_value = f"{value[:10]}...{value[-10:]}"
        print(f"✅ {key_name}")
        print(f"   Provider: {description}")
        print(f"   Value: {masked_value}")
        print()
        found_keys.append(key_name)
    else:
        print(f"⚠️  {key_name}")
        print(f"   Provider: {description}")
        print(f"   Status: Not set or placeholder")
        print()
        missing_keys.append(key_name)

# Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()

if found_keys:
    print(f"✅ Found {len(found_keys)} API key(s):")
    for key in found_keys:
        print(f"   • {key}")
    print()

if missing_keys:
    print(f"⚠️  Missing {len(missing_keys)} API key(s):")
    for key in missing_keys:
        print(f"   • {key}")
    print()
    print("💡 To add API keys:")
    print("   1. Edit .env file")
    print("   2. Replace placeholder values with your actual keys")
    print("   3. Re-run this script to verify")
    print()

# Test recommendations
print("=" * 70)
print("RECOMMENDED TESTS")
print("=" * 70)
print()

if 'OPENAI_API_KEY' in found_keys:
    print("✅ You can run tests with real OpenAI LLM:")
    print("   python3 run_comprehensive_tests.py --llm")
    print("   python3 tests/llm_test_client.py")
    print()
else:
    print("ℹ️  Using mock LLM clients (no API keys needed):")
    print("   python3 run_comprehensive_tests.py --quick")
    print()

if len(found_keys) >= 2:
    print("✅ You can test multi-LLM consensus:")
    print("   # Edit your test to use llm_mode='multi'")
    print("   # This enables Dawid-Skene consensus with multiple LLMs")
    print()

print("=" * 70)
