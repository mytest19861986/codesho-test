# WAVE5.5.3 — EDUCATOR / MENTOR COMMAND CENTER DIRECTIVE

**COMMAND STATUS: GO**  
**DIRECTIVE:** `EXECUTE WAVE5.5.3_EDUCATOR_MENTOR_COMMAND_CENTER_IMPLEMENTATION`

## ۱. هدف و فلسفه طراحی
- **مسیر اصلی:** `/mentor`
- **هدف:** ساخت تجربه اختصاصی مربی/منتور برای اینکه سریع بفهمد کدام دانش‌آموز نیاز به توجه دارد، چرا، چه شواهدی وجود دارد و اقدام بعدی چیست.
- **اصل تجربه:**  
  `SIGNAL → CONTEXT → EVIDENCE → ACTION`  
  *(نه: KPI → CHART → TABLE → MORE KPI)*

---

## ۲. حریم و خطوط قرمز (Hard Constraints)
- `DATABASE_CHANGE = 0`
- `BACKEND_CHANGE = 0`
- `NEW_API_ENDPOINT = 0`
- `SERVER_INFRA_CHANGE = 0`
- `NGINX_CHANGE = 0`
- `PRODUCTION_DEPLOY = NO-GO` (استقرار فقط پس از گزارش نهایی و صدور فرمان GO فرمانده مجاز است)
- `AI_TEACHER_IMPACT = 0`
- `DIRECT_GITHUB_ACCESS = FORBIDDEN` (انجام صرفاً از طریق Antigravity)

---

## ۳. بخش‌های اصلی داشبورد `/mentor`
1. **Cohort Pulse:** وضعیت انسانی دوره (stalled, struggling, milestone, encouragement opportunity, follow-up).
2. **Student Intervention Queue:** صف مداخله هوشمند دانش‌آموزان با فیلدهای (Student, Reason, Context, Urgency, Evidence, Recommended Action, State).
3. **Learning Evidence Workspace:** فضای شواهد یادگیری (پروژه فعال، شواهد مهارت، یادداشت مربی، زمینه مرتبط با والدین).
4. **Mentor Action Studio:** استودیوی اقدامات مربی (ارسال بازخورد، تشویق، گام بعدی، تغییر وضعیت مداخله، پیش‌نویس گزارش والدین).

---

## ۴. تعاملات الزامی (Mandatory Interactions)
- **Student Detail Drawer**
- **Evidence Review Drawer**
- **Feedback Composer**
- **Intervention Resolution Flow** (مدل وضعیت‌ها: `OPEN` → `REVIEWING` → `FOLLOW_UP` → `RESOLVED`)
- **Parent Briefing Preview**
- **Cohort / Student Switcher**
- بدون دکمه غیرفعال یا CTA مرده (`DEAD_PRIMARY_CTA = 0`).

---

## ۵. الزامات موبایل و RTL
- Mobile-first، عدم تبدیل صرف Desktop به ستون‌های عمودی.
- اولویت در موبایل: چه کسی نیاز به توجه دارد؟ چرا؟ بررسی شواهد، اقدام.
- بومی‌سازی کامل RTL (فونت، فاصله‌ها، آیکون‌های SVG جهت‌دار، شیت‌ها و اعداد فارسی/انگلیسی ترکیبی).
- ممنوعیت ایموجی، نمودارهای تزئینی، کارت‌های بی‌معنی KPI و متون لورم ایپسوم.

---

## ۶. تخصیص ایجنت‌ها (Agent Fleet Assignment)
- **Qwen 3.8 Max:** پیاده‌ساز اصلی (Primary Implementer).
- **GLM-5.3:** معمار ارشد (Principal Architect) برای مدل داده و لایه‌های بازکاربرد.
- **Gemini 3.8 Flash:** تضمین کیفیت بصری و کاربری (UX/Visual QA).
- **Claude Sonnet 5:** رزرو (فقط در صورت تداخل معماری یا مسائل امنیتی پیچیده).

---

## ۷. گیت‌های پذیرش و پسرفت (Regression & Quality Gates)
- `BUILD = PASS`, `TYPECHECK = PASS`, `RUNTIME = PASS`
- رگرسیون صفر روی مسیرهای:
  - `/`
  - `/student`
  - `/parent`
  - `/admin`
  - `/mentor`
