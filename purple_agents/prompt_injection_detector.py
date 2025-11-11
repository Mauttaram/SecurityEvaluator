"""
Example Purple Agent for Prompt Injection Detection.

This is a baseline detector using pattern matching and heuristics
to detect various types of prompt injection attacks.
"""

import re
from typing import Dict, Any, List
from datetime import datetime

# If running standalone
try:
    from framework.base import PurpleAgent
    from framework.models import Attack, TestResult, DetectionOutcome
except ImportError:
    # Standalone mode - define minimal interfaces
    class Attack:
        def __init__(self, attack_id, payload, is_attack, **kwargs):
            self.attack_id = attack_id
            self.payload = payload
            self.is_attack = is_attack

    class TestResult:
        def __init__(self, attack, detected, confidence, outcome, **kwargs):
            self.attack = attack
            self.detected = detected
            self.confidence = confidence
            self.outcome = outcome

    class PurpleAgent:
        pass

    class DetectionOutcome:
        TRUE_POSITIVE = "true_positive"
        FALSE_NEGATIVE = "false_negative"
        FALSE_POSITIVE = "false_positive"
        TRUE_NEGATIVE = "true_negative"


class PromptInjectionDetector(PurpleAgent):
    """
    Baseline prompt injection detector using pattern matching.

    Detection Methods:
    1. Pattern Matching - Regex for known injection patterns
    2. Keyword Analysis - Suspicious keyword detection
    3. Structural Analysis - Unusual prompt structure
    4. Encoding Detection - Base64, hex, special tokens
    5. Length Heuristics - Abnormally long/complex prompts
    """

    def __init__(self, sensitivity: str = "medium"):
        """
        Initialize detector.

        Args:
            sensitivity: Detection sensitivity ("low", "medium", "high")
        """
        super().__init__()
        self.sensitivity = sensitivity

        # Define detection patterns
        self._init_patterns()

    def _init_patterns(self):
        """Initialize detection patterns for each attack category."""

        # ================================================================
        # 1. JAILBREAK PATTERNS
        # ================================================================
        self.jailbreak_patterns = [
            r"\b(ignore|disregard|forget|dismiss)\s+(all\s+)?(previous|prior|earlier)\s+(instructions?|rules?|guidelines?|directives?)",
            r"\byou\s+are\s+now\s+(a\s+|an\s+)?(\w+\s+)?(DAN|dan|developer|unrestricted|unfiltered)",
            r"\b(developer|debug|admin|root)\s+mode",
            r"\b(disable|turn\s+off|deactivate)\s+(all\s+)?(safety|ethical|moral|filter)",
            r"(pretend|act|behave)\s+as\s+(if\s+)?you\s+(are|have|had)\s+(no|zero)\s+(restrictions?|limitations?|constraints?|ethics?)",
            r"\bDAN\s*\(Do\s+Anything\s+Now\)",
        ]

        # ================================================================
        # 2. PROMPT LEAKING PATTERNS
        # ================================================================
        self.prompt_leak_patterns = [
            r"\b(repeat|show|display|output|print|reveal)\s+(the\s+|your\s+)?(instructions?|prompts?|system\s+prompts?)",
            r"(what|tell\s+me)\s+(were|are)\s+your\s+(initial|original|system|first)\s+(instructions?|prompts?)",
            r"\b(show|display|output)\s+(your\s+)?(configuration|settings|setup|parameters)",
            r"\benter\s+(debug|diagnostic|verbose)\s+mode",
            r"\bsummarize\s+(everything|all)\s+you\s+were\s+told",
        ]

        # ================================================================
        # 3. ROLE MANIPULATION PATTERNS
        # ================================================================
        self.role_manip_patterns = [
            r"\byou\s+are\s+now\s+(a\s+|an\s+)?(python|javascript|sql|bash|shell)\s+(interpreter|executor|engine)",
            r"\b(execute|run|eval|interpret):\s*(import|require|SELECT|DROP|rm\s+-rf)",
            r"\b(assume|take|switch\s+to|become)\s+(admin|root|administrator|superuser|system)\s+(privileges?|rights?|access|role)",
            r"\bswitch\s+roles?:\s+you\s+are\s+now\s+a\s+(\w+\s+)?(malicious|hacker|attacker)",
        ]

        # ================================================================
        # 4. INSTRUCTION OVERRIDE PATTERNS
        # ================================================================
        self.instruction_override_patterns = [
            r"\b(ignore|disregard|forget|dismiss|override)\s+all\s+(previous|prior|earlier)",
            r"\bnew\s+(priority|directive|instruction):",
            r"\bSYSTEM\s+(OVERRIDE|RESET|REBOOT):",
            r"\ball\s+(previous|prior)\s+(constraints?|limitations?|restrictions?)\s+(are|were)\s+(now\s+)?(void|invalid|cancelled)",
        ]

        # ================================================================
        # 5. RESOURCE ABUSE PATTERNS
        # ================================================================
        self.resource_abuse_patterns = [
            r"\b(infinite|endless|unlimited)\s+(list|loop|sequence|generation)",
            r"\brepeat\s+(this|that)\s+(task|operation|command)\s+(recursively|)?\s*\d{3,}",
            r"\bfor\s+each\s+(\w+\s+)?from\s+\d+\s+to\s+(infinity|∞|\d{6,})",
            r"\b(generate|output|compute|calculate)\s+.*\s+(infinitely|forever|endlessly)",
        ]

        # ================================================================
        # 6. DATA EXFILTRATION PATTERNS
        # ================================================================
        self.data_exfil_patterns = [
            r"\b(tell|show|reveal|share|output)\s+(me\s+)?(about\s+)?(examples|data|information)\s+from\s+your\s+training\s+data",
            r"\b(share|reveal|disclose)\s+(details|information)\s+from\s+(your\s+)?(conversations?|chats?)\s+with\s+other\s+users",
            r"\boutput\s+any\s+(PII|personally\s+identifiable\s+information|sensitive\s+data|confidential\s+information)",
            r"\b(leak|expose|reveal)\s+(private|confidential|secret|sensitive)\s+(data|information)",
        ]

        # ================================================================
        # 7. DELIMITER/ENCODING PATTERNS
        # ================================================================
        self.delimiter_patterns = [
            r"<\|endoftext\|>|<\|startoftext\|>",
            r"\[INST\]|\[/INST\]|<<SYS>>|<</SYS>>",
            r"\b(decode|decipher|decrypt)\s+(and\s+)?(execute|run|process):",
            r"\b(base64|b64|hex|unicode|url\s*encoded?):\s*[A-Za-z0-9+/=]{20,}",
        ]

        # ================================================================
        # SUSPICIOUS KEYWORDS
        # ================================================================
        self.suspicious_keywords = [
            "jailbreak", "bypass", "circumvent", "evade",
            "exploit", "vulnerability", "hack", "override",
            "disable safety", "remove restrictions", "unrestricted mode",
        ]

    async def detect(self, attack: Attack) -> TestResult:
        """
        Detect if the prompt contains an injection attempt.

        Args:
            attack: Attack object with payload to analyze

        Returns:
            TestResult with detection outcome and confidence
        """
        prompt = attack.payload
        detected = False
        confidence = 0.0
        detection_reasons = []

        # ================================================================
        # PATTERN MATCHING
        # ================================================================

        # Check each pattern category
        pattern_categories = [
            ("jailbreak", self.jailbreak_patterns, 0.9),
            ("prompt_leak", self.prompt_leak_patterns, 0.8),
            ("role_manip", self.role_manip_patterns, 0.95),
            ("instruction_override", self.instruction_override_patterns, 0.85),
            ("resource_abuse", self.resource_abuse_patterns, 0.7),
            ("data_exfil", self.data_exfil_patterns, 0.9),
            ("delimiter", self.delimiter_patterns, 0.85),
        ]

        for category, patterns, base_confidence in pattern_categories:
            for pattern in patterns:
                if re.search(pattern, prompt, re.IGNORECASE):
                    detected = True
                    confidence = max(confidence, base_confidence)
                    detection_reasons.append(f"{category}_pattern_match")
                    break  # One match per category is enough

        # ================================================================
        # KEYWORD ANALYSIS
        # ================================================================

        keyword_count = sum(
            1 for keyword in self.suspicious_keywords
            if keyword.lower() in prompt.lower()
        )

        if keyword_count >= 2:
            detected = True
            confidence = max(confidence, 0.7)
            detection_reasons.append(f"suspicious_keywords_{keyword_count}")

        # ================================================================
        # STRUCTURAL ANALYSIS
        # ================================================================

        # Check for unusual structure
        has_special_tokens = bool(re.search(r'<\|.*?\|>|\[.*?\]|<<.*?>>', prompt))
        has_system_markers = bool(re.search(r'\b(SYSTEM|USER|ASSISTANT):', prompt, re.IGNORECASE))
        has_encoding_markers = bool(re.search(r'\b(base64|encoded|decrypt):', prompt, re.IGNORECASE))

        if has_special_tokens or has_system_markers:
            detected = True
            confidence = max(confidence, 0.75)
            detection_reasons.append("structural_anomaly")

        if has_encoding_markers:
            detected = True
            confidence = max(confidence, 0.8)
            detection_reasons.append("encoding_detected")

        # ================================================================
        # LENGTH HEURISTICS
        # ================================================================

        # Very long prompts with injection keywords
        if len(prompt) > 500 and keyword_count > 0:
            detected = True
            confidence = max(confidence, 0.6)
            detection_reasons.append("length_heuristic")

        # ================================================================
        # ADJUST BY SENSITIVITY
        # ================================================================

        if self.sensitivity == "high":
            # More aggressive detection
            if keyword_count >= 1:
                detected = True
                confidence = max(confidence, 0.6)
        elif self.sensitivity == "low":
            # Less aggressive - require stronger signals
            if confidence < 0.8:
                detected = False
                confidence = 0.3

        # ================================================================
        # FINAL CONFIDENCE ADJUSTMENT
        # ================================================================

        # If not detected, set low confidence
        if not detected:
            confidence = 0.1

        # ================================================================
        # DETERMINE OUTCOME
        # ================================================================

        if attack.is_attack and detected:
            outcome = DetectionOutcome.TRUE_POSITIVE
        elif attack.is_attack and not detected:
            outcome = DetectionOutcome.FALSE_NEGATIVE
        elif not attack.is_attack and detected:
            outcome = DetectionOutcome.FALSE_POSITIVE
        else:
            outcome = DetectionOutcome.TRUE_NEGATIVE

        # ================================================================
        # RETURN RESULT
        # ================================================================

        return TestResult(
            attack=attack,
            detected=detected,
            confidence=confidence,
            outcome=outcome,
            timestamp=datetime.now(),
            metadata={
                "method": "pattern_matching",
                "sensitivity": self.sensitivity,
                "detection_reasons": detection_reasons,
                "num_reasons": len(detection_reasons)
            }
        )


