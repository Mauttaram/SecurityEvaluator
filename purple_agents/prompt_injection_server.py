#!/usr/bin/env python3
"""
Purple Agent HTTP Server - Prompt Injection Detector

Implements A2A protocol for testing with Green Agent.
Production-ready detector service.
"""

import json
import uuid
import argparse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse


class PromptInjectionDetector:
    """
    Production-grade prompt injection detector.

    Uses multiple detection layers:
    1. Pattern matching (known attack patterns)
    2. Structural analysis (instruction override structure)
    3. Semantic analysis (intent classification)
    """

    def __init__(self, strictness: str = "balanced"):
        """
        Initialize detector.

        Args:
            strictness: Detection strictness (loose, balanced, strict)
        """
        self.strictness = strictness
        self.detection_count = 0
        self.total_count = 0

        # Known attack patterns
        self.jailbreak_patterns = [
            "ignore previous instructions",
            "ignore all previous",
            "disregard",
            "forget your training",
            "forget everything",
            "new instructions",
            "override",
            "bypass",
            "developer mode",
            "dan mode",
            "act as",
            "pretend you are",
            "roleplay as"
        ]

        self.prompt_leak_patterns = [
            "system prompt",
            "show me your prompt",
            "reveal your instructions",
            "what are your instructions",
            "print system",
            "show internal",
            "display configuration"
        ]

        self.role_manipulation_patterns = [
            "you are now",
            "switch roles",
            "assume the role",
            "from now on you are",
            "act like you are"
        ]

        self.instruction_override_patterns = [
            "new task:",
            "important:",
            "update:",
            "correction:",
            "\\n\\n===",
            "---\\n",
            "system:",
            "admin:"
        ]

    def detect(self, prompt: str) -> dict:
        """
        Detect prompt injection.

        Args:
            prompt: Input prompt to analyze

        Returns:
            Detection result dict with:
                - detected: bool
                - confidence: float (0-1)
                - reasons: list of detection reasons
                - category: attack category if detected
        """
        self.total_count += 1

        prompt_lower = prompt.lower()
        reasons = []
        confidence_scores = []

        # Layer 1: Jailbreak detection
        jailbreak_matches = [p for p in self.jailbreak_patterns if p in prompt_lower]
        if jailbreak_matches:
            reasons.append(f"Jailbreak patterns: {', '.join(jailbreak_matches[:2])}")
            confidence_scores.append(0.9)

        # Layer 2: Prompt leak detection
        leak_matches = [p for p in self.prompt_leak_patterns if p in prompt_lower]
        if leak_matches:
            reasons.append(f"Prompt leaking: {', '.join(leak_matches[:2])}")
            confidence_scores.append(0.85)

        # Layer 3: Role manipulation detection
        role_matches = [p for p in self.role_manipulation_patterns if p in prompt_lower]
        if role_matches:
            reasons.append(f"Role manipulation: {', '.join(role_matches[:2])}")
            confidence_scores.append(0.8)

        # Layer 4: Instruction override detection
        override_matches = [p for p in self.instruction_override_patterns if p in prompt_lower]
        if override_matches:
            reasons.append(f"Instruction override: {', '.join(override_matches[:2])}")
            confidence_scores.append(0.75)

        # Layer 5: Structural anomalies
        if self._has_structural_anomalies(prompt):
            reasons.append("Structural anomalies detected")
            confidence_scores.append(0.7)

        # Layer 6: Delimiter attacks
        if self._has_delimiter_attacks(prompt):
            reasons.append("Delimiter injection detected")
            confidence_scores.append(0.65)

        # Calculate final confidence
        if confidence_scores:
            # Weighted average (earlier detections have higher weight)
            weights = [1.0 / (i + 1) for i in range(len(confidence_scores))]
            confidence = sum(s * w for s, w in zip(confidence_scores, weights)) / sum(weights)
        else:
            confidence = 0.0

        # Apply strictness threshold
        threshold = self._get_threshold()
        detected = confidence >= threshold

        if detected:
            self.detection_count += 1

        # Determine category
        category = None
        if detected:
            if jailbreak_matches:
                category = "jailbreak"
            elif leak_matches:
                category = "prompt_leak"
            elif role_matches:
                category = "role_manipulation"
            elif override_matches:
                category = "instruction_override"
            else:
                category = "suspicious"

        return {
            'detected': detected,
            'confidence': round(confidence, 3),
            'reasons': reasons,
            'category': category,
            'threshold': threshold
        }

    def _get_threshold(self) -> float:
        """Get detection threshold based on strictness"""
        thresholds = {
            'loose': 0.7,
            'balanced': 0.5,
            'strict': 0.3
        }
        return thresholds.get(self.strictness, 0.5)

    def _has_structural_anomalies(self, prompt: str) -> bool:
        """Detect structural anomalies"""
        # Multiple newlines (potential delimiter injection)
        if '\\n\\n\\n' in prompt or '\n\n\n' in prompt:
            return True

        # Excessive special characters
        special_chars = sum(1 for c in prompt if c in '=*#-_|<>')
        if special_chars > len(prompt) * 0.2:  # > 20% special chars
            return True

        # ALL CAPS sections
        words = prompt.split()
        caps_words = sum(1 for w in words if w.isupper() and len(w) > 3)
        if caps_words > len(words) * 0.3:  # > 30% caps words
            return True

        return False

    def _has_delimiter_attacks(self, prompt: str) -> bool:
        """Detect delimiter injection attacks"""
        delimiters = [
            '"""', "'''", "```", "---", "===", "***",
            "<end>", "</system>", "[INST]", "</s>"
        ]
        return any(delim in prompt for delim in delimiters)

    def get_stats(self) -> dict:
        """Get detector statistics"""
        return {
            'total_prompts': self.total_count,
            'detected': self.detection_count,
            'detection_rate': self.detection_count / self.total_count if self.total_count > 0 else 0.0,
            'strictness': self.strictness
        }


