# Phase 3 Vertical Slice 4 Boundary Plan (P3-VS4)

## 1. Context and Authority
- Authority: `COMMANDER_P3_VS3_FINAL_DISPOSITION`
- Directive: `BEGIN: P3-VS4 DISCOVERY PHASE`
- Scope: `P3-VS4-LEARNING-ANALYTICS-AND-STUDENT-GAMIFICATION-PROGRESSION`
- Invariants:
  * Runtime Locked: No code edits until Discovery reviews (Qwen, GLM, Gemini) pass.
  * Zero PII: Gamification stats, badge codes, synthetic student identifiers.
  * Fail-Closed Multi-Tenancy: PostgreSQL RLS and FORCE RLS on all tenant models (`app.tenant_id`).
  * Source of Truth: Authoritative progress, streaks, and completed milestones in PostgreSQL.

---

## 2. Domain Entities, State Machine & Badge Rules (Qwen & GLM Invariants)
1. **قواعد صریح نشان‌ها (Badge Definition Invariants)**:
   - مدل یا کاتالوگ ثابت `BadgeDefinition`:
     * `badge_code` (e.g. `FIRST_LESSON`, `STREAK_3_DAYS`, `COURSE_COMPLETED`)
     * `badge_level` (پیش‌فرض: `1`)
     * `title` (فارسی، بدون PII)
     * `threshold` (e.g. 1, 3, 7)
     * `is_repeatable` (پیش‌فرض: `False`)
   - قید یکتایی نشان اعطاشده در `StudentBadgeAward`:
     `UNIQUE (tenant_id, student_id, badge_code, badge_level)`
2. **ماشین وضعیت نشان‌ها**:
   - رکوردهای پایدار در دیتابیس منحصراً در وضعیت `AWARDED` ذخیره می‌شوند.
   - وضعیت‌های `LOCKED` و `ELIGIBLE` به صورت مشتق‌شده و محاسباتی در سرویس/پروجکشن تعیین می‌گردند.
   - لغو نشان (`REVOKED`) در MVP غیرمجاز است و رکوردها غیرقابل دستکاری (Immutable) هستند.
3. **قوانین زنجیره روزانه (Streak Rules & Zero-State-Drift)**:
   - مبنای تعریف روز: `UTC Midnight` (یا منطقه زمانی پیش‌فرض سیستم آموزشی تهران `Asia/Tehran` با نرمالیزاسیون صریح UTC).
   - فعالیت‌های واجد شرایط (`Qualifying Activities`): رویدادهای قطعی `lesson_completed` و `submission_reviewed`.
   - رفع تکرار در روز (`Deduplication per Day`): فعالیت‌های متعدد در یک تقویم روزانه، تنها یک بار برای استمرار روز منظور می‌گردد.
   - رویدادهای دیرهنگام (`Late Event Handling`): بازسازی قطعی و ترتیبی (Deterministic Recomputation) بر مبنای جدول تاریخچه تکمیل درس.
4. **ایدمپوتنس و همزمانی (Idempotency & Concurrency)**:
   - کلید یکتایی رویداد در اعطای نشان: `UNIQUE (tenant_id, event_id, badge_code, badge_level)`.
   - قفل خوش‌بینانه (`Optimistic Locking`) با فیلد `version` بر روی `StudentProgressionProfile` برای جلوگیری از شرایط رقابتی (Race Conditions).

---

## 3. Data Flow & Architecture Boundary

```
[Lesson Completion / Submission Reviewed Event]
        │
        ▼
[platform_event.OutboxMessage] (Append-only, immutable)
        │
        ▼
[Gamification Outbox Dispatcher Task] (Idempotent worker, BaseTenantTask)
        │
        ├──► [Optimistic Lock on StudentProgressionProfile]
        │
        ▼
[modules.learning.models.StudentBadgeAward] (Tenant-scoped, FORCE RLS)
        │
        ▼
[GET /api/v1/learning/student/gamification/]
        │
        ▼
[Student Dashboard Gamification Showcase: BadgeShelf & StreakIndicator]
```

---

## 4. Multi-Agent Review Protocol (Mandatory Discovery Gate)
- **Qwen 3.8 Max**: Progression rules, streak state machine, idempotent badge awards, concurrency & API schema.
- **GLM 5.3**: Security perimeter, multi-tenant RLS (`app.tenant_id`), zero-PII gamification attributes, immutable audit trail.
- **Gemini 3.8**: Badges & streak visual UX, design tokens, RTL alignment, WCAG 2.2 AA compliance.
