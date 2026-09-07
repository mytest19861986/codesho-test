# Phase 3 Boundary and Execution Plan (Codesho)

## Document Metadata
- **TASK_ID**: `P3-BOUNDARY-001`
- **STATUS**: `COMPLETE / MACHINE_VERIFIED`
- **AUTHORITY**: `COMMANDER_PHASE3_BOUNDARY_ORDER`
- **TARGET_BRANCH**: `codex/phase1-engineering-readiness`
- **DRAFT_PR**: `https://github.com/mytest19861986/codesho-test/pull/47`

---

## 1. Executive Summary
This document establishes the authoritative operational and technical boundaries for **Phase 3** of the Codesho educational platform. Following the successful completion, quality gating, and Draft PR creation of Phase 2 (covering the complete multi-role learning experience for Admin, Student, Mentor, and Parent), Phase 3 transitions the platform into **Content/Media Attachments**, **Durable Outbox-backed Domain Events**, **Synthetic Notifications**, and **Cross-Role Feedback Loops**.

All capabilities are strictly partitioned into three categories:
1. `PHASE3_ENGINEERING_READY`: Safe, in-scope engineering enhancements that build upon verified Phase 2 primitives without external legal or commercial prerequisites.
2. `PHASE3_BLOCKED_BY_COUNSEL_OR_EMPLOYER`: High-risk or legal-dependent surfaces (real PII, real guardian consent, live payment gateways, runtime AI mentor, third-party trackers) strictly deferred until formal authorization.
3. `UNKNOWN`: Forbidden from implementation.

---

## 2. Phase 2 Baseline Inventory & Machine Truth

### 2.1 Backend Truth
- **Framework**: Django 5.2, Django REST Framework, Python 3.12, PostgreSQL (RLS enabled), Redis, Celery.
- **Test Suite Execution**: 259 passed, 59 skipped (environment-dependent), 0 failed.
- **RLS Multi-Tenancy**: 7 passed (`test_learning_rls_postgres.py`), fail-closed tenant isolation enforced.
- **OpenAPI Contract**: Exact parity between `docs/openapi.yaml` and live spectacular schema.

### 2.2 Frontend Truth
- **Framework**: Next.js App Router (15+), TypeScript, Vanilla/Tailwind CSS tokens.
- **Static Routes Generated (11 Clean Pages)**:
  - `/` (Home / Landing)
  - `/admin/learning` (Admin Curriculum & Course Lifecycle)
  - `/dashboard/student` (Student Learning Journey, Code Submissions)
  - `/dashboard/mentor` (Mentor Review Queue, Grading & Rubric Feedback)
  - `/dashboard/parent` (Parent Read-Only Supervised Progress)
  - Auth, profile, and tenant selection views.
- **E2E Browser Verification**: CDP verified on port 3000, 0 console errors, 0 broken links.

---

## 3. Personas & User Journeys (Phase 3 Target)

### 3.1 Admin Persona
- **Journey**: Creates Courses, Modules, Lessons, and Assignments -> Attaches Synthetic Media Metadata (reference guides, assets) -> Publishes Content via State Machine -> Triggers Outbox Event `ASSIGNMENT_PUBLISHED`.

### 3.2 Student Persona
- **Journey**: Discovers published Lesson -> Views attached media guides -> Solves and submits assignment solution -> Generates `SUBMISSION_RECEIVED` domain event -> Receives synthetic notification when feedback is completed.

### 3.3 Mentor Persona
- **Journey**: Observes submission queue -> Claims submission (`SUBMISSION_REVIEW_STARTED`) -> Submits grading rubric and feedback note (`SUBMISSION_REVIEWED` / `FEEDBACK_AVAILABLE`).

### 3.4 Parent Persona
- **Journey**: Supervised read-only monitoring of child's completed milestones, feedback scores, and attached educational assets (`PARENT_PROGRESS_VIEWED`).

---

## 4. Route & API Inventory

| Route / Endpoint | Role | Method | State Machine Action | Phase 3 Capability |
| :--- | :--- | :--- | :--- | :--- |
| `/api/v1/learning/admin/courses/` | Admin | GET, POST | `DRAFT` creation | `PHASE3_ENGINEERING_READY` |
| `/api/v1/learning/admin/courses/<id>/publish/` | Admin | POST | `DRAFT -> PUBLISHED` | `PHASE3_ENGINEERING_READY` |
| `/api/v1/learning/admin/courses/<id>/media/` | Admin | POST | Attach synthetic media | `PHASE3_ENGINEERING_READY` (P3-VS1) |
| `/api/v1/learning/lessons/<id>/` | Student | GET | View lesson & media | `PHASE3_ENGINEERING_READY` |
| `/api/v1/learning/submissions/` | Student | POST | `PENDING` submission | `PHASE3_ENGINEERING_READY` |
| `/api/v1/learning/mentor/reviews/` | Mentor | GET, POST | `IN_REVIEW -> COMPLETED` | `PHASE3_ENGINEERING_READY` |
| `/api/v1/learning/parent/overview/` | Parent | GET | Read-only summary | `PHASE3_ENGINEERING_READY` |
| `/api/v1/notifications/inbox/` | All | GET | Synthetic in-app inbox | `PHASE3_ENGINEERING_READY` (P3-VS1) |
| `/api/v1/payments/checkout/` | Any | ANY | Live payments | `PHASE3_BLOCKED_BY_COUNSEL_OR_EMPLOYER` |
| `/api/v1/ai/mentor/chat/` | Student | ANY | Runtime LLM mentor | `PHASE3_BLOCKED_BY_COUNSEL_OR_EMPLOYER` |

---

## 5. Event & Durable Outbox Architecture

