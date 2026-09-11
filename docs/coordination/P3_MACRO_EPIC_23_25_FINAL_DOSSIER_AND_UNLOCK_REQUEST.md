# P3-MACRO-EPIC-23-25 Dossier & Runtime Unlock Request

**Status**: ALL_FLEET_DISCOVERY_GATES_PASSED (Gemini, Qwen, Claude/GLM)  
**Epic ID**: `P3-MACRO-EPIC-23-25-CURRICULUM-AUTHORING-QUALITY-AND-RELEASE-OPERATIONS`  
**Delivery Mode**: `MACRO_FAST_ENTERPRISE`  
**Branch**: `codex/phase3-product-platform-foundation`  
**HEAD Commit**: `83b3311` (Pushed to `codesho-test`)  

---

## 1. آرای رسمی و مستقل ممیزان ناوگان

| ممیز ناوگان | دامنه تخصصی | رأی رسمی | تعداد بلاکر | تعداد میجر | سند پاسخ ثبت‌شده |
|:---|:---|:---:|:---:|:---:|:---|
| **Gemini** | سیستم طراحی، WCAG 2.2 AA، دسترسی‌پذیری و BiDi | **PASS** | 0 | 0 | `docs/coordination/GEMINI_P3_MACRO_EPIC_23_25_DISCOVERY_REPLY.md` |
| **Qwen** | چرخه حیات، FSM، تفکیک وظایف و مدل‌های داده | **PASS** | 0 | 0 | `docs/coordination/QWEN_P3_MACRO_EPIC_23_25_DISCOVERY_REPLY.md` |
| **Claude** (ارزیاب ارشد امنیت و دیتابیس) | PostgreSQL 17 FORCE RLS، ایزولاسیون و ایندکس‌ها | **PASS** | 0 | 0 | `docs/coordination/CLAUDE_P3_MACRO_EPIC_23_25_DISCOVERY_REPLY.md` |

---

## ۲. مستندات کانونیکال معماری نهایی‌شده
1. **سند مرزبندی کلان معماری**:
   [`docs/architecture/P3_MACRO_EPIC_23_25_BOUNDARY_PLAN.md`](file:///g:/project/codesho/codesho/worktrees/phase1-engineering-readiness/docs/architecture/P3_MACRO_EPIC_23_25_BOUNDARY_PLAN.md)
2. **اسکریپت کانونیکال DDL و RLS نسخه v1.1-HARDENED**:
   [`docs/architecture/p3_macro_epic_23_25_schema_ddl.sql`](file:///g:/project/codesho/codesho/worktrees/phase1-engineering-readiness/docs/architecture/p3_macro_epic_23_25_schema_ddl.sql)
3. **منیفست فایل‌های اجرایی بدون وایلدکارت**:
   [`docs/coordination/P3_MACRO_EPIC_23_25_WRITE_MANIFEST.md`](file:///g:/project/codesho/codesho/worktrees/phase1-engineering-readiness/docs/coordination/P3_MACRO_EPIC_23_25_WRITE_MANIFEST.md)
4. **دوسیه جامع دیسکاوری کلان**:
   [`docs/coordination/P3_MACRO_EPIC_23_25_DISCOVERY_DOSSIER.md`](file:///g:/project/codesho/codesho/worktrees/phase1-engineering-readiness/docs/coordination/P3_MACRO_EPIC_23_25_DISCOVERY_DOSSIER.md)
5. **ماتریس آزمون‌های منفی ۳۵ گانه (N1 تا N35)**:
   پوشش کامل ایزولاسیون تنانت، کلیدهای مرکب، منع خود-تأییدی، تغییرناپذیری محتوا، منع مطلق رتبه‌بندی دانش‌آموز، و منع بازاتصال شواهد تاریخی.

---

## ۳. درخواست گشایش ران‌تایم (Runtime Unlock Request)
با توجه به احراز اجماع ۱۰۰٪ ممیزان ناوگان، ثبت کامیت‌های تغییرناپذیر و فقدان هرگونه بلاکر، تقاضای صدور کلید ران‌تایم از سوی فرمانده محترم می‌گردد:

```text
COMMANDER_P3_MACRO_EPIC_23_25_RUNTIME_UNLOCK: GRANTED
```
تا پیاده‌سازی ۱۹ مدل کانونیکال، مایگریشن‌های اسکیما و RLS، سرویس‌های دامنه، روت‌های REST API و ماتریس تست‌های ۳۵ گانه بلافاصله آغاز گردد.
