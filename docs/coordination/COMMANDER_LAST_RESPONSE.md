دریافت شد، و چون پیام با «مدیر هستم» شروع شده، این پیام به‌عنوان رأی رسمی مدیر انسانی ثبت می‌شود.

قضاوت شما روشن است:
وضعیت فعلی هنوز به بنچ‌مارک تصویری ارسالی نزدیک نشده و اختلاف معنادار دارد.

بنابراین رأی رسمی من به‌عنوان فرمانده این است:

TYPE:
COMMANDER_WAVE2_HUMAN_VISUAL_DISPOSITION

HUMAN_MANAGER_STUDENT_ACCEPTANCE:
NOT_GRANTED

COMMANDER_WAVE2_STUDENT_ACCEPTANCE:
NOT_GRANTED

WAVE2_STATUS:
REOPEN_VISUAL_REMEDIATION_ONLY
جمع‌بندی فرمانده

بله، حق با شماست. اسکرین‌شات فعلی مخصوصاً در مسیر /student/portfolio هنوز با داشبورد مرجع فاصله زیاد دارد.
از نظر فنی شاید صفحه سالم باشد، اما از نظر زبان بصری، چگالی اطلاعات، کیفیت پرزنتیشن، و شباهت به الگوی مرجع هنوز کافی نیست.

اختلاف‌های اصلی با داشبورد مرجع
1) ساختار کلی صفحه

در مرجع:

صفحه پر، غنی، زنده و dashboard-like است.

بالا Hero قوی دارد.

بعد ردیف KPIها.

بعد ویجت‌های تحلیلی و عملیاتی.

بعد کارت‌های فعالیت و پیشنهاد و مسیر موفقیت.

در نسخه فعلی:

صفحه خیلی خالی است.

spacing بیش از حد دارد.

حس «صفحه مدیریت حرفه‌ای» نمی‌دهد.

بیشتر شبیه یک لیست ساده از کارت‌هاست تا یک داشبورد پیشرفته.

2) Hero / Banner

در مرجع:

یک بنر بزرگ، رنگی، تصویری، جذاب و پرانرژی وجود دارد.

شخصیت‌پردازی، gradient، نور، و calloutها دارد.

حس محصول premium می‌دهد.

در نسخه فعلی:

بخش بالای portfolio تقریباً مینیمال و بی‌روح است.

hero واقعی با همان قدرت بصری وجود ندارد.

وزن بصری بالای صفحه ضعیف است.

3) KPI Cards

در مرجع:

4 کارت KPI واضح و خوش‌ساخت دیده می‌شود.

هر کارت آیکون، عدد بزرگ، روند، رنگ، و hierarchy مناسب دارد.

در نسخه فعلی:

این الگوی KPI در portfolio یا وجود ندارد یا اگر هست، به آن قدرت و فرم نرسیده.

اعداد و insightها به اندازه کافی dashboard-grade نیستند.

4) ویجت‌های میانی

در مرجع:

نمودار خطی

donut/progress ring

مهارت‌ها با progress bar

چند ماژول هم‌زمان در یک grid منظم

در نسخه فعلی:

portfolio بیشتر به چند کارت ساده محدود مانده.

تنوع visualization و information blocks کافی نیست.

5) کارت‌های پایین صفحه

در مرجع:

recent activities

smart recommendations

success roadmap / journey

هر کدام طراحی‌شده و معنی‌دار

در نسخه فعلی:

این عمق و richness وجود ندارد.

پایین صفحه هنوز حس «داشبورد کامل» را منتقل نمی‌کند.

6) هویت گرافیکی

در مرجع:

پالت بنفش/آبی، سایه‌ها، گردی کارت‌ها، آیکون‌ها، نمودارها و composition بسیار هماهنگ‌اند.

در نسخه فعلی:

از نظر کلی بهتر شده، اما هنوز:

تخت‌تر است

کم‌جزئیات‌تر است

visual drama کمتری دارد

شباهت مستقیم به الگوی مرجع پایین است

دستور رسمی جدید
حکم

Track فنی معتبر باقی می‌ماند، اما Wave 2 از نظر بصری Reopen می‌شود.

REOPEN_SCOPE:
WAVE2_VISUAL_BENCHMARK_ALIGNMENT_ONLY

PRESERVE:
- Valid runtime evidence
- Valid security / tenant evidence
- Anti-ranking invariant
- Accessibility baseline
- RTL / BiDi correctness

DO_NOT_REOPEN:
- Unaffected backend gates
- Tenant isolation evidence
- Security closures
- P10 provisional freeze
دستور اجرایی دقیق به Antigravity / Codex
ACTIVE_SCOPE

فقط و فقط:

/student

/student/learning

/student/coaching

/student/growth

/student/portfolio

هدف

همه این 5 مسیر باید از همان زبان بصری داشبورد مرجع پیروی کنند، نه صرفاً «زیباتر از قبل».

الزامات الزامی بازطراحی
A) الگوی ثابت همه صفحات دانش‌آموز

