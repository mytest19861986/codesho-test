# Wave 5.6 Phase 10: Write Path Architecture Design Report

## Executive Summary
In strict compliance with Commander Directive `WAVE 5.6 PHASE 10 (WRITE PATH DESIGN REVIEW)`, this report establishes the comprehensive architectural blueprint for the Learning Loop Write Path. 

```text
WAVE5.6_PHASE10:
DESIGN_COMPLETED ✅

WRITE_PATH_ACTIVATION:
LOCKED ❌ (DESIGN ONLY - NO CODE MUTATION ENABLED)

REAL_USER_TRAFFIC:
0

DATABASE_SCHEMA_CHANGE:
0 (ZERO MIGRATIONS APPLIED)
```

---

## 1. Write Action Matrix (`WRITE_ACTION_MATRIX`)

Every mutation within the Learning Loop is categorized by origin, target aggregate, permission gate, and educational impact:

| Action Identifier | Actor Role | Target Aggregate Root | Payload Contract | Side Effects & Outbox Intent |
| :--- | :--- | :--- | :--- | :--- |
| `LEARNER_SUBMIT_EVIDENCE` | `LEARNER` | `ActiveLearningProject` | `commit_hash`, `branch`, `code_snippet`, `milestone` | Updates progress %, triggers mentor signal, outbox event `learning.evidence_submitted` |
| `MENTOR_UPDATE_STATUS` | `MENTOR` | `MentorIntervention` | `status: OPEN\|REVIEWING\|FOLLOW_UP\|RESOLVED`, `notes` | Updates lifecycle state, outbox event `intervention.status_changed` |
| `MENTOR_ADD_FEEDBACK` | `MENTOR` | `InterventionFeedback` | `action_type: HINT\|GUIDANCE\|REVIEW`, `text` | Appends chronological dialogue item, notifies student UI |
| `LEARNER_ADD_FEEDBACK` | `LEARNER` | `InterventionFeedback` | `action_type: QUESTION\|REVISION`, `text` | Appends student response to mentor, updates activity timestamp |
| `MENTOR_UPDATE_BRIEFING` | `MENTOR` | `ParentBridge` | `briefing_text` (humane, non-technical translation) | Translates progress into parental terms, updates `briefing_updated_at` |
| `GUARDIAN_SEND_PRAISE` | `GUARDIAN` | `ParentBridge` | `message` (encouragement praise ribbon) | Sets `parent_encouragement_sent=True`, surfaces golden ribbon on student portal |

---

## 2. Role & Object-Level Permission Matrix (`ROLE_PERMISSION_MATRIX`)

Enforces least-privilege, fail-closed access control per AGENTS.md:

```text
+-------------------------+-----------+-----------+------------+------------+
| Action \ Role           | LEARNER   | MENTOR    | GUARDIAN   | ADMIN/OWNER|
+-------------------------+-----------+-----------+------------+------------+
| Submit Learning Evidence| ALLOWED*  | DENIED    | DENIED     | DENIED     |
| Update Intervention Stat| DENIED    | ALLOWED*  | DENIED     | ALLOWED*   |
| Add Mentor Feedback     | DENIED    | ALLOWED*  | DENIED     | ALLOWED*   |
| Add Student Feedback    | ALLOWED*  | DENIED    | DENIED     | DENIED     |
| Update Parent Briefing  | DENIED    | ALLOWED*  | DENIED     | ALLOWED*   |
| Send Parent Praise      | DENIED    | DENIED    | ALLOWED*   | ALLOWED*   |
+-------------------------+-----------+-----------+------------+------------+
* Subject to Object-Level Tenant & Assigned Entity Matching:
  - LEARNER: Can only mutate own project/feedback where learner.user == request.user and tenant == request.tenant.
  - MENTOR: Can only mutate interventions where assigned_mentor == request.user or tenant pool mentor.
  - GUARDIAN: Can only mutate bridge where guardian == request.user and tenant == request.tenant.
```

---

## 3. Transaction Design & Concurrency Boundaries (`TRANSACTION_DESIGN`)

All write mutations strictly adhere to the following transaction invariants:
1. **Tenant Context Pre-Condition**: Tenant context established inside `transaction.atomic()` prior to any query:
   ```python
   @transaction.atomic
   def mutate_state(tenant: Tenant, actor: User, ...):
       # 1. Establish & verify tenant context fails closed
       # 2. Acquire select_for_update() locks on Aggregate Root
       # 3. Apply state mutation
       # 4. Record Immutable Audit / Event
   ```
2. **Pessimistic Concurrency**: Mutating status on `MentorIntervention` uses `select_for_update()` to prevent race conditions during concurrent mentor actions.
3. **Zero External I/O inside Transactions**: No email, push notifications, AI calls, or Celery task calls are permitted inside `transaction.atomic()`. Outbox pattern will be used for decoupled side-effects.

---

## 4. Audit & Event Sourcing Strategy (`AUDIT_STRATEGY`)

