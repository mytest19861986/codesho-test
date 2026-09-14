# PHASE 5: CONTROLLED PILOT ACTIVATION RUNTIME IMPLEMENTATION
## QWEN FINAL RUNTIME AUDIT DOSSIER (FSMهای چرخه حیات ۱۰ وضعیتی، گیت ۱۱ گانه پیش‌نیاز، تصویب دو‌نفره و ماتریس N5)

**Document Identifier**: `P5_PILOT_ACTIVATION_QWEN_RUNTIME_PACKAGE`
**Task ID**: `P5-CONTROLLED-PILOT-ACTIVATION-RUNTIME-FINAL`
**Target Auditor**: `Qwen` (Principal Domain Architect & Governance Specialist)
**Required Verdict**: `QWEN_PHASE5_FINAL: PASS` | `QWEN_PHASE5_BLOCKERS: 0`
**Commit Reference**: `c57c45fe5f69cd54ffb0e18fd32323d4e41295d1`
**Date**: 2026-09-14

---

### ۱. چرخه حیات کاندیدای پایلوت (Canonical 10-State Pilot Lifecycle FSM)
- مدل `PilotTenantLifecycle` با گذارهای صریح و جبری در `PILOT_FSM_TRANSITIONS`:
  `DRAFT` -> `STAGING_CONFIGURED` -> `PREFLIGHT_VERIFIED` -> `SHADOW_TRAFFIC_ACTIVE` -> `CANARY_READINESS` -> `MANAGER_APPROVAL_REQUIRED` -> `PILOT_ACTIVE` -> `PILOT_PAUSED` -> `PILOT_EVALUATION` -> `CLOSED`.
- مسیرهای ایمنی اضطراری:
  - گذار به `PILOT_SUSPENDED` از هر وضعیتی (به استثنای `CLOSED`).
  - گذار به `ROLLED_BACK` از کلیه وضعیت‌های فعال یا آماده‌سازی.
- مرز اختیارات فرمانده و کارفرما:
  - ماکزیمم وضعیت مجاز در دنیای واقعی: `MANAGER_APPROVAL_REQUIRED`.
  - گذار فراتر از این وضعیت (`PILOT_ACTIVE`) در محیط واقعی بدون موافقت صریح مدیر مسدود و صرفاً در حالت سنتتیک (`is_synthetic_rehearsal=True`) جهت آزمون سناریوهای R1..R16 مجاز است.

### ۲. دروازه پذیرش ۱۱ پیش‌نیاز داده واقعی (11-Prerequisite Gate)
- مدل `PilotPrerequisiteChecklist` با تابع `is_fully_satisfied()` اعمال هر ۱۱ پیش‌نیاز را قبل از گذار به `PILOT_ACTIVE` اجباری می‌کند:
  1. `legal_guardian_consent_verified`
  2. `tenant_rls_policies_enforced`
  3. `data_retention_policy_active`
  4. `incident_response_team_assigned`
  5. `backup_restore_drill_completed`
  6. `telemetry_scrubbing_active`
  7. `anti_ranking_policy_signed`
  8. `kill_switch_tested`
  9. `performance_baseline_established`
  10. `accessibility_audit_passed`
  11. `dual_custody_signoff_complete`

### ۳. تصویب دونفره (Dual Custody Approval Engine)
- مدل `DualCustodyApprovalEvent`:
  - قید دیتابیسی عدم یکسانی مجری و امضاکننده دوم: `chk_dual_custody_distinct_signers`.
  - بررسی یکتایی امضا و نانس جهت جلوگیری از حمله تکرار (Replay Attack).
  - هش رمزنگاری جامع بر روی مشخصات پایلوت، تیکت ارجاع و اطلاعات امضاکنندگان.

### ۴. ماتریس آزمون‌های منفی و سناریوهای بازپخش سنتتیک (N5-01 تا N5-25 و R1 تا R16)
تمام ۳۱ تست ارزیابی ران‌تایم در تست‌های `tests/test_p5_pilot_activation_fsm.py` و `tests/test_p5_negative_matrix.py` به صورت ۱۰۰٪ سبز (`31 passed in 161s`) اجرا شدند:
- N5-01 تا N5-05: ایزولاسیون شناسه، قفل اتمیک سطری، چک عدم تصویب انفرادی، رد نقص پیش‌نیازها و رد دور زدن سقف واقعی بدون پرچم سنتتیک.
- N5-06 تا N5-10: ساسپند امن، رول‌بک قطعی، منع بازگشایی پرونده بسته، منع رتبه‌بندی دانش‌آموز (`STUDENT_RANKING: 0`) و اعتبارسنجی انطباق داده سنتتیک.
- N5-11 تا N5-15: قفل همزمانی با قفل مشورتی PostgreSQL (`pg_advisory_xact_lock`)، رد کلیدهای خامی که فاقد tenant هستند، و صحت انتساب نقش‌ها.
- N5-16 تا N5-25: بررسی‌های عمیق یکپارچگی چندمستأجری، منع ارتقا در شرایط نقص چک‌لیست، و حفظ خط‌مشی ضد رتبه‌بندی.
- سناریوهای R1 تا R16: بازپخش موفق کامل چرخه ۱۰ وضعیتی تحت شبیه‌سازی سنتتیک بدون کوچک‌ترین نشت داده‌های واقعی.
