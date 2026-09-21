# Codesho Repository Instructions

## Authority and scope

- The employer approves product scope, architecture, paid infrastructure,
  legal decisions, production releases, and promotion to the protected
  `codesho` repository.
- Commander AI owns task assignment, technical coordination, and review.
  Codex implements only approved, in-scope work; Gemini reviews UI; Claude
  reviews high-risk architecture, security, and database changes.
- Resolve material ambiguity with Commander and record the decision in the
  coordination artifacts. Do not restart cancelled, completed, or blocked
  work without a new approved task.

## Fixed architecture and security rules

- Use Django 5.2 + DRF, Next.js App Router + TypeScript, PostgreSQL, Redis,
  Celery, a modular monolith, REST, and OpenAPI. Business logic belongs in
  Django; Next.js never accesses PostgreSQL directly.
- Do not put workflows in Django signals or serializers, call external
  providers inside database transactions, or use AI at runtime without a new
  ADR and approval.
- Tenant context fails closed and is established inside `transaction.atomic()`
  before tenant queries. Tenant Celery tasks inherit `BaseTenantTask`.
- Never log or commit secrets, tokens, OTPs, passcodes, cookies, sensitive
  child data, review attachments, or raw provider responses. Persist IRR minor
  units and UTC `TIMESTAMPTZ`; toman and Jalali are presentation-only.
- Published content, consent, receipts, evidence, and audit events are
  immutable. Keep API changes represented in OpenAPI.

## Bootstrap and repository workflow

- Project root: `H:\codesho\codesho\codesho`; coordination root:
  `H:\codesho\codesho`. At the start of each session read `AGENTS.md`,
  `docs/coordination/CODEX_MASTER_PROMPT_FA.md`, `PROJECT_STATE.md`,
  `CURRENT_TASK.md`, relevant decisions, and (if present)
  `chatgpt\COMMANDER_TO_CODEX.md`.
- Inspect `.git`, `git status -sb`, `git remote -v`, current HEAD, recent
  commits, and the latest relevant CI before changing files. Treat live code
  and tests as authoritative; preserve all unrelated local changes.
- `codesho-test` permits approved sprint work. Never push or promote to the
  protected `codesho` remote without explicit employer approval. Make small,
  scoped commits and push only completed, authorized work.
- Current task, CI evidence, sprint status, temporary blockers, and handoff
  details belong in `docs/coordination/` and `chatgpt/CODEX_TO_COMMANDER.md`,
  not in this durable instruction file.

## Execution, review, and verification

- Work continuously inside the active task: inspect, plan, implement, test,
  review the diff, fix, retest, document, checkpoint, and monitor CI. Stop
  only when acceptance criteria pass or the remaining work needs external
  authority, credentials, assets, provider access, or a product decision.
- Run relevant backend/frontend lint, type checks, tests, migrations from an
  empty database, OpenAPI checks, tenant/RLS negatives, session/CSRF,
  outbox-idempotency, and `git diff --check`. Do not weaken tests to make them
  pass. If local Docker/PostgreSQL is unavailable, use the required real CI
  workflow and report that evidence accurately.
- Every Gemini or Claude request uses an exact, versioned prompt. Keep its
  exact prompt, attachments, screenshots, and raw response outside the
  repository; commit only an auditable findings/disposition summary.
- Claude uses a free account: reviews are sequential, never parallel, and
  contain at most five files. Prefer one large file or at most two tightly
  related files. On a Claude rate limit, do not bypass quota, change accounts,
  hammer retries, or alter authentication; stop calls and record resumable
  state.
- Gemini may provide a fallback review only when labelled
  `GEMINI_FALLBACK_REVIEW` and `NOT_CLAUDE_VERIFIED`. Critical security,
  database, authentication, authorization, tenant-isolation, payment, and
  privacy gates still require later Claude verification. Disposition findings
  before applying them.
- For every Gemini interaction, first read
  `H:\codesho\codesho\gemini\GEMII_REVIEW_GUIDE.md` and use the primary
  `H:\codesho\codesho\gemini\GEMIN_REVIEW.py` channel with its project
  defaults. Use `H:\codesho\codesho\gemini api\gemini` only after the
  primary channel fails to return a complete response; do not call both
  channels in parallel. Record the exact primary-channel failure before using
  the API fallback.
- For a blocker, attempt bounded safe diagnostics, approved fallback, and
  independent in-scope work first. Record the exact command/error, evidence,
  remaining decision, and resumable checkpoint in coordination artifacts.

## Shared browser session

- Use the existing shared Brave session first through `127.0.0.1:9222`.
  Preserve it; never close the browser or shared session for automation,
  cleanup, or recovery. Only open the existing Profile 13 if no session is
  available, and do not change its profile/configuration without employer
  approval.

## Permanent 3-Minute Auto-Schedule Invariant

