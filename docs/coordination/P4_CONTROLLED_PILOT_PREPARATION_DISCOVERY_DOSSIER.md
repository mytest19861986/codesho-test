# PHASE 4: CONTROLLED PILOT PREPARATION & OPERATIONAL READINESS
# DISCOVERY DOSSIER (آماده‌سازی پایلوت کنترل‌شده و بلوغ عملیاتی)

**Document Identifier**: `P4_CONTROLLED_PILOT_PREPARATION_DISCOVERY_DOSSIER`
**Status**: `DISCOVERY_ACTIVE`
**Phase**: Phase 4 — Controlled Pilot Preparation and Operational Readiness
**Authorization**: `COMMANDER_PHASE4_DISCOVERY_UNLOCK: GRANTED`
**Date**: 2026-09-13

---

## 1. Executive Framing & Strategic Philosophy
Phase 3 established:
- **PRODUCT CAPABILITY**: Full learning, coaching, mentoring, curriculum authoring, and governance features.
- **ENTERPRISE GOVERNANCE**: Delegated administration, legal holds, data lifecycle, and RLS multi-tenancy.
- **TECHNICAL PILOT READINESS**: 100% test coverage, 0 drift, triple fleet certification.

Phase 4 moves strictly away from uncontrolled feature accumulation and focuses on:
`OPERABILITY + DEPLOYABILITY + OBSERVABILITY + CONTROLLED PILOT PREPARATION`.

---

## 2. Hard Governance Boundaries & Non-Goals
During Phase 4 Discovery and Execution, the following invariants are strictly enforced:
- `REAL_CHILD_DATA: 0` (Strictly prohibited; synthetic learner personas only).
- `REAL_GUARDIAN_DATA: 0` (Strictly prohibited).
- `REAL_SMS_EMAIL: 0` (Outbox simulated; no external live carrier invocation).
- `REAL_PAYMENT: 0` (Simulated sandbox gateways only).
- `PRODUCTION_CREDENTIALS: 0` (No production keys or secrets).
- `PRODUCTION_DEPLOY: 0` (Advisory control plane; zero automatic deploy authority).
- `STUDENT_RANKING: 0` (Zero comparative leaderboards or peer competition).
- `PRIVILEGE_SELF_GRANT: DENY` (Dual-custody access enforcement).

---

## 3. Macro Workstream Architecture

### Workstream A: Pilot Environment & Release Engineering
- **Purpose**: Create a controlled, reproducible, non-production Pilot staging environment.
- **Key Discovery Areas**:
  1. **Environment Topology**: Isolated Docker/K8s pilot cluster, tenant namespaces, PostgreSQL 17 primary-replica setup, Redis broker cluster.
  2. **Deployment Pipeline**: Immutable container builds, digest-pinned images, deterministic database migration runs before web ingress switch.
  3. **Release Candidate (RC) Process**: Forward-only semantic versioning (e.g., `v4.0.0-rc1`), automated sanity smoke tests.
  4. **Rollback Mechanics**: Blue/Green traffic routing cutover, migration rollback safety (additive backwards-compatible DDL), zero-downtime draining.
  5. **Health & Readiness Probes**: Deep `/healthz` and `/readyz` probes verifying PostgreSQL RLS, Redis connection pool, and Celery worker heartbeat.
  6. **Configuration Governance**: 12-Factor config via environment variables, secret vault abstraction, strict schema validation on startup.

### Workstream B: Operational Observability & Incident Readiness
- **Purpose**: Make the platform operable, monitorable, and resilient during a controlled Pilot.
- **Key Discovery Areas**:
  1. **Structured Application Telemetry**: OpenTelemetry (OTel) traces, JSON structured log formatting, correlation IDs (`request_id`, `tenant_id`, `trace_id`).
  2. **Health Monitoring & SLOs**: Request latency percentiles (p50, p95, p99), error rate budgets, Celery queue depth and task latency.
  3. **Audit & Event Visibility**: Real-time aggregation of `PrivilegedActionAudit`, `AccessReviewCampaign`, and Outbox transaction dispatch rates.
  4. **Alerting Policies & Runbooks**: Severity model (SEV1 Critical to SEV4 Minor), actionable triage playbooks, automated circuit breakers.
  5. **Failure & Recovery Drills**: Rehearsal of worker kill, cache eviction, database failover, and tenant partition isolation.

### Workstream C: Pilot Identity, Data & Activation Governance
- **Purpose**: Design how a future authorized Pilot would safely introduce real educational organizations, mentors, and students.
- **Key Discovery Areas**:
  1. **Pilot Tenant Provisioning**: Automated onboarding wizard creating tenant workspace, default retention policies, and operator bindings.
  2. **Account Lifecycle & Consent**: Two-party guardian consent workflows, age-appropriate onboarding, granular opt-ins.
  3. **Data-Minimization & Retention Rules**: PII field redaction, automated scheduled purge of ephemeral session telemetry, zero telemetry leakage of minor data.
  4. **Support Escalation & Offboarding**: Secure impersonation with time-bound audit tokens, tenant data export (GDPR compliant), and legal hold override safeguards.

---

## 4. Multi-Agent Fleet Specialization for Phase 4
- **Qwen**: Operational workflows, release FSMs, incident lifecycle states, pilot onboarding boundaries, idempotency, and rollback semantics.
- **GLM**: Pilot environment database roles (`app_role`, `migrator_role`, `readonly_role`), migration execution safety, backup/restore rehearsal, and tenant isolation verification.
- **Gemini**: Operational admin UX, incident dashboard UX, pilot onboarding wizard specifications, WCAG 2.2 AA accessibility, BiDi RTL layout integrity, and cognitive load minimization.
