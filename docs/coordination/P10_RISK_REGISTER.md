# P10 Decision Risk Register

## 1. Risk Evaluation Methodology
Risks are evaluated objectively across Likelihood (Low, Medium, High) and Impact (Low, Medium, High, Critical) with explicit identification of Go-Blocking status.

## 2. Risk Matrix

| Risk ID | Domain | Description | Likelihood | Impact | Mitigation Strategy | Detection Mechanism | Owner Role | Go-Blocking? |
|---|---|---|---|---|---|---|---|---|
| `RSK-01` | Privacy | Accidental admission of sensitive child PII | Low | Critical | Regex DLP, schema admission filter, synthetic-only fixtures | Ingestion audit trips | Data Protection Officer | YES |
| `RSK-02` | Legal | Guardian disputes consent validity post-activation | Medium | High | Dual-custody digital receipts with immutable cryptographic timestamp | Audit ledger lookup | Legal Counsel | YES |
| `RSK-03` | Security | Cross-tenant context leakage under concurrent spikes | Low | Critical | PostgreSQL RLS with `FORCE RLS`, `NOBYPASSRLS`, GUC `app.current_tenant` | Automated RLS negative tests | Lead Security Architect | YES |
| `RSK-04` | Telecom | SMS OTP delivery failure during guardian verification | Medium | Medium | Multi-provider fallback, clear retry limits, local school verification fallback | Delivery webhook latency monitor | Operations Lead | NO (Manager Decision) |
| `RSK-05` | Scope | School administrator adds unauthorized classes | Low | High | Scope Lock immutable SHA-256 digest bound to active token | Token invalidation & 403 response | Operations Lead | YES |
| `RSK-06` | Reliability| Database connection pool exhaustion during peak school hours | Medium | High | PgBouncer transaction pooling, strict bounded queries, read replicas | APM latency & pool alerts | DevOps Engineer | NO (Manager Decision) |
| `RSK-07` | Operations | Operator delays triggering Kill-Switch during anomaly | Low | High | Automated tripwires triggering `EMERGENCY_ABORT` on fatal exceptions | Automated system watchdog | Incident Commander | YES |
| `RSK-08` | Reputation | Negative parent reaction to platform usability | Medium | Medium | Phased rollout (max 50 students), active mentor onboarding support | Daily feedback pulse survey | Product Manager | NO (Manager Decision) |
