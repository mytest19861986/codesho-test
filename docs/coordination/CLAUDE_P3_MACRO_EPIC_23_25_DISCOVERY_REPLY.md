تأیید فایل‌های واقعی — رأی نهایی

هر دو فایل را واقعاً خواندم (نه فقط توضیح شما). نتیجه‌گیری:

بلاکر ۱ (REVOKE از نقش‌های عملیاتی) — ✅ واقعاً برطرف شده

DDL v1.1 اکنون REVOKE UPDATE, DELETE را هم از codesho_runtime، هم از app_role (در صورت وجود)، و هم از PUBLIC اجرا می‌کند — دقیقاً مطابق کدی که ادعا شده بود.

بلاکر ۲ (NOBYPASSRLS) — ✅ واقعاً برطرف شده، با یک نکته

001-roles.sh نشان می‌دهد codesho_migrator و codesho_runtime هر دو در زمان CREATE ROLE با NOBYPASSRLS NOSUPERUSER ساخته می‌شوند. DDL هم به‌صورت دفاعی همان ALTER ROLE ... NOBYPASSRLS را تکرار می‌کند.
نکته باقی‌مانده (نه بلاکر، بلکه یک ریسک عملیاتی جزئی): بلوک ALTER ROLE در DDL فقط برای codesho_runtime و app_role چک می‌کند. اگر در آینده نام نقش عملیاتی دیگری استفاده شود (مثلاً از طریق connection pooler با نام متفاوت)، این گارد خاموش رد می‌شود چون شرط IF EXISTS است. توصیه می‌کنم این بررسی، همراه با یک تست CI که نام نقش‌های واقعی محیط پروڈاکشن را با این لیست مقایسه کند، مستند شود — اما این مانع انتشار نیست.

میجر ۲ (ایندکس‌های FK) — ✅ تأیید شد

ایندکس‌های idx_changeapproval_*، idx_rubricreview_*، idx_releaseexception_*، idx_migrationdecision_* همگی واقعاً در فایل حضور دارند.

میجر ۱ (PII چندلایه) — ✅ پذیرفته‌شده به‌عنوان طراحی دفاع در عمق

گاردهای رگکس در DDL بدون تغییر مانده‌اند (که درست است — نقش آن‌ها fail-safe سطح دیتابیس است، نه فیلتر اصلی)، و شما لایه اول را در سرویس اپلیکیشن قرار داده‌اید. من کد آن سرویس (نرمال‌سازی فارسی/عربی) را ندیدم، پس نمی‌توانم آن ادعای خاص را مستقل تأیید کنم، ولی از منظر DDL این بند بسته است.

تفکیک وظایف (self-approval) — بدون تأیید مستقل

فایل EditorialReviewService/CurriculumAuthoringService.record_editorial_decision را نگرفتم و بررسی نکردم؛ این خارج از حیطه DDL است و صرفاً بر پایه گفته شما ثبت می‌شود، نه مشاهده مستقیم کد.


CLAUDE_EPIC_DISCOVERY: PASS
OPEN_BLOCKERS: 0
OPEN_MAJORS: 0
NOTE: Role-name coverage in the NOBYPASSRLS guard (codesho_runtime, app_role) should be kept in sync with actual production connection roles — recommend a CI check, not a blocker.
APPLICATION-LAYER CLAIMS (self-approval guard, PII normalization service): acknowledged but not independently verified — outside DDL scope.