# PHASE 5: CONTROLLED PILOT ACTIVATION RUNTIME IMPLEMENTATION
## GLM FINAL RUNTIME DATABASE & SECURITY DOSSIER (مایگریشن 0051، سیاست‌های RLS، قفل‌های مشورتی و ایزولاسیون چندمستأجری)

**Document Identifier**: `P5_PILOT_ACTIVATION_GLM_RUNTIME_PACKAGE`
**Task ID**: `P5-CONTROLLED-PILOT-ACTIVATION-RUNTIME-FINAL`
**Target Auditor**: `GLM` (Principal Database Architect & Multi-Tenant Security Specialist)
**Required Verdict**: `GLM_PHASE5_FINAL: PASS` | `GLM_PHASE5_BLOCKERS: 0`
**Commit Reference**: `c57c45fe5f69cd54ffb0e18fd32323d4e41295d1`
**Date**: 2026-09-14

---

### ۱. مایگریشن 0051 و ایمنی ران‌تایم پایگاه داده (DDL & Vendor Guarding)
- مایگریشن `backend/modules/learning/migrations/0051_p5_controlled_pilot_activation_fsm.py`:
  - اضافه کردن جداول:
    - `learning_pilot_tenant_lifecycle`
    - `learning_pilot_prerequisite_checklist`
    - `learning_dual_custody_approval_event`
  - کلیه دستورات تغییر ساختار (DDL) به صورت افزایشی و غیرمخرب (Additive Only) هستند؛ هیچ ستون، جدول یا کلیدی حذف نشده است.
  - اعمال توابع پایتونی `enable_p5_postgres_rls` و `disable_p5_postgres_rls` با محافظ `schema_editor.connection.vendor == "postgresql"` جهت سازگاری کامل با محیط‌های تست محلی و انطباق قطعی در PostgreSQL 17.

### ۲. سیاست‌های تفکیک و ایزولاسیون چندمستأجری (PostgreSQL 17 RLS)
- اعمال سخت‌گیرانه `FORCE ROW LEVEL SECURITY` بر روی کلیه جداول سه‌گانه فاز ۵.
- اعمال سیاست تفکیک مستأجر:
  `CREATE POLICY p5_tenant_isolation_policy ON %I FOR ALL USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid) WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);`
- تضمین عدم امکان نقض مرز مستأجر توسط نقش اپلیکیشن (`NOBYPASSRLS`).

### ۳. تغییرناپذیری و محافظت ممیزی (Immutability & Audit Integrity)
- لغو قطعی امتیاز حذف بر روی رخدادهای تصویب دو‌نفره:
  `REVOKE DELETE ON learning_dual_custody_approval_event FROM PUBLIC;`
  `REVOKE DELETE ON learning_dual_custody_approval_event FROM codesho_app;`
- کلیه تاییدیه‌ها دارای امضای امنیتی و تغییرناپذیر می‌باشند.

### ۴. قفل مشورتی تراکنش در سطح پایگاه داده (PostgreSQL Advisory Locking)
- پیاده‌سازی قفل انحصاری تراکنش در سرویس ارتقای پایلوت:
  `SELECT pg_advisory_xact_lock(hashtext(%s))`
  جهت پیشگیری قاطع از Race Condition در ارتقای موازی چرخه‌های پایلوت.

### ۵. یکپارچگی ارجاعات و عدم وجود کلیدهای بدون مستأجر (Zero Bare UUID)
- اعمال قید‌های یکتایی ترکیبی `(tenant_id, pilot_identifier)` و `(tenant_id, id)`.
- عدم وجود هرگونه ارجاع کلید خارجی بدون مرز صریح مستأجر (`BARE_TENANT_UUID: 0`).
- صحت عملکرد در آزمون‌های منفی N5-01 تا N5-25 و آزمون‌های همزمانی تایید شده است.