### 5.1 Authoritative Outbox Invariant
- **Rule**: No independent competing event queue or fire-and-forget message broker. All domain events must be appended inside `transaction.atomic()` to the existing durable outbox table.
- **Candidate Events**:
  - `ASSIGNMENT_PUBLISHED`
  - `SUBMISSION_RECEIVED`
  - `SUBMISSION_REVIEW_STARTED`
  - `SUBMISSION_REVIEWED`
  - `FEEDBACK_AVAILABLE`
  - `LESSON_COMPLETED`
  - `MEDIA_ATTACHED`

### 5.2 Delivery Lifecycle
```text
[Business Mutation] 
      │ (Atomic DB Commit)
      ▼
[Outbox Entry (PENDING)]
      │ (BaseTenantTask Dispatcher)
      ▼
[DISPATCHING] ──► [Synthetic Notification Provider] ──► [DELIVERED]
      │
      ▼ (On Failure)
[RETRY_PENDING] ──► Max Retries Exceeded ──► [FAILED_PERMANENT]
```

---

## 6. Capability Classification Matrix

### 6.1 Engineering-Ready Capabilities (`PHASE3_ENGINEERING_READY`)
- **CAPABILITY**: `P3-CAP-001: Synthetic Media Attachment Foundation`
  - **DOMAIN**: BACKEND / DATA / FRONTEND
  - **CURRENT_STATE**: Conceptual model documented; needs tenant-bound attachment schema.
  - **SECURITY_RISK**: R1
  - **PRIVACY_IMPACT**: NONE (Synthetic/fake storage provider only; zero user uploads).
  - **ENGINEERING_READY**: YES
  - **REQUIRES_COUNSEL**: NO
  - **REQUIRES_EMPLOYER**: NO
  - **RECOMMENDED_TASK**: `P3-VS1`

- **CAPABILITY**: `P3-CAP-002: Durable Outbox Domain Event Pipeline`
  - **DOMAIN**: BACKEND / DATA
  - **CURRENT_STATE**: Outbox table exists; learning domain events need standard serialization.
  - **SECURITY_RISK**: R1
  - **PRIVACY_IMPACT**: LOW (No PII in event payloads).
  - **ENGINEERING_READY**: YES
  - **REQUIRES_COUNSEL**: NO
  - **REQUIRES_EMPLOYER**: NO
  - **RECOMMENDED_TASK**: `P3-VS1`

- **CAPABILITY**: `P3-CAP-003: Synthetic In-App Notification Delivery`
  - **DOMAIN**: FRONTEND / BACKEND
  - **CURRENT_STATE**: UI notification bells mocked; backend ledger needed.
  - **SECURITY_RISK**: R1
  - **PRIVACY_IMPACT**: NONE
  - **ENGINEERING_READY**: YES
  - **REQUIRES_COUNSEL**: NO
  - **REQUIRES_EMPLOYER**: NO
  - **RECOMMENDED_TASK**: `P3-VS1`

- **CAPABILITY**: `P3-CAP-004: Frontend Accessibility & Multi-Role Theme Polish`
  - **DOMAIN**: FRONTEND / UX
  - **CURRENT_STATE**: All 4 role dashboards operational; ARIA tags, RTL spacing, and contrast require automated audit.
  - **SECURITY_RISK**: R0
  - **PRIVACY_IMPACT**: NONE
  - **ENGINEERING_READY**: YES
  - **REQUIRES_COUNSEL**: NO
  - **REQUIRES_EMPLOYER**: NO
  - **RECOMMENDED_TASK**: `P3-VS4`

---

### 6.2 Blocked Capabilities (`PHASE3_BLOCKED_BY_COUNSEL_OR_EMPLOYER`)
- **CAPABILITY**: `P3-BLOCK-001: Real User Onboarding & SMS OTP`
  - **REASON**: Requires SMS gateway credentials, Iranian legal compliance, privacy policies, and employer spend.
  - **STATUS**: `DEFERRED`
- **CAPABILITY**: `P3-BLOCK-002: Real Child Data & Legal Guardian Verification`
  - **REASON**: Requires formal legal counsel approval under child privacy regulations.
  - **STATUS**: `DEFERRED`
- **CAPABILITY**: `P3-BLOCK-003: Commercial Payment Gateway (Shetab / Shaparak / Zarinpal)`
  - **REASON**: Requires merchant bank contracts, fiscal identification, and production payment credentials.
  - **STATUS**: `DEFERRED`
- **CAPABILITY**: `P3-BLOCK-004: Runtime AI Mentor / LLM Integration`
  - **REASON**: Prohibited by architecture rules without formal ADR, safety guardrails, and budget sign-off.
  - **STATUS**: `DEFERRED`
- **CAPABILITY**: `P3-BLOCK-005: Third-Party Behavioral Tracking & Production S3/CDN`
  - **REASON**: Forbidden to prevent data leakage and unapproved infrastructure costs.
  - **STATUS**: `DEFERRED`

---

## 7. Vertical Slice 1 Definition: P3-VS1
- **TASK_ID**: `P3-VS1-CONTENT-MEDIA-NOTIFICATION-FOUNDATION`
- **RISK_LEVEL**: R2
- **GOAL**: Demonstrate complete closed-loop flow:
  `Admin Content Creation` -> `Synthetic Media Attachment` -> `Domain Event Publication` -> `Durable Outbox Ledger` -> `Dispatcher` -> `Synthetic In-App Notification` -> `Cross-Role UI Display`.
- **INVARIANTS**:
  - `CROSS_TENANT_LEAKS = 0`
  - `DUPLICATE_AUTHORITATIVE_DELIVERY = 0`
  - `OUTBOX_STATE_INCONSISTENCIES = 0`
  - `UNEXPLAINED_CONSOLE_ERRORS = 0`
