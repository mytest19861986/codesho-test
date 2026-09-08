# Phase 3 Vertical Slice 6 Boundary Plan (P3-VS6)

## 1. Context and Authority
- Authority: `COMMANDER_P3_VS5_FINAL_DISPOSITION` (`P3-VS5 = COMPLETE_FINAL_ACCEPTED`, `BEGIN: P3-VS6 DISCOVERY`)
- Scope: `P3-VS6-STUDENT-ASSIGNMENT-SUBMISSION-AND-MENTOR-FEEDBACK-WORKFLOW`
- Invariants:
  * Runtime Locked: No runtime implementation until Fleet Scope Approval (Qwen, GLM, Gemini), Manifest Lock, and Commander Runtime Authorization.
  * Zero PII: Synthetic identifiers for students, mentors, submissions, and feedback items.
  * Multi-Tenancy: PostgreSQL 17 FORCE ROW LEVEL SECURITY on all tenant-scoped tables (`app.tenant_id`).
  * Concurrency & Integrity: Atomic status transitions, submission state machine, idempotency on submission and grading.

---

## 2. Domain Scope & Business Rules

1. **مدل‌های داده‌ای و ماشین وضعیت (Data Models & State Machine)**:
   - مدل `Assignment` (تکلیف مقید به درس، مستأجر و وضعیت انتشار):
     * مقید به `Lesson` با وضعیت‌های `DRAFT`, `PUBLISHED`, `CLOSED`.
     * فیلدهای مهلت تحویل (`due_date`) و حداکثر نمره (`max_score`).
   - مدل `Submission` (ارسال تکلیف توسط دانش‌آموز):
     * وضعیت‌های ارسال: `DRAFT`, `SUBMITTED`, `UNDER_REVIEW`, `REVIEWED`.
     * قید یکتایی: هر دانش‌آموز در هر نسخه تکلیف حداکثر یک ارسال فعال/نهایی داشته باشد (`UNIQUE(tenant, assignment, student_id)`).
     * کلید یکتایی و عاری از تکرار: `idempotency_key`.
     * تحویل پس از مهلت (`late_submission_policy`): ثبت زمان واقعی `submitted_at` جهت بررسی سیاست‌های تأخیر.
   - مدل `Feedback` / `SubmissionReview` (بررسی و بازخورد منتور):
     * نمره ثبت‌شده: `score` اعتبارسنجی‌شده (`0 <= score <= assignment.max_score`).
     * متن بازخورد آموزشی ساختاریافته به زبان فارسی.
     * ارزیابی منتور و قفل وضعیت: پس از تایید (`REVIEWED`)، ثبت نهایی غیرقابل تغییر است (Immutability).
   - انطباق با گیمیفیکیشن و پیشرفت:
     * ثبت رویداد `submission_reviewed` جهت به‌روزرسانی `StudentProgressionProfile` (اعطای XP و مدال مرتبط).

2. **قواعد امنیتی و انزوای مستأجر (Security & Multi-Tenant Boundaries)**:
   - اعمال کامل PostgreSQL 17 `FORCE ROW LEVEL SECURITY` روی جداول تکالیف، ارسال‌ها و بازخوردها.
   - مسدودسازی دسترسی ضربدری (Cross-Tenant Negatives): منتور یا دانش‌آموز یک مستأجر تحت هیچ شرایطی نباید تکالیف یا ارسال‌های مستأجر دیگر را ببیند یا ویرایش کند.
   - تضمین Zero-PII در لاگ‌ها، پیلودها و بازخوردها.

3. **رابط کاربری و تجربه کاربری (Frontend & UX Boundaries)**:
   - کامپوننت ارسال تکلیف در داشبورد دانش‌آموز (`AssignmentSubmissionCard.tsx`):
     * پشتیبانی کامل از راست‌به‌چپ (RTL)، تایپوگرافی فارسی، وضعیت مهلت تحویل و وضعیت ارسال.
   - کامپوننت کارتابل بررسی منتور (`MentorReviewQueue.tsx`):
     * نمایش صف بررسی ارسال‌های در انتظار (`UNDER_REVIEW`)، فیلتر بر اساس کوهورت و درس.
   - پایبندی به استاندارد WCAG 2.2 AA، کنتراست رنگی، وضعیت‌های خطا و لودینگ.

---

## 3. Fleet Review Mandate
- **Qwen 3.8 Max**: ارزیابی دامنه کسب‌وکار، چرخه حیات و ماشین وضعیت ارسال و تصحیح تکالیف، همزمانی و مدیریت نمرات.
- **GLM 5.3**: ارزیابی معماری دیتابیس، سیاست‌های RLS در PostgreSQL 17، تراکنش‌های اتمیک و سیاست‌های عدم نشت داده/PII.
- **Gemini 3.8**: ارزیابی تجربه کاربری، ساختار کارت‌های تکلیف و بازخورد منتور در چیدمان RTL و دسترس‌پذیری.
