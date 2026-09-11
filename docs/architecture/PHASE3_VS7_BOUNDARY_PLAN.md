# Phase 3 Vertical Slice 7 Boundary Plan (P3-VS7)

## 1. Context and Authority
- Authority: `COMMANDER_P3_VS6_FINAL_DISPOSITION` (`P3-VS6 = COMPLETE_FINAL_ACCEPTED`, `BEGIN: P3-VS7 DISCOVERY`)
- Scope: `P3-VS7-ADVANCED-ASSESSMENT-AUTOMATED-EVALUATION-AND-CODE-PLAYGROUND`
- Invariants:
  * Runtime Locked: No runtime implementation until Fleet Scope Approval (Qwen, GLM, Gemini), Manifest Lock, and Commander Runtime Authorization.
  * Zero PII: Synthetic identifiers for students, code submissions, execution logs, and automated test evaluations.
  * Multi-Tenancy: PostgreSQL 17 FORCE ROW LEVEL SECURITY on all tenant-scoped tables (`app.current_tenant`).
  * Concurrency & Integrity: Isolated test container boundaries, deterministic timeout handling, idempotency on code runs and grading.
  * GUC Consistency: Standardized on `app.current_tenant` across all RLS policies, migrations, and tenant context managers.

---

## 2. Sandbox Specification & Security Isolation (GLM G1 / S1 Mandate)
1. **فناوری و لایه ایزولاسیون (Isolation Engine)**:
   - اجرای کدهای غیرقابل‌اعتماد (Untrusted Code) در محیط موقت سخت‌گیری‌شده بدون دسترسی به فایل‌سیستم هاست (Read-Only Root Filesystem, ephemeral `/tmp` with tmpfs limited to 64MB).
   - ایزولاسیون سی‌گروپ و نیم‌اسپیس‌ها (cgroups v2, PID/Mount/IPC/Network Namespaces, seccomp deny syscalls: ptrace, clone, mount, bpf, socket).
2. **سیاست شبکه (Egress & Ingress Deny-All)**:
   - شبکه به طور کامل قطع (`network: none`). صفر بایت ارتباط شبکه مجاز است.
   - دسترسی به شبکه داخلی، دیتابیس PostgreSQL، ردیس و ران‌تایم سلری کاملاً مسدود و غیرممکن (Zero Internal/External Network).
3. **سقف و محدودیت منابع (Strict Resource Limits)**:
   - سقف پردازنده: حداکثر ۱ هسته ایزوله (1 CPU core / 1000ms CPU quota).
   - سقف حافظه: حداکثر ۲۵۶ مگابایت (Memory Limit: 256MB hard cap, OOM-kill immediately).
   - سقف زمان اجرا: حداکثر ۵ ثانیه زمان دیواری (Wall-clock timeout: 5s).
   - سقف حجم لاگ خروجی: حداکثر ۶۴ کیلوبایت (Truncated to 64KB, sanitized to prevent buffer flood).
4. **محیط فاقد اسرار (Zero Secrets in Execution Env)**:
   - هیچ متغیر محیطی مربوط به سیستم، توکن‌ها، رمزهای عبور یا کلیدهای دیتابیس در کانتینر یا محیط اجرای کد تزریق نمی‌شود (`env -i` با متغیرهای حداقلی مانند `PATH` و `LANG=C.UTF-8`).

---

## 3. Domain Scope & Business Rules (Qwen Mandate)

1. **مدل‌های داده‌ای تفصیلی (Data Models & Entity Relationships)**:
   - مدل `CodeAssessment` (آزمون برنامه‌نویسی درس):
     * فیلدها: `id` (UUID), `tenant` (FK), `lesson` (FK), `language` (Choice: python, typescript), `timeout_seconds` (PositiveInt, max 5), `memory_limit_mb` (PositiveInt, max 256), `starter_code` (TextField), `testcases` (JSONField: array of {id, input, expected_output, weight, is_hidden}), `testcases_hash` (CharField 64, SHA-256 for deterministic caching), `is_active` (Boolean).
   - مدل `CodeExecutionRun` (تلاش اجرای کد در سندباکس):
     * فیلدها: `id` (UUID), `tenant` (FK), `assessment` (FK to CodeAssessment), `student_id` (UUID Synthetic), `attempt_number` (PositiveInt), `submitted_code` (TextField), `code_hash` (CharField 64, SHA-256), `runtime_image_hash` (CharField 64), `idempotency_key` (CharField 128, Unique per tenant), `status` (PENDING, RUNNING, PASSED, FAILED, TIMED_OUT, ERROR), `duration_ms` (PositiveInt), `memory_used_kb` (PositiveInt), `stdout_log` (TextField Sanitized), `stderr_log` (TextField Sanitized), `created_at`, `updated_at`.
     * اینواریانت یکتایی: `UNIQUE (tenant, assessment, student_id, attempt_number)` و `UNIQUE (tenant, idempotency_key)`.
   - مدل `AssessmentResult` (کارنامه قطعی و نمره نهایی ارزیابی):
     * فیلدها: `id` (UUID), `tenant` (FK), `execution_run` (OneToOneField to CodeExecutionRun), `assessment` (FK), `student_id` (UUID Synthetic), `passed_tests_count` (PositiveInt), `total_tests_count` (PositiveInt), `score` (Decimal 0.00 to 100.00), `is_passed` (Boolean), `is_final` (Boolean, default True), `created_at`.
     * تغییرناپذیری (Immutability): پس از درج رکورد در دیتابیس، آپدیت روی `AssessmentResult` توسط تریگر دیتابیس Fail-Closed مسدود است.
   - محدوده **Code Playground**:
     * ابزار تعاملی برای اجرای آزمایشی کدهای تمرینی در کلاینت بدون نیاز به ثبت نمره قطعی کارنامه، با استفاده از اجرای ایزوله موقت (Ephemeral Dry-Run).

