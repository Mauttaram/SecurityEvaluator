"""
SQL Injection Scenario - Adapter for the Unified Framework.

Implements the SecurityScenario interface for SQL Injection evaluation.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import json
import random

from ..base import SecurityScenario, PurpleAgent, Mutator, Validator
from ..models import (
    Attack, TestResult, TestOutcome, Severity,
    create_attack_id, create_result_id, calculate_outcome
)


# ============================================================================
# SQL INJECTION MUTATORS
# ============================================================================

class EncodingMutator(Mutator):
    """Mutates SQL injection payloads using encoding techniques."""

    def mutate(self, attack: Attack) -> List[Attack]:
        """Generate encoding mutations."""
        if not isinstance(attack.payload, str):
            return []

        mutations = []
        payload = attack.payload

        # URL encoding
        url_encoded = ''.join(f'%{ord(c):02x}' if c in "' \"" else c for c in payload)
        mutations.append(self._create_mutation(attack, url_encoded, 'url_encoding'))

        # Hex encoding for quotes
        hex_encoded = payload.replace("'", "0x27").replace('"', "0x22")
        mutations.append(self._create_mutation(attack, hex_encoded, 'hex_encoding'))

        # Unicode encoding
        unicode_encoded = ''.join(f'\\u{ord(c):04x}' if c in "' \"" else c for c in payload)
        mutations.append(self._create_mutation(attack, unicode_encoded, 'unicode_encoding'))

        return mutations

    def _create_mutation(self, base: Attack, payload: str, encoding: str) -> Attack:
        """Create mutated attack."""
        return Attack(
            attack_id=create_attack_id('sql_injection', base.technique, datetime.now()),
            scenario='sql_injection',
            technique=base.technique,
            payload=payload,
            metadata={
                **base.metadata,
                'mutation': encoding,
                'parent_id': base.attack_id
            },
            is_malicious=base.is_malicious,
            parent_attack_id=base.attack_id,
            generation=base.generation + 1,
            mutation_type='encoding'
        )

    def get_mutation_type(self) -> str:
        return 'encoding'


class ObfuscationMutator(Mutator):
    """Mutates SQL injection payloads using obfuscation techniques."""

    def mutate(self, attack: Attack) -> List[Attack]:
        """Generate obfuscation mutations."""
        if not isinstance(attack.payload, str):
            return []

        mutations = []
        payload = attack.payload

        # Case variation
        case_varied = ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(payload))
        mutations.append(self._create_mutation(attack, case_varied, 'case_variation'))

        # Comment injection
        comment_injected = payload.replace(' ', '/**/')
        mutations.append(self._create_mutation(attack, comment_injected, 'comment_injection'))

        # Whitespace variation
        whitespace_varied = payload.replace(' ', '\t')
        mutations.append(self._create_mutation(attack, whitespace_varied, 'whitespace_variation'))

        return mutations

    def _create_mutation(self, base: Attack, payload: str, obfuscation: str) -> Attack:
        """Create mutated attack."""
        return Attack(
            attack_id=create_attack_id('sql_injection', base.technique, datetime.now()),
            scenario='sql_injection',
            technique=base.technique,
            payload=payload,
            metadata={
                **base.metadata,
                'mutation': obfuscation,
                'parent_id': base.attack_id
            },
            is_malicious=base.is_malicious,
            parent_attack_id=base.attack_id,
            generation=base.generation + 1,
            mutation_type='obfuscation'
        )

    def get_mutation_type(self) -> str:
        return 'obfuscation'


class AdvancedSQLMutator(Mutator):
    """Advanced SQL-specific mutations."""

    def mutate(self, attack: Attack) -> List[Attack]:
        """Generate advanced SQL mutations."""
        if not isinstance(attack.payload, str):
            return []

        mutations = []
        payload = attack.payload

        # NULL byte injection
        null_injected = payload.replace("'", "'%00")
        mutations.append(self._create_mutation(attack, null_injected, 'null_byte'))

        # Inline comments
        inline_commented = payload.replace('OR', 'O/**/R').replace('AND', 'A/**/ND')
        mutations.append(self._create_mutation(attack, inline_commented, 'inline_comments'))

        # Concatenation
        if "'" in payload:
            concat = payload.replace("'", "CHAR(39)")
            mutations.append(self._create_mutation(attack, concat, 'char_concatenation'))

        return mutations

    def _create_mutation(self, base: Attack, payload: str, technique: str) -> Attack:
        """Create mutated attack."""
        return Attack(
            attack_id=create_attack_id('sql_injection', base.technique, datetime.now()),
            scenario='sql_injection',
            technique=base.technique,
            payload=payload,
            metadata={
                **base.metadata,
                'mutation': technique,
                'parent_id': base.attack_id
            },
            is_malicious=base.is_malicious,
            parent_attack_id=base.attack_id,
            generation=base.generation + 1,
            mutation_type='advanced_sql'
        )

    def get_mutation_type(self) -> str:
        return 'advanced_sql'


# ============================================================================
# SQL INJECTION VALIDATORS
# ============================================================================

class SQLSyntaxValidator(Validator):
    """Validates SQL syntax correctness."""

    def validate(self, attack: Attack) -> Tuple[bool, Optional[str]]:
        """Validate SQL syntax."""
        if not isinstance(attack.payload, str):
            return False, "Payload must be string"

        payload = attack.payload

        # Basic syntax checks
        if not payload.strip():
            return False, "Empty payload"

        # Check for common SQL keywords
        sql_keywords = ['SELECT', 'UNION', 'OR', 'AND', 'WHERE', 'INSERT', 'UPDATE', 'DELETE']
        has_sql = any(keyword in payload.upper() for keyword in sql_keywords)

        # Check for quotes (required for injection)
        has_quotes = "'" in payload or '"' in payload

        if not has_sql and not has_quotes:
            return False, "No SQL injection indicators found"

        return True, None

    def get_validator_type(self) -> str:
        return 'syntax'


class SQLSemanticValidator(Validator):
    """Validates semantic correctness of SQL injection."""

    def validate(self, attack: Attack) -> Tuple[bool, Optional[str]]:
        """Validate semantic correctness."""
        if not isinstance(attack.payload, str):
            return False, "Payload must be string"

        payload = attack.payload

        # Check for balanced quotes
        single_quotes = payload.count("'")
        double_quotes = payload.count('"')

        # Should have odd number of quotes for injection (unclosed quote attack)
        # OR even number for properly closed quotes

        # Check for logical structure
        if 'OR' in payload.upper():
            # OR-based injection should have comparison
            if '=' not in payload:
                return False, "OR-based injection missing comparison"

        if 'UNION' in payload.upper():
            # UNION-based should have SELECT
            if 'SELECT' not in payload.upper():
                return False, "UNION-based injection missing SELECT"

        return True, None

    def get_validator_type(self) -> str:
        return 'semantic'


# ============================================================================
# SQL INJECTION SCENARIO
# ============================================================================

class SQLInjectionScenario(SecurityScenario):
    """
    SQL Injection scenario implementation.

    Provides SQL injection-specific attack techniques, mutators, and validators.
    """

    def __init__(self, dataset_path: Optional[str] = None):
        """
        Initialize SQL injection scenario.

        Args:
            dataset_path: Optional path to baseline dataset
        """
        self.dataset_path = dataset_path
        self._baseline_dataset = None

        # Load baseline dataset
        if dataset_path:
            self._load_baseline_dataset()
        else:
            # Load default samples if no dataset provided
            self._baseline_dataset = self._create_default_samples()

    def get_name(self) -> str:
        """Return scenario name."""
        return 'sql_injection'

    def get_techniques(self) -> List[str]:
        """Return SQL injection techniques."""
        return [
            'union_based',
            'error_based',
            'boolean_based_blind',
            'time_based_blind',
            'stacked_queries',
            'out_of_band',
            'second_order'
        ]

    def get_mutators(self) -> List[Mutator]:
        """Return SQL injection mutators."""
        return [
            EncodingMutator(),
            ObfuscationMutator(),
            AdvancedSQLMutator()
        ]

    def get_validators(self) -> List[Validator]:
        """Return SQL injection validators."""
        return [
            SQLSyntaxValidator(),
            SQLSemanticValidator()
        ]

    def create_attack(
        self,
        technique: str,
        payload: Any,
        metadata: Dict[str, Any]
    ) -> Attack:
        """Create SQL injection attack."""
        return Attack(
            attack_id=create_attack_id('sql_injection', technique, datetime.now()),
            scenario='sql_injection',
            technique=technique,
            payload=payload,
            metadata=metadata,
            is_malicious=metadata.get('is_malicious', True),
            severity=Severity.HIGH if metadata.get('is_malicious', True) else Severity.LOW,
            expected_detection=metadata.get('expected_detection', True)
        )

    def execute_attack(self, attack: Attack, target: PurpleAgent) -> TestResult:
        """Execute SQL injection attack against purple agent."""
        # Call purple agent's detect method
        result = target.detect(attack)
        return result

    def get_mitre_mapping(self) -> Dict[str, List[str]]:
        """Return MITRE ATT&CK mapping."""
        return {
            'union_based': ['T1190'],  # Exploit Public-Facing Application
            'error_based': ['T1190'],
            'boolean_based_blind': ['T1190', 'T1499'],  # Endpoint Denial of Service
            'time_based_blind': ['T1190', 'T1499'],
            'stacked_queries': ['T1190', 'T1059.004'],  # Command and Scripting Interpreter: Unix Shell
            'out_of_band': ['T1190', 'T1071'],  # Application Layer Protocol
            'second_order': ['T1190', 'T1055']  # Process Injection
        }

    def get_baseline_dataset(self) -> Optional[List[Attack]]:
        """Return baseline attack dataset."""
        return self._baseline_dataset

    def _load_baseline_dataset(self):
        """Load baseline dataset from file."""
        # TODO: Implement dataset loading
        # For now, create some default samples
        self._baseline_dataset = self._create_default_samples()

    def _create_default_samples(self) -> List[Attack]:
        """Create default attack samples."""
        samples = []

        # Union-based samples
        union_payloads = [
            "' UNION SELECT NULL, NULL--",
            "' UNION SELECT username, password FROM users--",
            "1' UNION SELECT table_name FROM information_schema.tables--"
        ]

        for payload in union_payloads:
            attack = self.create_attack(
                technique='union_based',
                payload=payload,
                metadata={'source': 'default', 'is_malicious': True}
            )
            samples.append(attack)

        # Boolean-based blind samples
        boolean_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "admin' AND '1'='1",
        ]

        for payload in boolean_payloads:
            attack = self.create_attack(
                technique='boolean_based_blind',
                payload=payload,
                metadata={'source': 'default', 'is_malicious': True}
            )
            samples.append(attack)

        # Time-based blind samples
        time_payloads = [
            "'; WAITFOR DELAY '00:00:05'--",
            "' OR SLEEP(5)--",
            "'; SELECT pg_sleep(5)--"
        ]

        for payload in time_payloads:
            attack = self.create_attack(
                technique='time_based_blind',
                payload=payload,
                metadata={'source': 'default', 'is_malicious': True}
            )
            samples.append(attack)

        # Safe samples (should not be detected)
        safe_payloads = [
            "SELECT * FROM users WHERE id=1",
            "INSERT INTO logs (message) VALUES ('test')",
            "UPDATE users SET name='John' WHERE id=1"
        ]

        for payload in safe_payloads:
            attack = Attack(
                attack_id=create_attack_id('sql_injection', 'safe', datetime.now()),
                scenario='sql_injection',
                technique='safe',
                payload=payload,
                metadata={'source': 'default', 'is_malicious': False},
                is_malicious=False,
                expected_detection=False
            )
            samples.append(attack)

        return samples


# ============================================================================
# SQL INJECTION PURPLE AGENT (ADAPTER)
# ============================================================================

class SQLInjectionPurpleAgent(PurpleAgent):
    """
    Adapter for existing Purple Agent implementations.

    Wraps any SQL injection detector to work with the unified framework.
    """

    def __init__(self, name: str, detector_function: callable):
        """
        Initialize purple agent adapter.

        Args:
            name: Agent name
            detector_function: Function(payload: str) -> Dict with keys:
                - is_vulnerable: bool
                - confidence: float
                - explanation: str (optional)
        """
        self.name = name
        self.detector_function = detector_function

    def detect(self, attack: Attack) -> TestResult:
        """
        Detect SQL injection attack.

        Args:
            attack: Attack to test

        Returns:
            Test result
        """
        # Convert attack to payload string
        payload = str(attack.payload)

        # Call detector
        try:
            detection = self.detector_function(payload)
            detected = detection.get('is_vulnerable', False)
            confidence = detection.get('confidence', 0.5)
            explanation = detection.get('explanation', '')

        except Exception as e:
            # Detector failed
            detected = False
            confidence = 0.0
            explanation = f"Detector error: {e}"

        # Calculate outcome
        outcome = calculate_outcome(attack, detected)

        # Create test result
        result = TestResult(
            result_id=create_result_id(attack.attack_id, self.name, datetime.now()),
            attack_id=attack.attack_id,
            purple_agent=self.name,
            detected=detected,
            confidence=confidence,
            detection_reason=explanation,
            outcome=outcome
        )

        return result

    def get_name(self) -> str:
        """Return agent name."""
        return self.name

    def reset(self):
        """Reset agent state."""
        # Most detectors are stateless
        pass


# ============================================================================
# SIMPLE PATTERN-BASED PURPLE AGENT (BASELINE)
# ============================================================================

class SimplePatternPurpleAgent(SQLInjectionPurpleAgent):
    """
    Simple pattern-based SQL injection detector.

    Baseline implementation for testing.
    """

    def __init__(self):
        """Initialize simple detector."""
        self.patterns = [
            "' OR '",
            "' OR 1=1",
            "UNION SELECT",
            "--",
            "/*",
            "';",
            "WAITFOR DELAY",
            "SLEEP(",
            "pg_sleep(",
            "DROP TABLE",
            "DELETE FROM",
            "INSERT INTO",
            "UPDATE ",
            "EXEC(",
            "EXECUTE(",
        ]

        super().__init__(
            name="SimplePatternDetector",
            detector_function=self._detect_patterns
        )

    def _detect_patterns(self, payload: str) -> Dict[str, Any]:
        """Detect SQL injection using simple patterns."""
        payload_upper = payload.upper()

        # Check for patterns
        detected_patterns = []
        for pattern in self.patterns:
            if pattern.upper() in payload_upper:
                detected_patterns.append(pattern)

        is_vulnerable = len(detected_patterns) > 0
        confidence = min(1.0, len(detected_patterns) * 0.3)  # Max 1.0

        return {
            'is_vulnerable': is_vulnerable,
            'confidence': confidence,
            'explanation': f"Detected patterns: {detected_patterns}" if detected_patterns else "No patterns detected",
            'patterns': detected_patterns
        }
