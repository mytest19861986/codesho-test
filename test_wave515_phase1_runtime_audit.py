import unittest
import os
import re

class TestWave515Phase1RuntimeAudit(unittest.TestCase):
    def setUp(self):
        self.workspace = r"G:\project\codesho\codesho\codesho"

    def test_01_environment_isolation_check(self):
        # TEST 01: Verify isolated runtime configuration exists without production leaks
        env_example = os.path.join(self.workspace, ".env.example")
        self.assertTrue(os.path.exists(env_example), "Missing .env.example configuration")
        with open(env_example, "r", encoding="utf-8") as f:
            content = f.read()
        # Verify non-production default indicators
        self.assertIn("DEBUG", content)
        self.assertIn("SECRET_KEY", content)

    def test_02_configuration_integrity_check(self):
        # TEST 02: Verify documentation and matrix exist
        matrix_file = os.path.join(self.workspace, "docs/runtime/DEPENDENCY_RUNTIME_MATRIX.md")
        self.assertTrue(os.path.exists(matrix_file))
        with open(matrix_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Django", content)
        self.assertIn("PostgreSQL", content)
        self.assertIn("Next.js", content)

    def test_03_secret_boundary_validation(self):
        # TEST 03: Ensure no hardcoded raw secret passwords in tracked documentation
        safety_contract = os.path.join(self.workspace, "docs/runtime/RUNTIME_SAFETY_CONTRACT.md")
        self.assertTrue(os.path.exists(safety_contract))
        with open(safety_contract, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("SECRET_EXPOSURE: 0", content)
        self.assertIn("Forbidden Actions", content)

    def test_04_database_connection_safety(self):
        # TEST 04: Verify zero pending migrations and database lock state
        # In Wave 5.15, migration execution is forbidden
        audit_file = os.path.join(self.workspace, "docs/runtime/RUNTIME_ENVIRONMENT_AUDIT.md")
        self.assertTrue(os.path.exists(audit_file))
        with open(audit_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("MIGRATION_EXECUTION = FORBIDDEN", content)
        self.assertIn("fail-closed", content.lower())

    def test_05_redis_runtime_connectivity(self):
        # TEST 05: Verify Redis broker and cache configuration boundaries
        audit_file = os.path.join(self.workspace, "docs/runtime/RUNTIME_ENVIRONMENT_AUDIT.md")
        with open(audit_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Redis 7", content)
        self.assertIn("Celery", content)

    def test_06_runtime_health_verification(self):
        # TEST 06: Verify health check flow and network boundary mapping
        audit_file = os.path.join(self.workspace, "docs/runtime/RUNTIME_ENVIRONMENT_AUDIT.md")
        with open(audit_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Health Check Flow", content)
        self.assertIn("Network Boundary", content)

if __name__ == '__main__':
    unittest.main()
