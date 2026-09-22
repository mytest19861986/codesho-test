# ADR-057: Telemetry Security Boundary & Data Sanitization Gate

## Context & Problem Statement
Integrating telemetry ingestion endpoints into multi-tenant education platforms introduces risks of unintended PII leakage, child profile indexing, cross-tenant data pollution, and evaluation token exploitation. A fail-closed architectural boundary must be codified to ensure that operational performance data can never cross into user-identifiable domains or enable student scoring.

## Decision
We enforce **ADR-057: Telemetry Security Boundary & Sanitization Gate**:

1. **Fail-Closed Sanitization Engine**:
   - The ingestion gateway must evaluate every incoming telemetry event before writing to Redis streams.
   - Any payload containing string patterns matching national ID formats, phone numbers, email regex, or forbidden evaluation tokens (`score`, `rank`, `grade`, `eval_label`) must be discarded immediately without returning error details to the client.
2. **Tenant Hash One-Way Anonymization**:
   - Tenant identities are never persisted as raw database IDs. Telemetry payloads must use a one-way HMAC-SHA256 salted hash (`tenant_hash = HMAC(tenant_id, SECRET_SALT)`).
3. **Database Write Isolation**:
   - Telemetry data must never write directly to PostgreSQL relational tables used by product models.
   - Telemetry storage is strictly restricted to ephemeral Redis streams and standalone Prometheus/TSDB collectors.
4. **No Cross-Tenant Querying**:
   - Aggregators operate on anonymized operational buckets; cross-tenant correlation of learner journeys is technically barred by schema design.

## Consequences
- **Positive**:
  - Complete compliance with child privacy protection regulations.
  - 100% enforcement of the Anti-Evaluation Invariant.
  - Zero performance overhead on product relational database.
- **Negative**:
  - Debugging user-specific client errors requires correlation via ephemeral client session IDs rather than direct user profile queries.

## Compliance & Verification
- Verified by automated synthetic security test suites simulating malicious PII and evaluation token injections (`test_wave514_phase2_telemetry_harness.py`).
