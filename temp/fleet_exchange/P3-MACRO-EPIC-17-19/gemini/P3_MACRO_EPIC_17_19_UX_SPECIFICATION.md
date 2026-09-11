# P3-MACRO-EPIC-17-19 Boundary Plan & Architecture Specification (v1.0)

## 1. Epic Overview
- Epic ID: `P3-MACRO-EPIC-17-19-MENTOR-OPERATIONS-AND-PROGRAM-SUCCESS`
- Branch: `codex/phase3-product-platform-foundation`
- Authority: `COMMANDER_P3_VS16_CLOSURE_AND_MACRO_EPIC_17_19_DIRECTIVE`
- Delivery Mode: `MACRO_FAST_ENTERPRISE` (Single Epic Package, Combined Discovery, Parallel Fleet Review)
- Scope: Mentor Caseload Management, Support Queues, Learning Check-ins Orchestration, and Program Success Support Analytics.

---

## 2. Integrated Slices Architecture & Domain Boundaries

### 2.1. P3-VS17: Mentor Caseload & Support Operations
- **Core Models**:
  - `MentorCaseloadAssignment`: نگاشت دانش‌آموز به منتور با وضعیت‌های فعال/آرشیو شده و تاریخ تخصیص.
  - `SupportQueueItem`: صف عملیات حمایتی منتور شامل اقدامات پیگیری سررسیدشده، مداخلات نیازمند بررسی و وضعیت فوریت صرفاً عملیاتی (مانند تاریخ انقضا یا وضعیت در انتظار اقدام منتور).
- **Invariants**:
  - ZERO Ranking / Zero Behavioral Scoring: فوریت بر اساس زمان و تعهدات عملیاتی مشخص می‌شود، نه مدل‌های امتیازدهی روانی دانش‌آموز.
  - قید یکتایی تخصیص فعال دانش‌آموز به منتور در هر مستاجر: `UNIQUE (tenant_id, student_id, is_active)` به صورت partial index.

### 2.2. P3-VS18: Learning Check-ins, Scheduling & Follow-up Orchestration
- **Core Models**:
  - `LearningCheckIn`: جلسات کوتاه ارزیابی پیشرفت و بررسی وضعیت بین منتور و دانش‌آموز.
  - `CheckInOutcome`: نتایج چک‌این شامل تعهدات متقابل یادگیری و پیگیری‌های زمان‌بندی‌شده.
  - `FollowUpCommitment`: تعهدات طرفین با تاریخ سررسید و یادآوری خارج از تراکنش.
- **FSM States**:
  - Check-in: `SCHEDULED` -> `IN_PROGRESS` -> `COMPLETED` / `RESCHEDULED` / `CANCELLED`
- **Invariants**:
  - تایید دانش‌آموز اختیاری و محترمانه است؛ عدم حضور یا تاخیر منجر به برچسب‌های تنبیهی نمی‌شود.
  - استفاده از سیستم Outbox جهت ارسال نوتیفیکیشن‌ها خارج از تراکنش دیتابیس (`BaseTenantTask`).

### 2.3. P3-VS19: Program Success Operations & Support Analytics
- **Core Models / Projections**:
  - `ProgramSupportAggregate`: تجمیع آمار حمایت‌های آموزشی (تعداد چک‌این‌های انجام‌شده، میانگین زمان پیگیری، پوشش حمایتی).
  - `MentorWorkloadMetric`: بار کاری منتورها بدون مقایسه رقابتی بین منتورها، صرفاً جهت توزیع عادلانه دانش‌آموزان.
- **Invariants**:
  - اکیداً غیرمقتدرانه (Non-Authoritative): تجمیع‌ها هرگز نباید به عنوان وضعیت نهایی دانش‌آموز عمل کنند.
  - حذف لیدربورد، امتیازدهی منفی، یا تعیین بهترین/بدترین دانش‌آموز.

---

## 3. Database Schema & PostgreSQL 17 RLS Specification

1. **FORCE ROW LEVEL SECURITY**:
   - بر روی تمامی جداول پنج‌گانه جدید اعمال می‌گردد:
     ```sql
     ALTER TABLE learning_mentorcaseloadassignment ENABLE ROW LEVEL SECURITY;
     ALTER TABLE learning_mentorcaseloadassignment FORCE ROW LEVEL SECURITY;
     ```
2. **Composite Foreign Keys**:
   - تمامی ارتباطات با `(tenant_id, target_id)` برقرار شده و هیچ‌گونه کلید خارجی Bare UUID وجود ندارد.
3. **Session Protocol & GUC**:
   - کلیه کوئری‌ها منحصراً درون `transaction.atomic()` و پس از تنظیم `app.current_tenant` اجرا می‌شوند.
4. **PII Scrubbing**:
   - اعمال فیلتراسیون جامع ۱۳ کلید PII و گاردهای `jsonb_typeof` بر روی متادیتاها و یادداشت‌های ارزیابی.

---

## 4. UI/UX Design System & Accessibility Specification

1. **داشبورد منتور (Mentor Workspace)**:
   - رابط تعاملی مدرن با تمرکز بر کاهش بار شناختی (Cognitive Load).
   - تفکیک شفاف سه تب عملیاتی: بار کاری (Caseload)، چک‌این‌ها (Check-ins)، و بینش‌های برنامه (Analytics).
2. **عایق‌بندی BiDi و RTL**:
   - استفاده از پراپرتی‌های منطقی CSS (`margin-inline`, `padding-inline`, `border-inline-start`).
   - الزام سراسری به کارگیری `<bdi dir="ltr">` برای تاریخ‌ها، شناسه‌های سنتتیک و زمان‌ها.
3. **WCAG 2.2 AA**:
   - ابعاد اهداف لمسی $\ge 44 \times 44\text{ px}$.
   - کنتراست رنگ متن $\ge 4.5:1$ و عناصر رابط کاربری $\ge 3.0:1$.
   - پشتیبانی ۱۰۰٪ از ناوبری با کیبورد و فوکوس واضح.

---

## 5. Negative Test Proof Matrix (N1 - N30)
- N1 - N6: آزمون‌های منفی نشت مستأجر و جعل GUC در اختصاص منتور و صف حمایتی.
- N7 - N12: آزمون‌های تخطی از FSM چک‌این و تلاش برای گذار نامعتبر.
- N13 - N18: آزمون‌های تزریق PII در یادداشت‌های چک‌این و رد قطعی در سطح پایگاه‌داده.
- N19 - N24: آزمون‌های ضد رتبه‌بندی (Anti-Ranking) و اطمینان از عدم انتشار داده‌های تحلیلی مقایسه‌ای.
- N25 - N30: آزمون‌های همزمانی (Concurrency) با `pg_advisory_xact_lock` در تغییر وضعیت‌های صف و چک‌این.