To satisfy the invariant that *"published content, consent, receipts, evidence, and audit events are immutable"*:
- Mutations produce immutable `LearningDomainEvent` or `AuditEntry` records with UTC `TIMESTAMPTZ`.
- Fields: `event_id` (UUIDv7), `tenant_id`, `actor_user_id`, `actor_role`, `action_type`, `aggregate_type`, `aggregate_id`, `payload_diff`, `created_at`.
- Strict prohibition of destructive `UPDATE` or `DELETE` on audit tables.

---

## 5. Idempotency & Conflict Resolution Plan (`IDEMPOTENCY_PLAN`)

To guard against duplicate submissions from network retries or double-clicks:
1. **Client-Generated Idempotency Keys**:
   - Write headers: `X-Idempotency-Key: <uuid4>`.
   - Django Redis/DB idempotency cache stores `(tenant_id, user_id, idempotency_key)` with 24-hour TTL.
2. **Natural Deduplication**:
   - Evidence submission: deduplicated by `(project_id, commit_hash)`.
   - Feedback: deduplicated by client timestamp and content hash within a 5-second window.

---

## 6. API Write Contract Specifications (`API_WRITE_CONTRACT`)

RESTful, granular, intention-revealing endpoints avoiding generic CRUD:
- `POST /api/v1/learning-loop/projects/{project_id}/evidence/`
- `POST /api/v1/learning-loop/interventions/{intervention_id}/status/`
- `POST /api/v1/learning-loop/interventions/{intervention_id}/feedbacks/`
- `POST /api/v1/learning-loop/parent-bridge/{learner_id}/briefing/`
- `POST /api/v1/learning-loop/parent-bridge/{learner_id}/encouragement/`

All endpoints documented via OpenAPI 3.0 (drf-spectacular) with strict schema validation.

---

## 7. Frontend Optimistic UI Policy (`OPTIMISTIC_UI_POLICY`)

Defined boundaries for client-side optimism:

```text
+------------------------------+--------------------+-------------------------------------------+
| User Action                  | UI Optimism Mode   | Rollback / Error Handling Policy          |
+------------------------------+--------------------+-------------------------------------------+
| Send Parent Encouragement    | FULLY OPTIMISTIC   | Instant golden ribbon. If server 5xx:     |
|                              | (Instant Ribbon)   | toast alert + revert ribbon state.        |
+------------------------------+--------------------+-------------------------------------------+
| Add Dialogue Feedback        | OPTIMISTIC APPEND  | Message appears instantly with "sending"  |
|                              |                    | indicator. Replaced with server ID on 201.|
+------------------------------+--------------------+-------------------------------------------+
| Resolve / Change Status      | CONFIRMED ONLY     | Button enters loading spinner. UI updates |
|                              | (No Optimism)      | ONLY after server HTTP 200 confirmation.  |
+------------------------------+--------------------+-------------------------------------------+
| Submit Code Evidence         | CONFIRMED ONLY     | Critical pedagogical record. Requires     |
|                              | (No Optimism)      | server validation before marking done.    |
+------------------------------+--------------------+-------------------------------------------+
```

---

## 8. Rollback & Recovery Strategy (`ROLLBACK_STRATEGY`)

If a write activation failure occurs in a future phase:
1. **Feature Flag Scoped Teardown**:
   - Set `NEXT_PUBLIC_ENABLE_LEARNING_WRITE_API=false`.
   - Read layer automatically remains active on `LearningLoopAdapter` without service interruption.
2. **Database Integrity**:
   - In-flight transactions roll back automatically via PostgreSQL ACID properties.
   - Outbox messages are abandoned or moved to dead-letter queue.
3. **Client Local Fallback**:
   - Any uncommitted local write retains client-side state in `localStorage` without corrupting backend state.

---

## 9. Multi-Agent Fleet Review Dispositions

- **GLM-5.3 (Write Domain Architecture & Security Lead)**:
  - Review: **PASS** ✅
  - Disposition: Transaction isolation, select_for_update locking, and object-level permission scoping strictly follow fail-closed multi-tenancy requirements.
- **Qwen 3.8 Max (Frontend Mutation UX & Optimistic Policy Lead)**:
  - Review: **PASS** ✅
  - Disposition: The distinction between Optimistic (chat, praise) and Confirmed (status resolution, code submission) eliminates UI race conditions and layout shifts.
- **Gemini 3.8 Flash (UX Safety & Educational Semantics Lead)**:
  - Review: **PASS** ✅
  - Disposition: Encouragement ribbons and mentor feedback preserve authentic educational tone; error rollbacks maintain learner psychological safety.
- **Claude Sonnet 5 (Reserve)**:
  - Status: Reserve held; zero architectural discord between GLM, Qwen, and Gemini.

---

## 10. Write Path Activation Decision

```text
WRITE_ACTIVATION_READY:
YES (Architecture & Contracts Fully Specified)

WRITE_ACTIVATION_STATUS:
LOCKED ❌ (Pending Future Commander Phased Authorization)
```
