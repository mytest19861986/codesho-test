Thought Process
ممیزی Re-Audit P3-MACRO-EPIC-20-22 — راستی‌آزمایی بسته اثبات v1.2

درود و احترام، فرماندهی محترم.

B3 پاسخ داده شد — بسته اثبات در فرم کامل رسید: §2.1 با Pin های upstream ✓، اعلام رسمی استثنای Snapshot Provenance (دقیقاً همان متن تجویز شده) ✓، تعیین تکلیف Outbox در لایه سرویس ✓، ماتریس N1-N33 ✓، FSM چهارگانه ✓، Actor Matrix هفت‌نقشی ✓. Actor Matrix خاصِ این Epic (Curriculum Author / Program Operations) از Macro-17-19 غنی‌تر است — تقدیر می‌شود.

اما ممیزی تطبیق — که همیشه، در هر دروازه، بدون استثنا اجرا می‌شود — این بار یافته‌ای دارد که ماهیتش دقیقاً همان کلاس «فرم بدون ماده» است، در سطحی عمیق‌تر:

بسته اثبات، سیستمی را توصیف می‌کند که با DDLِ v1.1 مطابقت ندارد. سه FSM از چهار FSM، نام وضعیت‌هایی دارند که در DDL وجود ندارند؛ و ~۶ تست، به constraint هایی ارجاع می‌دهند که در DDL تعریف نشده‌اند.

رأی رسمی
text
GLM_EPIC_DISCOVERY: CHANGES_REQUIRED
OPEN_BLOCKERS: 0
OPEN_MAJORS: 2
FINDINGS: بسته اثبات ساختاراً کامل ✓ — اما ۳ FSM از ۴ FSM با
وضعیت‌های DDL ناسازگارند (نام‌های متفاوت) + ~۶ تست به constraint های
غیرموجود ارجاع می‌دهند + تست GUC غیر-UUID غایب. اصلاح متنی — یک دور.
🔴 Major ۱ — FSM-DDL Misalignment: سه ماشین، دو سیستم
FSM
	
وضعیت‌های PROOF PACKAGE
	
وضعیت‌های DDL V1.1
	
وضعیت

۳.۱ CurriculumVersion	DRAFT, REVIEW, APPROVED, PUBLISHED, RETIRED	همان پنج — مطابق ✓	✅
۳.۲ LearningSession	DRAFT, SCHEDULED, IN_SESSION, COMPLETED, RESCHEDULED, CANCELLED	SCHEDULED, IN_SESSION, COMPLETED, RESCHEDULED, CANCELLED — بدون DRAFT	🔴
۳.۳ SessionOccurrence	PENDING, OCCURRING, CONCLUDED, MISSED	PENDING, CONDUCTED, SUBSTITUTE_CONDUCTED, MISSED	🔴🔴
۳.۴ DeliveryException	OPEN, ACKNOWLEDGED, RESOLVED, WAIVED	OPEN, INVESTIGATING, RESOLVED, IGNORED	🔴🔴

پیامدها:

LearningSession: FSM از [DRAFT] شروع می‌شود؛ DDL چنین وضعیتی ندارد → INSERT با status='DRAFT' → CHECK violation در همان روز اول
SessionOccurrence: FSM دو وضعیت دارد که DDL نمی‌شناسد (OCCURRING, CONCLUDED) و DDL یک وضعیت دارد که FSM نمی‌شناسد (SUBSTITUTE_CONDUCTED)
DeliveryException: دو نام کاملاً متفاوت (ACKNOWLEDGED↔INVESTIGATING، WAIVED↔IGNORED) → هر گذاری که FSM مجاز بداند، DB رد می‌کند و برعکس

این هم‌خوانی نیست اشتباه تایپی — دو سیستم مختلف توصیف شده‌اند. اصلاح: FSM ها را با نام‌های وضعیتِ DDL هم‌راستا کنید (یا DDL را با FSM — تصمیمِ کدام، با فرماندهی است؛ مقاومت DDL بر است).

🟡 Major ۲ — Test-DDL Misalignment: ~۶ تست به مصنوع ناموجود ارجاع می‌دهند
تست
	
ارجاع در PROOF
	
واقعیت DDL V1.1

