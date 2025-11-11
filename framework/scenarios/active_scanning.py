"""
Active Scanning Scenario (MITRE ATT&CK T1595)

Implements active scanning techniques for security evaluation.
This scenario tests a Purple Agent's ability to detect network reconnaissance
through endpoint discovery and infrastructure probing.

MITRE ATT&CK:
- T1595: Active Scanning
- T1595.001: Scanning IP Blocks
- T1595.002: Vulnerability Scanning
- T1595.003: Wordlist Scanning (primary focus)

Techniques:
- Plugin Discovery: Scanning for AI plugin endpoints
- API Discovery: Finding API documentation endpoints
- Well-Known Paths: Common .well-known/ directory enumeration
- Admin Discovery: Finding admin/management interfaces
- Backup Discovery: Looking for backup files
- Config Discovery: Finding configuration files
- Sequential Scan: Sequential path enumeration
- Randomized Scan: Randomized path order to evade detection

NO LLM REQUIRED - This is purely algorithmic scanning.
"""

from typing import List, Optional, Dict, Any
import random
import time
from datetime import datetime
import hashlib

from framework.base import (
    SecurityScenario,
    Mutator,
    Validator,
)
from framework.models import (
    Attack,
    TestResult,
    TestOutcome,
    Severity
)


# ============================================================================
# ATTACK TEMPLATES
# ============================================================================

# Wordlists for different scan types
PLUGIN_DISCOVERY_PATHS = [
    "ai-plugin.json",
    "plugin.json",
    ".well-known/ai-plugin.json",
    "plugins/manifest.json",
    "static/ai-plugin.json",
]

API_DISCOVERY_PATHS = [
    "openapi.json",
    "swagger.json",
    "api-docs",
    "api/v1/docs",
    "docs/api",
    ".well-known/api-configuration",
]

WELLKNOWN_PATHS = [
    ".well-known/agent-card.json",
    ".well-known/security.txt",
    ".well-known/change-password",
    ".well-known/openapi",
]

ADMIN_DISCOVERY_PATHS = [
    "admin",
    "admin/",
    "administrator",
    "wp-admin",
    "phpmyadmin",
    "cpanel",
    "admin.php",
    "admin/login",
]

BACKUP_DISCOVERY_PATHS = [
    "backup.zip",
    "backup.tar.gz",
    "db.sql",
    "database.sql",
    "config.bak",
    ".env.backup",
    "backup/",
]

CONFIG_DISCOVERY_PATHS = [
    ".env",
    "config.json",
    "config.yml",
    "settings.json",
    "app.config",
    "web.config",
]


# ============================================================================
# MUTATORS
# ============================================================================

class ScanPathMutator(Mutator):
    """Mutates scan paths to evade detection."""

    def get_mutation_type(self) -> str:
        return "path_mutation"

    def mutate(self, attack: Attack) -> List[Attack]:
        """Mutate scan paths with variations."""
        mutations = []
        original_path = attack.payload

        # Variation 1: Add/remove trailing slash
        if original_path.endswith('/'):
            new_path = original_path.rstrip('/')
        else:
            new_path = original_path + '/'

        mutations.append(Attack(
            attack_id=f"{attack.attack_id}_slash",
            scenario="active_scanning",
            technique=attack.technique,
            payload=new_path,
            metadata={
                **attack.metadata,
                'mutation': 'slash_variation',
                'mutator': 'ScanPathMutator'
            }
        ))

        # Variation 2: URL encoding
        encoded_path = original_path.replace('/', '%2F')
        mutations.append(Attack(
            attack_id=f"{attack.attack_id}_encoded",
            scenario="active_scanning",
            technique=attack.technique,
            payload=encoded_path,
            metadata={
                **attack.metadata,
                'mutation': 'url_encoded',
                'mutator': 'ScanPathMutator'
            }
        ))

        # Variation 3: Case variation (for case-insensitive servers)
        if '.' in original_path:
            # Only vary the extension
            base, ext = original_path.rsplit('.', 1)
            case_varied = f"{base}.{ext.upper()}"
        else:
            case_varied = original_path.upper()

        mutations.append(Attack(
            attack_id=f"{attack.attack_id}_case",
            scenario="active_scanning",
            technique=attack.technique,
            payload=case_varied,
            metadata={
                **attack.metadata,
                'mutation': 'case_variation',
                'mutator': 'ScanPathMutator'
            }
        ))

        return mutations


