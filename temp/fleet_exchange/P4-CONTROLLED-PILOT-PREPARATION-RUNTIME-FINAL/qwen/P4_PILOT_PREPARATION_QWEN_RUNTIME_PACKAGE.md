# PHASE 4: CONTROLLED PILOT PREPARATION & OPERATIONAL READINESS
## QWEN FINAL RUNTIME AUDIT DOSSIER (FSMهای عملیاتی، کنترل رول‌بک و ماتریس N4)

**Document Identifier**: `P4_PILOT_PREPARATION_QWEN_RUNTIME_PACKAGE`
**Task ID**: `P4-CONTROLLED-PILOT-PREPARATION-RUNTIME-FINAL`
**Target Auditor**: `Qwen` (Principal Domain Architect & Governance Specialist)
**Required Verdict**: `QWEN_PHASE4_FINAL: PASS` | `QWEN_PHASE4_BLOCKERS: 0`
**Date**: 2026-09-13

---

### ۱. چرخه حیات کاندیدای انتشار (Release Candidate FSM)
- وضعیت‌ها: `DRAFT` -> `CANDIDATE_TAGGED` -> `VERIFIED_ON_STAGING` -> `PILOT_DEPLOYED`
- وضعیت‌های لغو و ایمنی: `ABORTED` و `ROLLED_BACK`
- الزام تایید دو‌نفره: متد clean مدل ReleaseCandidate مانع ارتقا به وضعیت `PILOT_DEPLOYED` بدون `has_dual_custody_approval=True` می‌شود.
- منع استقرار پروداکشن: قید `chk_rc_zero_production_deploy` و متد clean خطای اعتبارسنجی را برای `is_production_target=True` صادر می‌کنند (`PRODUCTION_DEPLOY_AUTHORITY: 0`).

### ۲. چرخه حیات مدیریت رخدادها (Incident FSM)
- وضعیت‌ها: `DETECTED` -> `TRIAGED` -> `INVESTIGATING` -> `MITIGATED` -> `RESOLVED`
- سطوح بحران: `SEV1` (نقض چندمستأجری/قطعی کامل)، `SEV2` (اختلال یادگیری)، `SEV3` (کارایی)، `SEV4` (خفیف).
- اسکرابینگ PII: فیلدهای خلاصه و Post-Incident Review (PIR) مجهز به اعتبارسنجی خودکار عدم وجود شماره تلفن و ایمیل واقعی هستند.

### ۳. ماتریس آزمون‌های منفی (N4-01 تا N4-16)
تمام ۱۶ سناریوی منفی در `tests/test_p4_negative_matrix.py` با نتیجه ۱۶/۱۶ پاس شده‌اند:
- N4-01: رد صریح استقرار خودکار پروداکشن
- N4-02: رد ارتقای پایلوت بدون تأییدیه دو‌نفره
- N4-03 & N4-04: رد ورود PII واقعی در رخدادها و گزارش PIR
- N4-05: رد خروج از حالت سنتتیک برای طرح‌های پایلوت
- N4-06 تا N4-10: ایزولاسیون کامل چندمستأجری، یکتایی شناسه‌ها و اعتبارسنجی وضعیت‌ها
- N4-11 & N4-12: گذار امن به استقرار پایلوت و رول‌بک
- N4-13 تا N4-15: ایجاد سنتتیک، گذار FSM رخداد و انصراف RC
- N4-16: تضمین قطعی خط‌مشی ضد رتبه‌بندی آموزشی (`STUDENT_RANKING: 0`)
