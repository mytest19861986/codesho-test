# Phase 7 Discovery: Real Pilot Manager Decision and Admission Preparation
## P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-DISCOVERY

- **Task ID**: `P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-DISCOVERY`
- **Program Mode**: `MACRO_FAST_ENTERPRISE`
- **Authority**: `COMMANDER_P7_DISCOVERY_AUTHORIZATION` (Commit `13cae17`)
- **Core Objective**: Prepare the complete, auditable, fail-closed Manager Decision Package for Human Manager determination (`GO` / `NO_GO` / `DEFER`).
- **Core Policy**: Phase 7 SHALL NOT activate the Real Pilot.

---

### Invariants & Locked Manager Boundaries (Fail-Closed)
| Gate / Invariant | Status | Enforcement Mechanism |
| :--- | :--- | :--- |
| `REAL_PILOT` | **`LOCKED`** | Manager-controlled only; no autonomous unlocking |
| `REAL_DATA` | **`LOCKED`** | Ingestion pipeline rejects non-synthetic schemas |
| `REAL_CHILD_DATA` | **`0`** | Hard block at schema and serializer validation |
| `REAL_GUARDIAN_DATA` | **`0`** | Hard block; strictly synthetic guardian profiles |
| `REAL_PII` | **`0`** | Regex and DLP scanners trigger SEV1 halt |
| `REAL_CONSENT_ACTIVATION` | **`LOCKED`** | Consent engine operates in rehearsal sandbox |
| `REAL_SMS_EMAIL` | **`LOCKED`** | Mock provider; zero egress to real telecom/SMTP |
| `REAL_PAYMENT` | **`LOCKED`** | Zero real IRR minor units transactions |
| `PRODUCTION` | **`LOCKED`** | Isolated to test/staging environments |
| `MERGE_TO_MAIN` | **`LOCKED_FOR_MANAGER`** | Work confined to `codesho-test` |
| `PRODUCTION_CREDENTIALS` | **`0`** | Zero production secrets committed or loaded |

---

### Workstream Breakdown

#### P7-WS1: Candidate Organization Due Diligence Model
- **Objective**: Establish structured, objective eligibility criteria for prospective pilot organizations.
- **Components**:
  - Organizational legal readiness checklist (school / educational center accreditation).
  - Technical infrastructure assessment (LAN, device specifications, browser compatibility).
  - Operator competence qualification (administrative staff trained on cockpit controls).
  - Dedicated pilot champion designation and dual-custody approval pairing.

#### P7-WS2: Real Pilot Scope Envelope Proposal
- **Objective**: Formulate the bounded, conservative parameters for the real pilot for Manager approval.
- **Components**:
  - Maximum organization limit: 1 accredited organization.
  - Maximum authorized operators: Up to 5 qualified operators.
  - Maximum learner cohort: Up to 50 learners (ages 13–19, verified parental consent).
  - Maximum guardian cohort: Up to 50 verified guardians.
  - Geographical / Network boundaries: Defined IP allowlist / closed campus perimeter.
  - **Explicit Note**: All figures are recommendations requiring Human Manager sign-off.

#### P7-WS3: Legal, Privacy & Real Data Admission Readiness
- **Objective**: Ensure complete compliance with child privacy protection laws and zero-unauthorized-data policies.
- **Components**:
  - Persian / BiDi parental consent agreement legal text and cryptographic signing workflow.
  - Age verification protocol (ensuring 13–19 bracket compliance).
  - Data minimization charter: Zero tracking cookies, zero student ranking, zero external AI at runtime.
  - Explicit crypto-shredding keys lifecycle for instantaneous "Right to be Forgotten" execution.

#### P7-WS4: Production & Operational Admission Readiness
- **Objective**: Guarantee zero-downtime, fault-tolerant infrastructure and fail-closed operational readiness.
- **Components**:
  - PostgreSQL 17.10 cluster configuration with strict RLS (`FORCE ROW LEVEL SECURITY`, `NOBYPASSRLS`).
  - Automated continuous backup verification and Point-In-Time Recovery (PITR) RTO/RPO targets.
  - Dual-custody operational runbooks for incident management and privilege escalation.
  - Real-time observability: Sentry error alerting, Redis queue latency, audit log immutability.

#### P7-WS5: Human Manager Go/No-Go Decision Package
- **Objective**: Design the definitive, single-pane-of-glass executive dossier and cockpit UI for the Manager.
- **Components**:
  - 14 mandatory Go/No-Go binary gates (zero weighted averaging, any single failure = NO_GO).
  - Explicit three-state outcome options: `GO`, `NO_GO`, `DEFER`.
  - Cryptographically verifiable digital signature record for the Manager's final order.
  - Summary dashboard integrating all 6 workstreams with real-time audit proofs.

#### P7-WS6: Real Pilot Exit, Rollback & Emergency Governance
- **Objective**: Provide unconditional, instantaneous fail-safe termination mechanisms.
- **Components**:
  - Single-action Emergency Hard-Stop killswitch (suspends all sessions, locks data within < 500ms).
  - Deterministic data purging and crypto-shredding protocol upon pilot conclusion or abort.
  - Rollback playbook returning the platform to pre-pilot baseline without data corruption.
  - Post-mortem and incident reporting templates for operational debrief.