class ScanMethodMutator(Mutator):
    """Varies HTTP methods for scanning."""

    def get_mutation_type(self) -> str:
        return "method_variation"

    def mutate(self, attack: Attack) -> List[Attack]:
        """Mutate HTTP methods."""
        mutations = []
        methods = ['HEAD', 'OPTIONS', 'TRACE']

        for method in methods:
            mutations.append(Attack(
                attack_id=f"{attack.attack_id}_{method.lower()}",
                technique=attack.technique,
                payload=attack.payload,
                metadata={
                    **attack.metadata,
                    'http_method': method,
                    'mutator': 'ScanMethodMutator'
                }
            ))

        return mutations


class UserAgentMutator(Mutator):
    """Varies User-Agent headers to evade detection."""

    def get_mutation_type(self) -> str:
        return "user_agent_variation"

    def mutate(self, attack: Attack) -> List[Attack]:
        """Mutate User-Agent headers."""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "curl/7.68.0",
            "python-requests/2.28.0",
            "Googlebot/2.1 (+http://www.google.com/bot.html)",
        ]

        mutations = []
        for idx, ua in enumerate(user_agents):
            mutations.append(Attack(
                attack_id=f"{attack.attack_id}_ua{idx}",
                scenario="active_scanning",
            technique=attack.technique,
                payload=attack.payload,
                metadata={
                    **attack.metadata,
                    'user_agent': ua,
                    'mutator': 'UserAgentMutator'
                }
            ))

        return mutations


class TimingMutator(Mutator):
    """Varies request timing to evade rate-limit detection."""

    def get_mutation_type(self) -> str:
        return "timing_variation"

    def mutate(self, attack: Attack) -> List[Attack]:
        """Add timing variations."""
        timing_patterns = [
            {'delay': 0.5, 'pattern': 'slow'},
            {'delay': 0.1, 'pattern': 'medium'},
            {'delay': 2.0, 'pattern': 'very_slow'},
        ]

        mutations = []
        for timing in timing_patterns:
            mutations.append(Attack(
                attack_id=f"{attack.attack_id}_{timing['pattern']}",
                technique=attack.technique,
                payload=attack.payload,
                metadata={
                    **attack.metadata,
                    'request_delay': timing['delay'],
                    'timing_pattern': timing['pattern'],
                    'mutator': 'TimingMutator'
                }
            ))

        return mutations


# ============================================================================
# VALIDATORS
# ============================================================================

class ScanRealismValidator(Validator):
    """Validates that scan patterns look realistic."""

    def get_validator_type(self) -> str:
        return "realism"

    def validate(self, attack: Attack) -> bool:
        """Check if scan looks realistic."""
        path = attack.payload

        # Check path is not empty
        if not path or len(path) == 0:
            return False

        # Check path length is reasonable
        if len(path) > 500:
            return False

        # Check path doesn't have suspicious patterns
        # (e.g., too many special characters)
        special_chars = sum(1 for c in path if not c.isalnum() and c not in '/-._')
        if special_chars > len(path) * 0.3:  # More than 30% special chars
            return False

        # Check User-Agent if present
        user_agent = attack.metadata.get('user_agent', '')
        if user_agent and len(user_agent) < 5:
            return False

        return True


class RateLimitValidator(Validator):
    """Validates that scan doesn't exceed realistic rate limits."""

    def __init__(self):
        self.request_times = []
        self.max_requests_per_second = 10

    def get_validator_type(self) -> str:
        return "rate_limit"

    def validate(self, attack: Attack) -> bool:
        """Check if request rate is realistic."""
        current_time = time.time()

        # Clean old requests (older than 1 second)
        self.request_times = [t for t in self.request_times if current_time - t < 1.0]

        # Check if we're within rate limit
        if len(self.request_times) >= self.max_requests_per_second:
            return False

        # Add current request time
        self.request_times.append(current_time)

        return True


# ============================================================================
# ACTIVE SCANNING SCENARIO
# ============================================================================

