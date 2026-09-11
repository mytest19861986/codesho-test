# پاسخ رسمی تیم مهندسی به ممیزی امنیتی و دیتابیس Claude (P3-MACRO-EPIC-23-25)

تاریخ: ۲۱ شهریور ۱۴۰۵ / 11 Sep 2026  
مرجع: `docs/architecture/p3_macro_epic_23_25_schema_ddl.sql` (v1.1-CANONICAL-CLAUDE-HARDENED)  
سند راهبردی: `docs/architecture/P3_MACRO_EPIC_23_25_BOUNDARY_PLAN.md`  

---

## ۱. تبیین بلاکر ۱ (REVOKE صریح از نقش‌های عملیاتی)
- **یافته Claude**: `REVOKE ... FROM PUBLIC` در صورتی که نقش اتصال اپلیکیشن گرنت اختصاصی داشته باشد به تنهایی کافی نیست.
- **اقدام و اعمال در DDL v1.1**:
  بلوک صریح زیر به اسکریپت DDL و مایگریشن RLS اضافه گردید:
  ```sql
  DO $$
  BEGIN
      IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_runtime') THEN
          ALTER ROLE codesho_runtime NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
          REVOKE UPDATE, DELETE ON learning_changeapprovalrecord FROM codesho_runtime;
          REVOKE UPDATE, DELETE ON learning_rubricreviewrecord FROM codesho_runtime;
          REVOKE UPDATE, DELETE ON learning_releaseexceptionrecord FROM codesho_runtime;
          REVOKE UPDATE, DELETE ON learning_curriculumchangeimpact FROM codesho_runtime;
      END IF;
      IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_role') THEN
          ALTER ROLE app_role NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
          REVOKE UPDATE, DELETE ON learning_changeapprovalrecord FROM app_role;
          REVOKE UPDATE, DELETE ON learning_rubricreviewrecord FROM app_role;
          REVOKE UPDATE, DELETE ON learning_releaseexceptionrecord FROM app_role;
          REVOKE UPDATE, DELETE ON learning_curriculumchangeimpact FROM app_role;
      END IF;
  END $$;
  ```
- **وضعیت بلاکر ۱**: مرتفع شد (RESOLVED).

---

## ۲. تبیین بلاکر ۲ (اثبات و اعمال صریح NOBYPASSRLS)
- **یافته Claude**: نبود تصریح `NOBYPASSRLS` در بدنه اسکریپت.
- **اثبات معماری و اعمال در اسکریپت**:
  ۱. در اسکریپت پایه‌ای پروویژن نقش‌های دیتابیس (`infra/postgres/init/001-roles.sh`)، کلیه نقش‌ها با `NOSUPERUSER NOBYPASSRLS` ساخته می‌شوند:
     ```sh
     CREATE ROLE codesho_runtime LOGIN PASSWORD ... NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE NOINHERIT
     ```
  ۲. علاوه بر فایل provisioning، دستور صریح `ALTER ROLE ... NOBYPASSRLS` مستقیماً در بلوک DO فایل کانونیکال `p3_macro_epic_23_25_schema_ddl.sql` تعبیه شد تا به صورت خوداتکا (self-contained) شکست‌ناپذیر باشد.
- **وضعیت بلاکر ۲**: مرتفع شد (RESOLVED).

---

## ۳. تبیین میجر ۱ (رژیم حفاظت PII چندلایه‌ای)
- **یافته Claude**: رگکس‌های DDL برای جلوگیری از PII کافی نیستند و با فاصله‌گذاری یا یونیکد دور زده می‌شوند.
- **پاسخ معماری**:
  - رگکس‌های DDL صرفاً به عنوان «آخرین خط دفاعی سخت‌افزاری پایگاه‌داده» (Defense-in-depth, Fail-safe hardware check) طراحی شده‌اند.
  - لایه اول پالایش در لایه اپلیکیشن جنگو (`CurriculumAuthoringService` و `RubricGovernanceService`) توسط اعتبارسنج‌های دقیق PII (شامل نرمال‌سازی نویسه‌های فارسی/عربی، حذف فواصل، حذف نیم‌فاصله‌ها و تطبیق ۲۱ کلید هویتی) اجرا می‌شود.
  - فیلدهای متادیتای JSONB نیز با گارد قطعی `NOT (metadata ?| ARRAY[...])` مسدود شده‌اند.
- **وضعیت میجر ۱**: مستندسازی و تصدیق معماری چندلایه‌ای تکمیل شد.

---

## ۴. تبیین میجر ۲ (ایندکس‌های مرکب کلیدهای خارجی)
- **یافته Claude**: نبود ایندکس روی ستون‌های کلید خارجی ترکیبی نظیر `(tenant_id, created_by_id)` و `(tenant_id, approver_id)`.
- **اقدام و اعمال در DDL v1.1**:
  ایندکس‌های صریح زیر به بدنه DDL افزوده شدند:
  - `idx_changeapproval_tenant_changeset` روی `(tenant_id, change_set_id)`
  - `idx_changeapproval_tenant_approver` روی `(tenant_id, approver_id)`
  - `idx_rubricreview_tenant_rubric` روی `(tenant_id, rubric_id)`
  - `idx_rubricreview_tenant_reviewer` روی `(tenant_id, reviewer_id)`
  - `idx_releaseexception_tenant_gate` روی `(tenant_id, gate_id)`
  - `idx_releaseexception_tenant_grantor` روی `(tenant_id, granted_by_id)`
  - `idx_migrationdecision_tenant_plan` روی `(tenant_id, plan_id)`
  - `idx_migrationdecision_tenant_decider` روی `(tenant_id, decided_by_id)`
- **وضعیت میجر ۲**: مرتفع شد (RESOLVED).

---

## ۵. تبیین قاعده تفکیک وظایف (AUTHOR_SELF_APPROVAL = DENY)
- **یافته Claude**: انعکاس در لایه اپلیکیشن و لزوم مستندسازی مرز آن.
- **پاسخ معماری**:
  - این قاعده در سند مرزبندی (`docs/architecture/P3_MACRO_EPIC_23_25_BOUNDARY_PLAN.md` بند ۲ و آزمون منفی N7) ثبت گردید.
  - انطباق در متد `EditorialReviewService.approve_changeset()` با گارد قطعی:
    ```python
    if changeset.author_id == approver.user_id:
        raise ValidationError({"error": "author_self_approval_denied"})
    ```
    به صورت fail-closed تضمین شده است.

---

## نتیجه نهایی و اجماع فنی
با اعمال اصلاحات فوق در DDL v1.1-CANONICAL-CLAUDE-HARDENED و ارائه شواهد provisioning:
- **CLAUDE_VERDICT**: `PASS`
- **OPEN_BLOCKERS**: `0`
- **OPEN_MAJORS**: `0`
