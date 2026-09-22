# Telemetry Verification Plan & Attack Simulation Matrix

## 1. Scope & Objectives
The Telemetry Verification Plan defines synthetic negative injection tests to validate the fail-closed behavior of the sanitization gate, the schema validator, and the tenant isolation boundary.

---

## 2. Test Execution Matrix

| Test Suite Identifier | Target Vector | Injection Payload / Condition | Expected Result | Hard Gate Pass Criteria |
|---|---|---|---|---|
| `TEST_PII_01_PHONE` | PII Leakage | Injecting Iranian mobile `09123456789` in payload | Dropped by Sanitizer | HTTP 204 / Dropped, 0 bytes in Redis |
| `TEST_PII_02_NATIONAL_ID`| PII Leakage | Injecting 10-digit national code `0012345678` | Dropped by Sanitizer | Payload dropped, alert logged |
| `TEST_PII_03_EMAIL` | PII Leakage | Injecting personal email `student@example.com` | Dropped by Sanitizer | Payload dropped, clean quarantine |
| `TEST_EVAL_01_SCORE` | Anti-Evaluation | Injecting key `student_score: 95` | Dropped by Evaluation Gate | Immediate reject, Anti-Eval invariant holds |
| `TEST_EVAL_02_RANK` | Anti-Evaluation | Injecting `rank: "1st"` or `class_rank: 5` | Dropped by Evaluation Gate | Immediate reject |
| `TEST_EVAL_03_LABEL` | Anti-Evaluation | Injecting `capability: "slow_learner"` | Dropped by Evaluation Gate | Immediate reject |
| `TEST_SCHEMA_01_EXTRA_PROP`| Schema Strictness | Injecting unlisted property `extra_debug: true` | Rejected by Schema Gate | Rejection (`additionalProperties: false`) |
| `TEST_TENANT_01_RAW_ID` | Multi-Tenant Gate | Submitting raw integer tenant ID instead of hash | Rejected by Schema Gate | Rejection (`pattern: ^[a-f0-9]{64}$`) |
| `TEST_RATE_LIMIT_01` | DOS Protection | Dispatching 150 events in 30 seconds | Rate Limiter Clamped | Events > 100 dropped cleanly |

---

## 3. Automated Harness Implementation
- Automated validation is codified in `test_wave514_phase2_telemetry_harness.py`.
- Tests run against mock sanitization pipelines ensuring 100% pass rates before Phase 2 acceptance.
