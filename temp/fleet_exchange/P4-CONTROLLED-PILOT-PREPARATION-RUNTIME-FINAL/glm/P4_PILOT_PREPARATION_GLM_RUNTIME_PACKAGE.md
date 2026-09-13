# PHASE 4: CONTROLLED PILOT PREPARATION & OPERATIONAL READINESS
## GLM FINAL RUNTIME DATABASE & SECURITY DOSSIER (نقش‌های دیتابیس، ایمنی مایگریشن و RLS)

**Document Identifier**: `P4_PILOT_PREPARATION_GLM_RUNTIME_PACKAGE`
**Task ID**: `P4-CONTROLLED-PILOT-PREPARATION-RUNTIME-FINAL`
**Target Auditor**: `GLM` (Principal Database Architect & Multi-Tenant Security Specialist)
**Required Verdict**: `GLM_PHASE4_FINAL: PASS` | `GLM_PHASE4_BLOCKERS: 0`
**Date**: 2026-09-13

---

### ۱. تفکیک نقش‌های سه‌گانه پایگاه‌داده پایلوت (DB Role Topology)
- `codesho_migrator`: اجرای مایگریشن‌های مجاز در خط استقرار کنترل‌شده CI.
- `codesho_app`: ران‌تایم اپلیکیشن، تحت خط‌مشی‌های سخت‌گیرانه `FORCE ROW LEVEL SECURITY` و `NOBYPASSRLS`.
- `codesho_readonly`: مانیتورینگ سلامت با اعمال قطعی tenant context.

### ۲. مایگریشن‌های افزایشی فاز ۴ (Additive DDL)
- مایگریشن `0049_incidentrecord_pilottenantprovisioningplan_and_more.py`: افزودن مدل‌های جدید پایلوت بدون هیچ‌گونه تخریب یا حذف ستون.
- مایگریشن `0050_p4_pilot_preparation_rls_force.py`: فعال‌سازی `FORCE ROW LEVEL SECURITY` در PostgreSQL 17 به همراه لغو دسترسی `DELETE` بر روی رکوردهای تغییرناپذیر عملیاتی (`REVOKE DELETE ... FROM codesho_app`).

### ۳. یکپارچگی کلیدهای خارجی و ایزولاسیون چندمستأجری
- صفر Bare UUID: کلیه جدول‌ها دارای قید ترکیبی یکتای `(tenant, id)` هستند.
- انطباق با قواعد بازیابی آزمایشی (PITR Sandbox) و حفظ حاکمیت قفل‌های حقوقی.