N21	chk_curriculum_semver_format + سناریوی «رشته semver نامعتبر»	وجود ندارد — semver سه ستون INT است با chk_curriculum_semver_nonnegative؛ رشته در INT اصلاً type error است نه CHECK
N24	chk_exception_resolution_order + «resolved_at < occurred_at»	وجود ندارد — DDL دارد chk_deliveryexception_resolved_order (فقط NULL/NOT NULL)؛ فیلد «occurred_at» وجود ندارد
N25	chk_release_meta_no_pii	نام متفاوت — DDL: chk_curriculumversion_metadata_no_pii
N26	«context شامل phone_number» روی delivery exception	فیلد JSONB وجود ندارد — جدول فقط description TEXT دارد (constraint: chk_deliveryexception_desc_bound)
N27	chk_session_notes_no_pii	نام متفاوت — DDL: chk_sessionoccurrence_notes_bound یا chk_learningsession_title_no_pii
N28	chk_approval_rationale_no_pii	نام متفاوت — DDL: chk_releaseapproval_comments_bound

این همان کلاس VS16-F1 است (سازوکار تست، به غیرموجود ارجاع می‌دهد) — در مقیاس بزرگ‌تر. در Implementation، این تست ها fail می‌شوند چون constraint های ارجاع‌شده وجود ندارند.

Minor
GUC هسته ۴/۵: Unset ✓ / Empty ✓ / Positive ✓ / Cross-tenant ✓ — Non-UUID غایب (N31 در Macro-17-19؛ اینجا جا افتاده) → افزودن N34
§2.1 Pin: learning_course به «VS10/VS11» نسبت داده شده — این جدول از اسلایس‌های اولیه (VS1-VS5) است؛ اصلاح attribution
FSM ۳.۲: RESCHEDULED → SCHEDULED (re-arm) — طراحی متفاوت از VS18 (RESCHEDULED آنجا terminal بود) — قابل‌دفاع، ولی باید تصمیم مستند شود
آنچه تایید شد (اعتبار genuine)
§2.1 Snapshot Exemption: دقیقاً متن درست، با Rationale صحیح («frozen payload is the sole authoritative representation») ✅
Outbox: اعلان Service-layer با transaction.atomic() — قابل قبول ✅
Actor Matrix: هفت نقش × پنج دامنه، با Anonymous/Cross-Tenant = DENY ✅
N1-N20, N22-N23, N29-N33: سازوکار و سناریو صحیح ✅
FSM ۳.۱ (CurriculumVersion): کاملاً مطابق DDL، با Actor و Guard ✅
N3 (Positive) — درس VS16 زنده است ✅
دروازه — یک دورِ متنی

بسته v1.3 (صرفاً ترازبندی — هیچ DDL جدیدی لازم نیست):
۱. FSM ۳.۲/۳.۳/۳.۴: نام وضعیت‌ها را با DDL هم‌راستا کن (یا DDL را به‌روز کن — اما یک منبع حقیقت)
۲. N21/N24-N28: constraint name ها و فیلدها را با DDL v1.1 تراز کن
۳. N34: GUC غیر-UUID (یک سطر)
۴. §2.1: اصلاح attribution اسلایس‌های upstream
۵. تصمیم مستند: RESCHEDULED terminal (VS18) یا re-arm-able (این FSM)

→ ارائه → PASS در همان نوبت. DDL شما از نوبت قبل آماده بود؛ این دور فقط proof را با آن هم‌راستا می‌کند.

رجیستر
کلاس جدید: «Proof-Artifact Identity» — بسته اثبات و DDL، دو سیستم مختلف توصیف می‌کنند؛ ثبت به‌عنوان پنجمین اصل حاکمیتی: Proof باید همان مصنوعی را توصیف کند که DDL پیاده می‌کند
Test-DDL Misalignment: کلاس VS16-F1، occurrence دوم — در مقیاس ۶ تست
بدهی‌ها: VS12-v1.4 (۱۷م) + VS16-v1.2 + Macro-17-19 §2.1
رجیستر: VS10 ✓ VS11 ✓ VS13 ✓ VS14 ✓ VS15 ✓ VS17-19 ✓ | VS12 ✗ VS16 ✗ | Macro-20-22: دور سوم — DDL ✓ / Proof ✓-فرم / Proof-DDL ✗-تراز

خلاصه تک‌جمله‌ای: DDL از نوبت قبل کامل است؛ Proof این نوبت ساختاراً کامل است؛ اما این دو، همدیگر را نمی‌شناسند. پنجاه سطر ترازبندی متنی — نام وضعیت‌ها و نام constraint ها — و هر دو به یک سیستم تبدیل می‌شوند که گواهی‌پذیر است.

با احترام،
GLM — معمار ارشد دیتابیس و امنیت | پروژه کُدشو (P3-Macro-Epic-20-22)
رأی: GLM_EPIC_DISCOVERY: CHANGES_REQUIRED