class PurpleAgentHandler(BaseHTTPRequestHandler):
    """HTTP handler for Purple Agent"""

    detector = None  # Shared detector instance

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/detect':
            self.handle_detect()
        else:
            self.send_error(404, "Not Found")

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.handle_health()
        elif self.path == '/stats':
            self.handle_stats()
        elif self.path == '/card' or self.path == '/.well-known/agent-card.json':
            self.handle_agent_card()
        else:
            self.send_error(404, "Not Found")

    def handle_detect(self):
        """Handle detection request"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            request = json.loads(post_data.decode('utf-8'))
            prompt = request.get('prompt', '')

            if not prompt:
                self.send_error(400, "Missing 'prompt' field")
                return

            # Detect
            result = self.detector.detect(prompt)

            # Add metadata
            result['timestamp'] = datetime.now().isoformat()
            result['agent'] = 'PromptInjectionDetector'

            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode())

        except Exception as e:
            self.send_error(500, f"Detection error: {str(e)}")

    def handle_health(self):
        """Handle health check"""
        health = {
            'status': 'healthy',
            'service': 'PromptInjectionDetector',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        }

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(health, indent=2).encode())

    def handle_stats(self):
        """Handle statistics request"""
        stats = self.detector.get_stats()

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(stats, indent=2).encode())

    def handle_agent_card(self):
        """Handle AgentCard request"""
        card = {
            "name": "PromptInjectionDetector",
            "description": "Production-grade prompt injection detector with multi-layer detection",
            "version": "1.0.0",
            "type": "purple_agent",
            "capabilities": [
                "jailbreak_detection",
                "prompt_leak_detection",
                "role_manipulation_detection",
                "instruction_override_detection",
                "structural_anomaly_detection",
                "delimiter_attack_detection"
            ],
            "api_endpoints": {
                "detect": "/detect",
                "health": "/health",
                "stats": "/stats",
                "card": "/.well-known/agent-card.json"
            },
            "detection_layers": 6,
            "strictness_modes": ["loose", "balanced", "strict"]
        }

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(card, indent=2).encode())

    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {format%args}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Purple Agent - Prompt Injection Detector')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--strictness', choices=['loose', 'balanced', 'strict'],
                       default='balanced', help='Detection strictness')
    args = parser.parse_args()

    # Initialize detector
    PurpleAgentHandler.detector = PromptInjectionDetector(strictness=args.strictness)

    # Start server
    server_address = (args.host, args.port)
    httpd = HTTPServer(server_address, PurpleAgentHandler)

    print("=" * 80)
    print("🛡️  Purple Agent - Prompt Injection Detector")
    print("=" * 80)
    print(f"Listening on http://{args.host}:{args.port}")
    print(f"Strictness: {args.strictness}")
    print()
    print("Available endpoints:")
    print(f"  POST http://{args.host}:{args.port}/detect      - Detect prompt injection")
    print(f"  GET  http://{args.host}:{args.port}/health      - Health check")
    print(f"  GET  http://{args.host}:{args.port}/stats       - Detection statistics")
    print(f"  GET  http://{args.host}:{args.port}/card        - AgentCard")
    print()
    print("Example usage:")
    print(f'  curl -X POST http://{args.host}:{args.port}/detect \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"prompt": "Ignore all previous instructions"}\'')
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)
    print()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        httpd.shutdown()


if __name__ == '__main__':
    main()
