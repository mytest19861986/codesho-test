import re
import unittest
import uuid
from datetime import datetime, timezone

# Canonical regex and token rules from ADR-057 and TELEMETRY_EVENT_SCHEMA.md
PII_PATTERNS = [
    re.compile(r'09\d{9}'), # Iranian mobile numbers
    re.compile(r'\d{10}'),   # 10-digit National IDs
    re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'), # Email
]

FORBIDDEN_EVALUATION_TOKENS = {
    'score', 'scoring', 'student_score',
    'rank', 'ranking', 'class_rank',
    'grade', 'grading', 'mark',
    'iq', 'capability', 'slow_learner', 'fast_learner'
}

class TelemetrySanitizerEngine:
    @staticmethod
    def sanitize_and_validate(event: dict) -> bool:
        # Check required top-level fields
        required_fields = {"event_id", "schema_version", "event_type", "timestamp_utc", "tenant_hash", "payload"}
        if set(event.keys()) != required_fields:
            return False # Reject extra or missing properties

        # Tenant hash must be 64-char hex
        if not re.match(r'^[a-f0-9]{64}$', str(event.get("tenant_hash", ""))):
            return False

        # Recursively inspect payload strings for PII and Evaluation tokens
        def inspect(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    k_lower = str(k).lower()
                    if any(tok in k_lower for tok in FORBIDDEN_EVALUATION_TOKENS):
                        return False
                    if not inspect(v):
                        return False
            elif isinstance(obj, list):
                for item in obj:
                    if not inspect(item):
                        return False
            elif isinstance(obj, str):
                s_lower = obj.lower()
                if any(tok in s_lower for tok in FORBIDDEN_EVALUATION_TOKENS):
                    return False
                for pattern in PII_PATTERNS:
                    if pattern.search(obj):
                        return False
            return True

        return inspect(event["payload"])

class TestWave514Phase2TelemetryHarness(unittest.TestCase):
    def get_valid_base_event(self):
        return {
            "event_id": str(uuid.uuid4()),
            "schema_version": "1.0.0",
            "event_type": "PLATFORM_LATENCY_OBSERVED",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "tenant_hash": "a" * 64,
            "payload": {
                "metric_name": "api_p95_ms",
                "metric_value": 85.5,
                "role_context": "STUDENT",
                "route_canonical": "/student/dashboard"
            }
        }

    def test_nominal_valid_event(self):
        event = self.get_valid_base_event()
        self.assertTrue(TelemetrySanitizerEngine.sanitize_and_validate(event))

    def test_pii_injection_mobile_number(self):
        event = self.get_valid_base_event()
        event["payload"]["error_code"] = "ERR_09123456789"
        self.assertFalse(TelemetrySanitizerEngine.sanitize_and_validate(event))

    def test_pii_injection_national_id(self):
        event = self.get_valid_base_event()
        event["payload"]["route_canonical"] = "/student/0012345678"
        self.assertFalse(TelemetrySanitizerEngine.sanitize_and_validate(event))

    def test_pii_injection_email(self):
        event = self.get_valid_base_event()
        event["payload"]["route_canonical"] = "/student/learner@codesho.ir"
        self.assertFalse(TelemetrySanitizerEngine.sanitize_and_validate(event))

    def test_evaluation_token_injection_score(self):
        event = self.get_valid_base_event()
        event["payload"]["student_score"] = 98.0
        self.assertFalse(TelemetrySanitizerEngine.sanitize_and_validate(event))

    def test_evaluation_token_injection_rank(self):
        event = self.get_valid_base_event()
        event["payload"]["class_rank"] = 2
        self.assertFalse(TelemetrySanitizerEngine.sanitize_and_validate(event))

    def test_evaluation_token_injection_slow_learner(self):
        event = self.get_valid_base_event()
        event["payload"]["metric_name"] = "slow_learner"
        self.assertFalse(TelemetrySanitizerEngine.sanitize_and_validate(event))

    def test_schema_strictness_extra_properties(self):
        event = self.get_valid_base_event()
        event["unauthorized_field"] = "malicious_probe"
        self.assertFalse(TelemetrySanitizerEngine.sanitize_and_validate(event))

    def test_tenant_isolation_raw_id_rejected(self):
        event = self.get_valid_base_event()
        event["tenant_hash"] = "tenant_123" # Not a 64-char hex string
        self.assertFalse(TelemetrySanitizerEngine.sanitize_and_validate(event))

if __name__ == '__main__':
    unittest.main()