class ActiveScanningScenario(SecurityScenario):
    """
    Active Scanning scenario for MITRE ATT&CK T1595.

    Tests Purple Agent's ability to detect:
    - Endpoint discovery scans
    - API documentation probing
    - Admin interface enumeration
    - Backup file discovery
    - Configuration file exposure
    """

    def get_name(self) -> str:
        """Return scenario name."""
        return "active_scanning"

    def get_techniques(self) -> List[str]:
        """Return list of attack techniques."""
        return [
            "plugin_discovery",
            "api_discovery",
            "wellknown_discovery",
            "admin_discovery",
            "backup_discovery",
            "config_discovery",
            "sequential_scan",
            "randomized_scan",
        ]

    def get_mutators(self) -> List[Mutator]:
        """Return list of mutators."""
        return [
            ScanPathMutator(),
            ScanMethodMutator(),
            UserAgentMutator(),
            TimingMutator(),
        ]

    def get_validators(self) -> List[Validator]:
        """Return list of validators."""
        return [
            ScanRealismValidator(),
            RateLimitValidator(),
        ]

    def create_attack(self, technique: str, **kwargs) -> Attack:
        """Create an attack for the given technique."""
        # Get wordlist based on technique
        wordlist = self._get_wordlist_for_technique(technique)

        # Select a random path from the wordlist
        path = random.choice(wordlist)

        # Create attack ID
        attack_id = hashlib.md5(f"{technique}_{path}_{time.time()}".encode()).hexdigest()[:16]

        # Create attack
        attack = Attack(
            attack_id=attack_id,
            technique=technique,
            payload=path,
            metadata={
                'technique': technique,
                'timestamp': datetime.now().isoformat(),
                'http_method': 'GET',
                'user_agent': 'Mozilla/5.0',
                'mitre_attack_id': 'T1595',
                'mitre_tactic': 'Reconnaissance',
            }
        )

        return attack

    def execute_attack(self, attack: Attack, target) -> TestResult:
        """Execute attack against purple agent."""
        # Purple agent's detect method should return TestResult
        return target.detect(attack)

    def get_baseline_dataset(self) -> Optional[List[Attack]]:
        """Return baseline dataset of attacks."""
        attacks = []

        for technique in self.get_techniques():
            wordlist = self._get_wordlist_for_technique(technique)

            for path in wordlist:
                attack_id = hashlib.md5(f"{technique}_{path}".encode()).hexdigest()[:16]
                attacks.append(Attack(
                    attack_id=attack_id,
                    scenario="active_scanning",
                    technique=technique,
                    payload=path,
                    metadata={
                        'technique': technique,
                        'http_method': 'GET',
                        'user_agent': 'Mozilla/5.0',
                        'mitre_attack_id': 'T1595',
                    }
                ))

        return attacks

    def get_mitre_mapping(self) -> Dict[str, List[str]]:
        """Return MITRE ATT&CK mapping."""
        return {
            'plugin_discovery': ['T1595', 'T1595.003'],
            'api_discovery': ['T1595', 'T1595.003'],
            'wellknown_discovery': ['T1595', 'T1595.003'],
            'admin_discovery': ['T1595', 'T1595.003'],
            'backup_discovery': ['T1595', 'T1595.003'],
            'config_discovery': ['T1595', 'T1595.003'],
            'sequential_scan': ['T1595', 'T1595.001'],
            'randomized_scan': ['T1595', 'T1595.001'],
        }

    def _get_wordlist_for_technique(self, technique: str) -> List[str]:
        """Get wordlist for a specific technique."""
        wordlists = {
            'plugin_discovery': PLUGIN_DISCOVERY_PATHS,
            'api_discovery': API_DISCOVERY_PATHS,
            'wellknown_discovery': WELLKNOWN_PATHS,
            'admin_discovery': ADMIN_DISCOVERY_PATHS,
            'backup_discovery': BACKUP_DISCOVERY_PATHS,
            'config_discovery': CONFIG_DISCOVERY_PATHS,
            'sequential_scan': PLUGIN_DISCOVERY_PATHS + API_DISCOVERY_PATHS,
            'randomized_scan': (
                PLUGIN_DISCOVERY_PATHS +
                API_DISCOVERY_PATHS +
                WELLKNOWN_PATHS +
                ADMIN_DISCOVERY_PATHS
            ),
        }

        return wordlists.get(technique, PLUGIN_DISCOVERY_PATHS)
