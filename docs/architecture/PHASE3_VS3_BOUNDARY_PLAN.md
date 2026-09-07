# Phase 3 Vertical Slice 3 Boundary Plan (P3-VS3)

## 1. Context and Authority
- Authority: `COMMANDER_P3_VS2_FINAL_DISPOSITION`
- Directive: `BEGIN: P3-VS3 DISCOVERY PHASE`
- Scope: `P3-VS3-COMMUNICATION-NOTIFICATIONS-DISPATCHER`
- Invariants:
  * Runtime Locked: No code edits until Discovery reviews (Qwen, GLM, Gemini) pass.
  * Zero PII: Notification payloads, recipient addressing, synthetic-only identifiers.
  * Fail-Closed Multi-Tenancy: PostgreSQL RLS and FORCE RLS on all tenant models.
  * Authoritative Business Records Preserved.

---

## 2. Problem Statement & Scope Definition
Vertical Slice 3 focuses on the **Unified Outbox Event Dispatcher, Reliable Delivery Guarantees, and Cross-Role Notification Engine**:
1. **Outbox Worker/Dispatcher Pipeline**:
   - Reliable polling of pending `OutboxMessage` records.
   - Batch dispatch with backoff retry policy and Dead-Letter Queue (DLQ) for poisoned notifications.
   - Transactional idempotency ensuring exactly-once processing effects.
2. **Notification Delivery & Preferences**:
   - In-app notification delivery linked to canonical domain events (`lesson_completed`, `submission_received`, `feedback_available`).
   - Read-status tracking (`read_at`, `delivered_at`) strictly isolated by tenant and user.
   - Role-partitioned dispatch (Students, Mentors, Parents, Admins).
3. **Frontend Notification Center & Bell Integration**:
   - Live badge counter sync with backend authority.
   - Drawer/Dropdown notification list with mark-as-read, filter-by-role, and responsive mobile/desktop UX.
   - Accessibility (WCAG 2.2 AA) and RTL alignment.

---

## 3. Data Flow & Architecture Boundary

```
[Domain Action / Event]
        │
        ▼
[platform_event.OutboxMessage] (Append-only, immutable)
        │
        ▼
[Celery Outbox Dispatcher Task] (Idempotent worker)
        │
        ├──► [Projection Applier / Watermark]
        │
        ▼
[modules.learning.models.NotificationItem] (Tenant-scoped, RLS enforced)
        │
        ▼
[GET /api/v1/learning/notifications/] (Role-authorized REST endpoint)
        │
        ▼
[Frontend NotificationBell & Drawer] (Brave tested, WCAG 2.2 AA)
```

---

## 4. Multi-Agent Review Protocol (Mandatory Gate)
- **Qwen 3.8 Max**: Domain logic, state transitions, retry backoff, idempotency semantics.
- **GLM 5.3**: Security boundary, RLS impact, database integrity, zero PII.
- **Gemini 3.8**: Notification drawer UX, RTL design tokens, responsive breakpoints, accessibility.
