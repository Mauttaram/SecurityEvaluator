"""
Scenario implementations for the Unified Framework.

This is the CENTRALIZED location for ALL security scenarios including:
- Web application attacks (SQL Injection, XSS, CSRF, etc.)
- Network attacks (DDoS, Port Scanning, etc.)
- LLM attacks (Prompt Injection, Jailbreak, etc.)
- MITRE ATT&CK techniques (200+ scenarios planned)

Future structure:
    framework/scenarios/
    ├── sql_injection.py
    ├── prompt_injection.py
    ├── web_attacks/       ← XSS, CSRF, Command Injection, etc.
    ├── network_attacks/   ← DDoS, Port Scanning, DNS Tunneling, etc.
    └── mitre/             ← 200+ MITRE ATT&CK scenarios
"""

from .sql_injection import SQLInjectionScenario, SQLInjectionPurpleAgent
from .prompt_injection import PromptInjectionScenario
from .active_scanning import ActiveScanningScenario

__all__ = [
    'SQLInjectionScenario',
    'SQLInjectionPurpleAgent',
    'PromptInjectionScenario',
    'ActiveScanningScenario',
]