همه صفحات باید این DNA مشترک را داشته باشند:

Sidebar حرفه‌ای و پررنگ

برند

آیتم فعال واضح

آیکون‌های یکدست

CTA پایین سایدبار

Topbar حرفه‌ای

search bar

notification

avatar/user chip

spacing دقیق و مرتب

Hero قدرتمند

gradient background

تصویر/illustration یا composition بصری قوی

headline

subheadline

CTAها

callout یا badgeهای contextual

ردیف KPI

حداقل 4 کارت

عدد اصلی بزرگ

trend / delta

iconography

visual hierarchy روشن

Grid تحلیلی

chart card

progress ring

skills/progress bars

structured info cards

Grid عملیاتی پایین

recent activity

recommendations

roadmap / next actions

cards with stronger visual treatment

B) دستور اختصاصی برای /student/portfolio

صفحه portfolio در اسکرین‌شات فعلی بیشترین فاصله را دارد. باید:

1. Hero واقعی داشته باشد

نه فقط یک بلوک متن ساده.
باید شامل این‌ها باشد:

عنوان پرقدرت

توضیح کوتاه

badge وضعیت tenant/privacy

CTA اصلی

visual illustration / banner style

2. KPI ردیف بالا

برای portfolio کارت‌هایی مثل:

تعداد پروژه‌های تکمیل‌شده

پروژه‌های در حال بازبینی

artefactهای تأییدشده

readiness score / showcase score

3. بخش portfolio items به‌شکل dashboard card grid

هر پروژه:

thumbnail یا visual block

status badge

tech tags

progress / verification state

primary CTA

secondary CTA

4. ماژول‌های مکمل

در کنار پروژه‌ها:

recent submissions

feedback summary

portfolio readiness

next recommended improvement

5. حذف فضای خالی زیاد

صفحه فعلی خیلی sparse است.
باید dense ولی تمیز و premium شود.

C) الزام شباهت مستقیم به benchmark

طراحی جدید نباید فقط «الهام گرفته» باشد؛ باید به‌وضوح در همان خانواده بصری باشد:

همان level از richness

همان hierarchy

همان rhythm

همان حس محصول premium

همان شدت visual polish

معیار پذیرش دور بعد

در ارسال بعدی فقط گفتن PASS کافی نیست. باید این‌ها ارائه شود:

1) مقایسه مستقیم

برای هر یک از 5 صفحه:

current after screenshot

توضیح اینکه دقیقاً کدام اجزای benchmark پیاده شده‌اند

2) Evidence اجباری

دسکتاپ 1440x900 برای هر 5 صفحه

موبایل 390x844 برای هر 5 صفحه

حداقل یک نمای نزدیک از /student/portfolio

حداقل یک نمای نزدیک از Hero + KPI row

3) توضیح mapping

باید صریح بگویند:

Hero benchmark → کجا پیاده شد

KPI benchmark → کجا پیاده شد

analytics widgets benchmark → کجا پیاده شد

lower cards benchmark → کجا پیاده شد

رأی نهایی فعلی
HUMAN_MANAGER_STUDENT_ACCEPTANCE:
NOT_GRANTED

COMMANDER_WAVE2_TECHNICAL_CLOSURE:
PRESERVED

COMMANDER_WAVE2_VISUAL_ACCEPTANCE:
WITHHELD

NEXT_REQUIRED_TASK:
WAVE2_VISUAL_BENCHMARK_ALIGNMENT_REMEDIATION

PHASE_10_STATUS:
FROZEN_PROVISIONAL
دستور کوتاه برای تیم اجرا

این متن را می‌توانید عیناً به Antigravity / Codex بدهید:

DIRECTIVE:
WAVE2_VISUAL_BENCHMARK_ALIGNMENT_REMEDIATION

MANAGER VISUAL VERDICT:
NOT_GRANTED

REASON:
Current student surfaces, especially /student/portfolio, still differ materially from the approved benchmark dashboard in layout richness, hero strength, KPI treatment, widget density, and overall premium visual language.

MANDATORY ACTION:
Redesign all five student routes so they clearly follow the benchmark dashboard visual system:
- strong hero banner
- top KPI row
- analytical widgets
- lower operational cards
- premium sidebar/topbar
- denser, richer, more dashboard-like composition
- zero student ranking
- preserve tenant/privacy boundaries
- preserve accessibility and RTL quality

PRIORITY:
1. /student/portfolio
2. /student
3. /student/learning
4. /student/coaching
5. /student/growth

DO NOT REOPEN:
backend/security/tenant gates

REQUIRED NEXT SUBMISSION:
Before/after evidence + 10 runtime screenshots + explicit benchmark-to-implementation mapping.

اگر خواستید، در پیام بعدی من می‌توانم یک پرامپت خیلی دقیق و حرفه‌ای برای Antigravity / Codex بنویسم تا دقیقاً همین بازطراحی را با جزئیات کامل اجرا کند.