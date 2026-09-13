# PHASE 4: CONTROLLED PILOT PREPARATION & OPERATIONAL READINESS
## QWEN DISCOVERY AUDIT DOSSIER (معماری، چرخه حیات و FSMهای عملیاتی)

**Document Identifier**: `P4_PILOT_PREPARATION_QWEN_DISCOVERY_PACKAGE`
**Task ID**: `P4-CONTROLLED-PILOT-PREPARATION-DISCOVERY`
**Target Auditor**: `Qwen` (Principal Domain Architect & Governance Specialist)
**Required Verdict**: `QWEN_PHASE4_DISCOVERY: PASS` | `QWEN_BLOCKERS: 0`
**Date**: 2026-09-13

---

### ۱. هدف و دامنه ارزیابی معماری
این دوسیه چارچوب عملیاتی و چرخه حیات استقرار، مدیریت رخدادها و ورود به پایلوت کنترل‌شده سامانه کُدشو (Phase 4) را جهت ارزیابی انطباق کامل با موازین حاکمیتی و ضد تخریب ارائه می‌دهد.

### ۲. چرخه‌های حیات حالت‌مند (FSM Lifecycles)

#### ۲.۱. چرخه حیات کاندیدای انتشار (Release Candidate FSM)
```
[DRAFT]
  │
  ▼ (action: PREPARE_RC / precondition: 100% tests pass, zero unapplied migrations)
[CANDIDATE_TAGGED]
  │
  ├──────────────────────────────────┐
  ▼ (action: RUN_SMOKE_TESTS)        ▼ (action: ABORT_RC / reason logged)
[VERIFIED_ON_STAGING]              [ABORTED]
  │
  ▼ (action: APPROVE_PILOT_PROMOTION / precondition: explicit dual-custody approval)
[PILOT_DEPLOYED]
  │
  ▼ (action: TRIGGER_ROLLBACK / condition: health check failure or critical error)
[ROLLED_BACK]
```
- **قاعده لغو خودکار**: هرگونه شکست در پروب‌های سلامت یا کشف رگرسیون، فوراً انتقال به وضعیت `ABORTED` یا `ROLLED_BACK` را فعال می‌سازد.
- **منع ارتقای خودکار**: هیچ گذار حالتی به سمت پروداکشن مجاز نبوده و `PRODUCTION_DEPLOY_AUTHORITY: 0` به صورت سخت‌افزاری در کد لحاظ شده است.

#### ۲.۲. چرخه حیات مدیریت رخدادها (Incident Management FSM)
```
[DETECTED]
  │
  ▼ (action: TRIAGE / classify: SEV1 to SEV4)
[TRIAGED]
  │
  ▼ (action: INVESTIGATE / assign lead operator)
[INVESTIGATING]
  │
  ▼ (action: MITIGATE / apply runbook mitigation)
[MITIGATED]
  │
  ▼ (action: CONDUCT_POSTMORTEM / write immutable PIR)
[RESOLVED]
```
- **دسته‌بندی شدت رخداد**:
  - `SEV1 (بسیار بحرانی)`: قطعی کامل ترافیک یا نقض احتمالی مرز چندمستأجری.
  - `SEV2 (بحرانی)`: اختلال در فرآیند یادگیری، از کار افتادن ورکر‌های سلری یا تاخیر بحرانی Outbox.
  - `SEV3 (متوسط)`: کندی موردی در رندر فرانت‌اند یا خطاهای غیر بحرانی ثبت وقایع.
  - `SEV4 (خفیف)`: خطاهای بصری جزیی یا هشدارهای غیرمسدودکننده.

### ۳. ماتریس بازیگران و اختیارات عملیاتی (Actor / Permission Matrix)

| نقش بازیگر (Actor Role) | ایجاد RC | آغاز استقرار پایلوت | اجرای رول‌بک | مدیریت رخداد | خروج مستأجر |
|---|---|---|---|---|---|
| `Platform Operator` | مجاز | نیازمند تأیید دو‌نفره | مجاز (اضطراری) | مجاز | مجاز با قفل لاگ |
| `Tenant Admin` | غیرمجاز | غیرمجاز | غیرمجاز | غیرمجاز | درخواست مجاز |
| `Mentor / Teacher` | غیرمجاز | غیرمجاز | غیرمجاز | گزارش رخداد | غیرمجاز |
| `Learner / Child` | غیرمجاز | غیرمجاز | غیرمجاز | غیرمجاز | انصراف از پایلوت |

### ۴. مرزهای حاکمیتی و انطباق با قواعد تخطی‌ناپذیر
- `REAL_CHILD_DATA: 0` و `REAL_GUARDIAN_DATA: 0`: داده‌های واقعی در پایلوت وارد نخواهند شد و تمامی سناریوها با داده‌های مصنوعی (Synthetic Data) اجرا می‌گردد.
- `STUDENT_RANKING: 0`: هیچ مقایسه رتبه‌ای یا لیدربورد رقابتی در تل‌متری یا لاگ‌ها وجود ندارد.
- `PRIVILEGE_SELF_GRANT: DENY`: هیچ اپراتوری نمی‌تواند سطح دسترسی خود را شخصاً بدون حضور اپراتور ناظر ارتقا دهد.
- `TAMPER_EVIDENCE_IMMUTABILITY: ENFORCED`: کلیه رویدادهای FSM به عنوان لاگ تغییرناپذیر ممیزی ذخیره می‌شوند.

### ۵. ماتریس آزمون‌های منفی معماری (N4-01 تا N4-06)
- **N4-01 (منع استقرار خودکار پروداکشن)**: درخواست استقرار خارج از محیط پایلوت با خطای `DeployAuthorityViolation` مسدود می‌شود.
- **N4-02 (تلاش برای خود-اعطایی دسترسی رول‌بک)**: بدون تاییدیه دو نفره رد می‌شود.
- **N4-03 (تلاش برای ثبت PII کودک در پیام‌های رخداد)**: توسط لایه Sanitize اسکراب و مسدود می‌شود.
- **N4-04 (تلاش برای تغییر لاگ ممیزی پس از رخداد)**: با خطای عدم اجازه SQL رد می‌شود.
- **N4-05 (تلاش برای ارتقای RC در زمان فعال بودن قفل حقوقی)**: با خطای `LegalHoldViolation` متوقف می‌گردد.
- **N4-06 (تلاش برای دسترسی تلمتری میان مستأجرها)**: خط‌مشی‌های RLS بلافاصله رکوردها را فیلتر می‌کنند.
