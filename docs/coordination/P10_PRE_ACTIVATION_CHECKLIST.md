# P10 Pre-Activation Checklist

> **CRITICAL INVARIANT**: At Phase 10, real-world execution is strictly `PROHIBITED`. This checklist establishes the exact procedural gates that must be satisfied prior to any prospective real activation if and only if the Human Manager later issues an Option A (`GO`) decision.

## 1. Pre-Activation Gate Checklist

- [ ] **Gate 01: Formal Manager Authorization Recorded**
  - Option A (`GO`) form signed and committed to repository with explicit scope fields.
- [ ] **Gate 02: Single Pilot Institution Bound**
  - Exactly one vetted educational institution selected and bound via legal agreement.
- [ ] **Gate 03: Pilot Numerical Limits Hard-Coded in Scope Lock**
  - Student count <= 50, Guardian count <= 50, Duration <= 14 days frozen in SHA-256 digest.
- [ ] **Gate 04: Data Classification Whitelist Enforced**
  - Zero biometric data, zero financial data; only approved educational fields permitted.
- [ ] **Gate 05: Guardian Consent Receipts Generated**
  - Dual-custody immutable digital consent records created and verified prior to student login.
- [ ] **Gate 06: Emergency Kill-Switch Authority Designated**
  - Primary Incident Commander and Secondary Operator assigned credentials with kill-switch authority.
- [ ] **Gate 07: Live Monitoring & APM Tripped Alerts Operational**
  - Prometheus/Grafana real-time metrics and Sentry exception reporting active and verified.
- [ ] **Gate 08: Cold Backup & WAL Archive Verified**
  - Fresh full PostgreSQL 17 backup taken and tested for restore prior to admission of any live data.
- [ ] **Gate 09: Dedicated Telecom Whitelist Configured**
  - SMS gateway restricted strictly to authorized pilot participants to prevent accidental spam.
- [ ] **Gate 10: Rollback & Compensation Scripts Staged**
  - Automated crypto-shredding and database compensation routines staged and verified.