2. **ماشین وضعیت و بازیابی کارگر (State Machine & Recovery)**:
   - وضعیت‌های مجاز: `PENDING` -> `RUNNING` -> (`PASSED` | `FAILED` | `TIMED_OUT` | `ERROR`).
   - وضعیت‌های پایانی (Terminal States): `PASSED`, `FAILED`, `TIMED_OUT`, `ERROR` همگی غیرقابل برگشت هستند.
   - بازیابی کارگر اجرایی (Worker Recovery / Visibility Timeout):
     * ثبت `lease_expires_at` در `CodeExecutionRun`. در صورتی که ورکر سلری یا کانتینر کرش کند و وضعیت پس از ۳۰ ثانیه در `RUNNING` باقی بماند، ران با وضعیت `ERROR` و لاگ `Worker Crashed / Lease Expired` علامت‌گذاری شده و تسک مجدد قفل نخواهد ماند.

3. **سیاست نمره‌دهی و ارزیابی (Scoring & Normalization Policy)**:
   - نرمال‌سازی خروجی: مقایسه خروجی واقعی با خروجی مورد انتظار پس از `strip()` کردن خطوط انتهایی و یکسان‌سازی شکست خط (`\r\n` -> `\n`).
   - اعداد اعشاری: پشتیبانی از مقایسه با تلورانس عددی (Epsilon tolerance $10^{-5}$) در صورت تعریف در تست‌کیس.
   - نمره‌دهی وزن‌دار: محاسبه نمره بر اساس مجموع اوزان تست‌های پاس‌شده تقسیم بر کل اوزان ضربدر ۱۰۰. در صورت خطای زمان کامپایل یا Syntax Error، وضعیت بلافاصله `FAILED` و نمره صفر تعیین می‌شود.

4. **ایزولاسیون چندمستأجری و امنیت پایگاه داده (PostgreSQL 17 FORCE RLS)**:
   - اعمال `ALTER TABLE ... FORCE ROW LEVEL SECURITY` بر روی جداول `learning_codeassessment`, `learning_codeexecutionrun`, `learning_assessmentresult`.
   - پالیسی ایزولاسیون Fail-Closed بر اساس `app.current_tenant`:
     ```sql
     CREATE POLICY code_assessment_tenant_isolation ON learning_codeassessment
         FOR ALL TO authenticated_role
         USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
         WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);
     ```
   - نشت داده ضربدری (Cross-Tenant Leakage): دقیقاً 0. تست‌های منفی دسترسی چندمستأجری در سوئیت تست پوشش داده خواهند شد.

---

## 4. Frontend UX & Accessibility Boundaries (Gemini Mandate)

1. **کامپوننت محیط کدنویسی تعاملی (`InteractivePlaygroundCard.tsx`)**:
   - تلفیق تمیز راست‌به‌چپ (RTL) در کادرها، سرصفحه و راهنمای مسئله با چپ‌به‌راست (LTR) در ادیتور کد و کنسول ترمینال.
   - فونت مونو استاندارد خوانا، شماره خطوط، کنترل‌های اجرای کد (Run Code)، تب‌های نمایش خروجی (Console Output / Test Cases).
   - وضعیت‌های لودینگ صریح و غیرمسدودکننده، کنترل کلیک‌های مکرر.
2. **کامپوننت ارزیابی تست‌ها (`TestEvaluationPanel.tsx`)**:
   - کارت‌های تست‌کیس با برچسب‌های رنگی استاندارد و آیکون و متن صریح (Passed / Failed).
   - نمایش زمان اجرا (ms) و نمره کل با فونت خوانا.
3. **پایبندی به استانداردهای WCAG 2.2 AA**:
   - کنتراست بالای ۴.۵:۱ برای تمام متون، تارگت‌های لمسی بالای ۴۴ پیکسل، فوکوس کیبورد قابل مشاهده (`focus-visible`).
   - واکنش‌گرایی در نمایشگر موبایل (390px) و دسکتاپ (1440px).

---

## 5. Fleet Review Verification Checklist
- [ ] **Qwen 3.8 Max**: احراز مدل‌های دامنه، فیلدهای هشینگ و تلاش، ماشین وضعیت با بازیابی ورکر، سیاست نمره‌دهی و صدور صریح `QWEN_SCOPE: PASS`.
- [ ] **GLM 5.3**: احراز مشخصات سخت‌گیرانه سندباکس (ایزولاسیون، deny-all شبکه، سقف منابع، عدم وجود سکرت)، یکنواختی `app.current_tenant` در RLS و صدور صریح `GLM_SCOPE: PASS`.
- [ ] **Gemini 3.8**: احراز کامپوننت‌های فرانت‌اند، تلفیق RTL/LTR در ادیتور، استانداردهای WCAG 2.2 AA و صدور صریح `GEMINI_SCOPE: PASS`.
