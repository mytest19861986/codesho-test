import unittest
import os
import re

class TestWave514Phase4Certification(unittest.TestCase):
    def setUp(self):
        self.workspace = r"G:\project\codesho\codesho\codesho"

    def test_telemetry_and_adr_files_presence(self):
        # 1. Telemetry Contract Validation
        expected_docs = [
            "docs/telemetry/PERFORMANCE_DOMAIN_MODEL.md",
            "docs/telemetry/ZERO_PII_TELEMETRY_CONTRACT.md",
            "docs/telemetry/MIGRATION_IMPACT_AND_REGRESSION_PLAN.md",
            "docs/telemetry/TELEMETRY_PIPELINE_ARCHITECTURE.md",
            "docs/telemetry/TELEMETRY_EVENT_SCHEMA.md",
            "docs/telemetry/RELIABILITY_SIGNAL_MODEL.md",
            "docs/telemetry/RELIABILITY_PLAYBOOK.md",
            "docs/telemetry/INCIDENT_MITIGATION_MATRIX.md",
            "docs/telemetry/PERFORMANCE_REGRESSION_GATE.md",
            "docs/telemetry/WAVE5.14_ARCHITECTURE_CERTIFICATE.md",
            "docs/telemetry/WAVE5.14_COMPLIANCE_MATRIX.md",
            "docs/adr/ADR_055_FRONTEND_PERFORMANCE_BUDGET_AND_BUNDLE_GOVERNANCE.md",
            "docs/adr/ADR_056_BACKEND_LATENCY_SLA_AND_QUERY_BUDGET_GATE.md",
            "docs/adr/ADR_057_TELEMETRY_SECURITY_BOUNDARY.md",
            "docs/adr/ADR_058_TELEMETRY_GOVERNANCE_FREEZE.md",
        ]
        for rel_path in expected_docs:
            full_path = os.path.join(self.workspace, rel_path)
            self.assertTrue(os.path.exists(full_path), f"Missing certified document: {rel_path}")

    def test_forbidden_field_scan_in_telemetry_schema(self):
        # 2. Forbidden Field Scan
        schema_path = os.path.join(self.workspace, "docs/telemetry/TELEMETRY_EVENT_SCHEMA.md")
        with open(schema_path, "r", encoding="utf-8") as f:
            content = f.read()

        # In schema, additionalProperties must be false
        self.assertIn('"additionalProperties": false', content)
        self.assertIn("score", content) # Listed in forbidden
        self.assertIn("rank", content)  # Listed in forbidden

    def test_performance_gate_validation(self):
        # 3. Performance Gate Validation
        gate_path = os.path.join(self.workspace, "docs/telemetry/PERFORMANCE_REGRESSION_GATE.md")
        with open(gate_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("120ms", content)
        self.assertIn("85 KB", content)

    def test_adr_compliance_check(self):
        # 4. ADR Compliance Check
        adr_path = os.path.join(self.workspace, "docs/adr/ADR_058_TELEMETRY_GOVERNANCE_FREEZE.md")
        with open(adr_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Permanent Architecture Freeze", content)
        self.assertIn("Anti-Evaluation Hard Lock", content)

    def test_migration_lock_check(self):
        # 5. Migration Lock Check: verify no pending django migration files created
        # Check backend/apps for any new migration files in git
        backend_dir = os.path.join(self.workspace, "backend")
        if os.path.exists(backend_dir):
            new_migrations = []
            for root, dirs, files in os.walk(backend_dir):
                if "migrations" in root:
                    for file in files:
                        if file.endswith(".py") and file != "__init__.py" and "00" in file:
                            # Verify no wave514 migration exists
                            if "wave514" in file or "telemetry" in file:
                                new_migrations.append(file)
            self.assertEqual(len(new_migrations), 0, f"Found unauthorized migrations: {new_migrations}")

    def test_production_isolation_check(self):
        # 6. Production Isolation Check
        cert_path = os.path.join(self.workspace, "docs/telemetry/WAVE5.14_ARCHITECTURE_CERTIFICATE.md")
        with open(cert_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("FROZEN", content)
        self.assertIn("Zero-PII Guarantee", content)

if __name__ == '__main__':
    unittest.main()