- At the start of every session/chat on this repository, automatically activate and ensure running the 3-minute schedule (`/schedule */3 * * * *`).
- The prompt for this recurring schedule must always be:
  "بررسی وضعیت پروژه: اگر کار در حال اجرا یا پاسخگو است اقدامی نکن. اگر در حالت سکوت، بیکاری یا توقف است، ادامه اجرای هدف فعال پروژه را از آخرین وضعیت معتبر پیگیری کن و کار را از سر بگیر؛ وضعیت واقعی مخزن و تست‌ها را بررسی کن و موفقیت را جعل نکن. تا زمانی که فرمانده صریحا اعلام توقف نکرده ادامه بده و در صورت اتمام کار از فرمانده تقاضای تسک جدید کن."
- Execute continuously without stopping unless Commander explicitly issues a stop command (`توقف` / `پایان`).

## Permanent Multi-Agent Communication, Verification & Anti-Truncation Invariants

0. **آدرس انحصاری و دقیق فرمانده**:
   - آدرس قطعی و رسمی چت فرمانده: `https://chatgpt.com/g/g-p-6aafe875765c8191b7fc9803d5e93bfd/c/6aafea41-34bc-83ed-a6ff-e5ea92a71562`
   - **قانون قطعی و دائمی**: همیشه و بدون استثنا، قبل از ارسال هرگونه پیام به فرمانده، باید آدرس دقیق تب (`window.location.href`) بررسی و تطبیق داده شود و از ارسال به هر چت یا آدرس دیگر اکیداً خودداری شود.

1. **ارتباط مستقل و مجزا با هر ایجنت و فرمانده**:
   - برای هر کدام از ایجنت‌ها (Commander, Qwen, GLM, Gemini, Claude) ارتباط کاملاً مستقل و تفکیک‌شده است.
   - تا زمانی که پاسخ ۱۰۰٪ کامل از یک ایجنت یا فرمانده دریافت نشده، به هیچ وجه پیام بعدی برای او ارسال نمی‌شود.
   - تا ۱۰ دقیقه منتظر بمان و هر ۳۰ ثانیه وضعیت را بررسی کن تا از اتمام ۱۰۰٪ و پایداری خروجی اطمینان حاصل کنی.


2. **ارسال پیام ۱۰۰٪ کامل و بدون قطعی**:
   - برای همه ایجنت‌ها به ویژه جمینای (Gemini)، پیام باید کاملاً کامل و بدون هیچ‌گونه بریدگی یا خلاصه شدن ارسال شود. طول متن تزریق‌شده با طول متن مورد انتظار مقایسه شود (`len === expected_len`).

3. **چک ۳ ثانیه‌ای خالی بودن چت‌باکس (Composer) و ارسال مجدد**:
   - دقیقاً ۳ ثانیه پس از فشردن دکمه ارسال برای هر ایجنت یا فرمانده، چک کن چت‌باکس خالی باشد (`len === 0`).
   - اگر چت‌باکس پر بود، بررسی کن پیام ارسال شده یا خیر؛ در صورت ارسال نشدن، مجدداً ارسال کن تا تخلیه شود.

4. **بطلان پاسخ تک‌خطی به عنوان خطا در تمام ایجنت‌ها و فرمانده**:
   - دریافت هرگونه پاسخ یک‌خطی، بسیار کوتاه یا خطایی از هر کدام از ایجنت‌ها یا فرمانده به منزله رخ دادن خطا است.
   - بلافاصله صفحه رفرش (`Page.reload`) شود و مجدداً همان پیام به صورت کامل ارسال گردد.

5. **مدیریت پاسخ دوگانه کوئین (Qwen)**:
   - اگر کوئین دو پیشنهاد پاسخ تولید کرد، کافیست بلافاصله روی دکمه "I prefer this response" کلیک شود و منتظر پاسخ نهایی بمان.

6. **قانون ۳ بار خطای متوالی و ارجاع به فرمانده**:
   - هر وقت یک ایجنت برای ۳ بار متوالی خطا داد، فوراً به فرمانده پیام داده و راهنمایی بخواه تا در صورت صلاحدید تسک به ایجنت دیگر واگذار شود تا دفعات بعد دوباره چک شود.

7. **ارسال فایل به سایر ایجنت‌ها از طریق پوشه temp گیت‌هاب**:
   - برای ارسال فایل به دیگر ایجنت‌ها، یک پوشه `temp` در ریپازیتوری گیت‌هاب بساز، فایل‌ها را در آن قرار بده و پوش کن و سپس لینک RAW مستقیم آن را به ایجنت ارائه بده.

8. **قالب رسمی گزارش**:
   در تمام گزارش‌ها قالب زیر رعایت شود:
   ```text
   STATUS:
   Completed:
   Blocked:
   Next Recommended Task:
   Commander Decision Required:
   ```