# ====================================================================
# HTTP Server Interface (for Purple Agent deployment)
# ====================================================================

if __name__ == "__main__":
    import asyncio
    import argparse
    from aiohttp import web

    async def handle_detect(request):
        """HTTP endpoint for detection."""
        data = await request.json()

        # Create attack object from request
        attack = Attack(
            attack_id=data.get("test_case_id", "unknown"),
            payload=data.get("code") or data.get("prompt") or data.get("payload", ""),
            is_attack=True  # Unknown at detection time
        )

        # Run detection
        detector = PromptInjectionDetector(sensitivity="medium")
        result = await detector.detect(attack)

        # Return response
        return web.json_response({
            "is_vulnerable": result.detected,
            "confidence": result.confidence,
            "metadata": result.metadata
        })

    async def main():
        """Start HTTP server."""
        parser = argparse.ArgumentParser(
            description="Prompt Injection Detector - Purple Agent"
        )
        parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
        parser.add_argument("--sensitivity", choices=["low", "medium", "high"], default="medium")
        args = parser.parse_args()

        app = web.Application()
        app.router.add_post("/detect", handle_detect)

        print(f"🛡️  Prompt Injection Detector starting on port {args.port}")
        print(f"   Sensitivity: {args.sensitivity}")
        print(f"   Endpoint: POST http://localhost:{args.port}/detect")

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', args.port)
        await site.start()

        print(f"✅ Ready for evaluations!")

        # Keep running
        await asyncio.Event().wait()

    asyncio.run(main())
