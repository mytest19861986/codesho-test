# P3-MACRO-EPIC-20-22 Discovery Closure Dossier & Runtime Unlock Request

```yaml
TYPE: P3_MACRO_EPIC_20_22_DISCOVERY_AND_RUNTIME_UNLOCK_REQUEST
PROJECT: Codesho / SSD
TASK_ID: P3-MACRO-EPIC-20-22-CURRICULUM-DELIVERY-AND-PROGRAM-OPERATIONS
BRANCH: codex/phase3-product-platform-foundation
HEAD_COMMIT: 36ed9e7 (docs: canonical schema ddl v1.1 and discovery boundary plan)
MODE: MACRO_FAST_ENTERPRISE (Unified Implementation Slices 20, 21, 22)

FLEET_CONSENSUS_SUMMARY:
  QWEN_EPIC_DISCOVERY: PASS
  QWEN_BLOCKERS: 0
  GLM_EPIC_DISCOVERY: PASS
  GLM_BLOCKERS: 0
  GEMINI_EPIC_DISCOVERY: PASS
  GEMINI_BLOCKERS: 0

DISCOVERY_ARTIFACTS:
  BOUNDARY_PLAN_VERSION: v1.0-CANONICAL (docs/architecture/P3_MACRO_EPIC_20_22_BOUNDARY_PLAN.md)
  DDL_VERSION: v1.1-CANONICAL (docs/architecture/p3_macro_epic_20_22_schema_ddl.sql)
  PROOF_PACKAGE_VERSION: v1.3-ALIGNED (docs/coordination/P3_MACRO_EPIC_20_22_PROOF_PACKAGE.md)
  WRITE_MANIFEST: LOCKED (docs/coordination/P3_MACRO_EPIC_20_22_WRITE_MANIFEST.md)
  NEGATIVE_MATRIX: N1-N34 LOCKED (docs/coordination/P3_MACRO_EPIC_20_22_PROOF_PACKAGE.md)

INVARIANT_VERIFICATION_STATUS:
  IMMUTABLE_PUBLISHED_CURRICULUM: VERIFIED_ENFORCED
  ZERO_HISTORICAL_REBINDING: VERIFIED_ENFORCED
  ZERO_THIRD_PARTY_PROVIDERS: VERIFIED_ENFORCED
  ANTI_RANKING_STUDENT_METRICS: VERIFIED_ENFORCED (STUDENT_RANKING: 0)
  NO_AUTOMATED_PUNITIVE_ACTIONS: VERIFIED_ENFORCED
  POSTGRES_17_FORCE_RLS: VERIFIED_15_TABLES
  COMPOSITE_FOREIGN_KEYS: VERIFIED_100_PERCENT (Zero Bare UUIDs)
  SNAPSHOT_PROVENANCE_EXEMPTION: DOCUMENTED_AND_APPROVED_BY_GLM
  PII_REGIME: VERIFIED_21_KEYS_BLACKLIST_OBJECT_GUARD_TEXT_REGEX_BOUNDS
  REVOKE_UPDATE_DELETE: VERIFIED_5_AUDIT_SNAPSHOT_TABLES
  WCAG_2_2_AA_RTL_BIDI: VERIFIED_AND_APPROVED_BY_GEMINI

R3_R4: 0
OPEN_BLOCKERS: 0
OPEN_MAJORS: 0
```

---

### خلاصه ادله و اسناد اجماع کامل ناوگان

1. **ناظر قوانین چرخه حیات و ماشین‌های حالت (Qwen)**:
   - **رأی**: `QWEN_EPIC_DISCOVERY: PASS` | **بلاکرها**: 0
   - **سند رسمی**: `docs/coordination/QWEN_P3_MACRO_EPIC_20_22_DISCOVERY_REVIEW.md`
   - **خلاصه تأییدیه**: تأیید ماشین‌های حالت FSM برای نسخه‌ها و جلسات، انجماد تاریخی اسنپ‌شات‌ها، ممنوعیت اتصال مجدد داده‌های فراگیران و پایبندی به اصل ضد رتبه‌بندی.

2. **ناظر پایگاه‌داده، امنیت و رژیم RLS (GLM)**:
   - **رأی**: `GLM_EPIC_DISCOVERY: PASS` | **بلاکرها**: 0 | **ماژورها**: 0
   - **سند رسمی**: `docs/coordination/GLM_P3_MACRO_EPIC_20_22_ALIGNED_VERDICT.md`
   - **خلاصه تأییدیه**: تأیید ۱۰۰٪ DDL نسخه v1.1 و تطبیق کامل ماشین‌های حالت ۴گانه با بسته اثبات v1.3-ALIGNED، تثبیت کلیدهای خارجی ترکیبی، رژیم ۲۱ فیلدی PII، اعمال REVOKE روی ۵ جدول و ماتریس تست‌های منفی N1 تا N34 با پوشش کامل هسته ۵ گانه GUC.

3. **ناظر رابط کاربری، سیستم طراحی RTL و سلامت روان (Gemini)**:
   - **رأی**: `GEMINI_EPIC_DISCOVERY: PASS` | **بلاکرها**: 0
   - **سند رسمی**: `docs/coordination/GEMINI_P3_MACRO_EPIC_20_22_OFFICIAL_REVIEW.txt`
   - **خلاصه تأییدیه**: تأیید ارگونومی صفحات `/dashboard/admin/curriculum-operations` و `/dashboard/admin/cohort-schedules`، ریشه‌کنی لیدربورد و نمره‌دهی ریسک، انطباق با WCAG 2.2 AA، حداقل مساحت لمسی ۴۴ پیکسل، ایزولاسیون کامل عبارات فنی با `<bdi dir="ltr">` و استفاده از خصوصیات منطقی CSS.

---

### درخواست از فرماندهی محترم
با عنایت به تحقق کامل شرایط سه‌گانه ابلاغیه فرمانده (`Qwen: PASS`, `GLM: PASS`, `Gemini: PASS`, `OPEN_BLOCKERS: 0`) و قفل کامل مانیفست‌ها و DDL کانونیکال، تقاضای صدور فرمان قطعی:
```yaml
COMMANDER_P3_MACRO_EPIC_20_22_RUNTIME_UNLOCK: GRANTED
```
را برای ورود یکپارچه به فاز پیاده‌سازی ران‌تایم (شامل ۱۵ مدل جنگو، مایگریشن‌ها، پالیسی‌های RLS و کامپوننت‌های فرانت‌اند) دارم.
