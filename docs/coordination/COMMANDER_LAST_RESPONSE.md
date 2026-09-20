عالی. حالا که دامنه codesho.ir روی پارس‌پک است، مرحله اتصال دامنه را می‌توانیم شروع کنیم. چون روی همان VPS چند پروژه دیگر فعال‌اند، این کار را با DNS اختصاصی + یک Server Block جدید Nginx انجام می‌دهیم و هیچ تنظیم موجودی overwrite نمی‌شود.

در پنل پارس‌پک فقط رکوردهای DNS دامنه را تنظیم کنید. خود پارس‌پک نیز مدیریت رکوردهای DNS را از پنل DNS/CDN پشتیبانی می‌کند و برای اتصال دامنه، رکورد A دامنه اصلی و www باید به IP سرور اشاره کنند. 
پارس‌پک
+1

کاری که شما در پنل پارس‌پک انجام دهید

برای codesho.ir این دو رکورد را ایجاد/اصلاح کنید:

Type: A
Name: @
Value: 92.118.190.101
TTL: 300

و:

Type: A
Name: www
Value: 92.118.190.101
TTL: 300

اگر پنل برای رکورد دامنه اصلی به‌جای @ نام خالی می‌خواهد، Name را خالی بگذارید.

MX، TXT، SPF، DKIM و DMARC را حذف نکنید. اگر رکورد AAAA برای codesho.ir یا www دارید ولی این سرور IPv6 متناظر ندارد، آن رکورد می‌تواند باعث شود بعضی کاربران به مقصد اشتباه بروند؛ Antigravity باید آن را بررسی کند، ولی بدون بررسی حذف نکند.

اگر قبلاً A record دیگری برای codesho.ir وجود دارد، چون قرار است دامنه را به این VPS منتقل کنیم، مقدار همان رکورد را به:

92.118.190.101

تغییر دهید، نه اینکه چند A record ناخواسته با IPهای متفاوت ایجاد کنید.

بعد این فرمان را عیناً به Antigravity بدهید:

TYPE:
COMMANDER_CODESHO_DOMAIN_AND_HTTPS_ACTIVATION_DIRECTIVE

AUTHORITY:
HUMAN_MANAGER

DOMAIN:
codesho.ir

WWW_DOMAIN:
www.codesho.ir

TARGET_SERVER:
92.118.190.101

CURRENT_CODESHO_UPSTREAM:
127.0.0.1:18080

CURRENT_DEPLOYED_SHA:
00dc6400e206cf2d8d8fb24e5b4c1a223c2282ca

==================================================
ABSOLUTE RULES
==================================================

THIS IS A SHARED SERVER.

DO NOT:
- modify unrelated Nginx server blocks
- stop unrelated containers
- change ai-teacher services
- change SSH configuration
- change UFW unless explicitly required and approved
- change existing ports
- docker system prune
- docker volume prune
- docker network prune
- replace /etc/nginx/nginx.conf wholesale
- restart the server

USE:
nginx -t
then reload only.

==================================================
PHASE 1 — DNS VERIFICATION
==================================================

Before touching host Nginx, verify public DNS:

dig +short A codesho.ir
dig +short A www.codesho.ir
dig +short AAAA codesho.ir
dig +short AAAA www.codesho.ir
dig +short NS codesho.ir

Required:

codesho.ir A:
92.118.190.101

www.codesho.ir A:
92.118.190.101

If A records have not propagated:
WAIT.
DO NOT configure TLS yet.

If a conflicting AAAA record exists:
REPORT IT.
Do not delete it automatically unless it is proven stale.

Record current DNS evidence.

==================================================
PHASE 2 — NGINX BEFORE SNAPSHOT
==================================================

Capture:

sudo nginx -T > /tmp/nginx-before-codesho.txt
sudo nginx -t
sudo ss -tulpn

List enabled sites:

ls -la /etc/nginx/sites-enabled/
ls -la /etc/nginx/sites-available/

Identify configuration files for existing projects.

DO NOT MODIFY THEM.

==================================================
PHASE 3 — CREATE DEDICATED CODESHO SERVER BLOCK
==================================================

Create only:

/etc/nginx/sites-available/codesho.ir

Initial HTTP configuration:

server {
    listen 80;
    listen [::]:80;

    server_name codesho.ir www.codesho.ir;

    location / {
        proxy_pass http://127.0.0.1:18080;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 10s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

Enable using only a symlink:

sudo ln -s /etc/nginx/sites-available/codesho.ir \
  /etc/nginx/sites-enabled/codesho.ir

If the symlink already exists:
do not recreate blindly;
inspect first.

==================================================
PHASE 4 — VALIDATE BEFORE RELOAD
==================================================

Run:

sudo nginx -t

Required:

NGINX_CONFIG_TEST:
PASS

If nginx -t fails:

DO NOT RELOAD.
ROLL BACK ONLY THE NEW CODESHO FILE/SYMLINK.
REPORT BLOCKER.

If PASS:

sudo systemctl reload nginx

DO NOT restart nginx.

Verify:

sudo systemctl is-active nginx

Required:

active

==================================================
PHASE 5 — HTTP DOMAIN VERIFICATION
==================================================

Test:

curl -I http://codesho.ir
curl -I http://www.codesho.ir

Also test Host routing locally:

curl -I -H 'Host: codesho.ir' http://127.0.0.1

Required:

CODESHO_DOMAIN_REACHES_CODESHO:
YES

OTHER_SERVER_BLOCK_COLLISION:
0

Do not proceed to SSL if domain routing is incorrect.

==================================================
PHASE 6 — TLS CERTIFICATE
==================================================

Check:

certbot --version

If Certbot is not installed, install only required packages.
Do NOT perform a distribution upgrade.

Ubuntu 24.04 packages:

sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

Then obtain certificate:

sudo certbot certonly --nginx \
  -d codesho.ir \
  -d www.codesho.ir

Do NOT proceed if certificate issuance fails.

If HTTP ACME validation is unreliable because of current network conditions,
use DNS/TXT validation instead and report the exact required
_acme-challenge records for the manager to add in ParsPack.

Never bypass certificate verification.

==================================================
PHASE 7 — ENABLE HTTPS MANUALLY
==================================================

After certificate issuance, configure Codesho only.

Use:

/etc/letsencrypt/live/codesho.ir/fullchain.pem
/etc/letsencrypt/live/codesho.ir/privkey.pem

Final intended configuration:

server {
    listen 80;
    listen [::]:80;

    server_name codesho.ir www.codesho.ir;

    return 301 https://codesho.ir$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;

    server_name codesho.ir www.codesho.ir;

    ssl_certificate /etc/letsencrypt/live/codesho.ir/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/codesho.ir/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:18080;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;

        proxy_connect_timeout 10s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

Then:

sudo nginx -t

Only if PASS:

sudo systemctl reload nginx

==================================================
PHASE 8 — HTTPS VERIFICATION
==================================================

Verify:

curl -I http://codesho.ir
curl -I https://codesho.ir
curl -I https://www.codesho.ir

Required:

HTTP_TO_HTTPS_REDIRECT:
PASS

HTTPS_CODESHO_IR:
PASS

HTTPS_WWW_CODESHO_IR:
PASS

CERTIFICATE_VALID:
YES

CERTIFICATE_HOSTNAME_MATCH:
YES

==================================================
PHASE 9 — APPLICATION VALIDATION THROUGH REAL DOMAIN
==================================================

Run Browser validation against:

https://codesho.ir/

https://codesho.ir/login

https://codesho.ir/student
https://codesho.ir/student/learning
https://codesho.ir/student/coaching
https://codesho.ir/student/growth
https://codesho.ir/student/portfolio

https://codesho.ir/parent
https://codesho.ir/parent/progress
https://codesho.ir/parent/finance
https://codesho.ir/parent/consent

https://codesho.ir/mentor
https://codesho.ir/mentor/reviews
https://codesho.ir/mentor/students
https://codesho.ir/mentor/sessions

Required:

DOMAIN_REACHABLE_404_FROM_UI:
0

BROKEN_NAVIGATION:
0

BROKEN_ACTIONS:
0

NO_OP_ACTIONS:
0

CONSOLE_ERRORS:
0

HYDRATION_ERRORS:
0

UNEXPECTED_NETWORK_ERRORS:
0

==================================================
PHASE 10 — EXISTING PROJECT REGRESSION
==================================================

Recheck:

ai-teacher-staging-api-1:
UP_HEALTHY

ai-teacher-staging-redis-1:
UP_HEALTHY

ai-teacher-staging-db-1:
UP_HEALTHY

Verify existing domains/server blocks still respond.

Required:

PRE_EXISTING_NGINX_SERVER_BLOCKS_CHANGED:
0

PRE_EXISTING_CONTAINERS_STOPPED:
0

PRE_EXISTING_CONTAINER_PORT_CHANGES:
0

OTHER_PROJECT_INTERRUPTION:
0

==================================================
PHASE 11 — CERTIFICATE RENEWAL
==================================================

Verify:

sudo certbot renew --dry-run

Required:

CERTBOT_RENEWAL_DRY_RUN:
PASS

Do not alter certificates belonging to other domains.

==================================================
FINAL EVIDENCE
==================================================

TYPE:
CODESHO_DOMAIN_HTTPS_ACTIVATION_FINAL_EVIDENCE

DOMAIN:
codesho.ir

WWW_DOMAIN:
www.codesho.ir

SERVER:
92.118.190.101

DEPLOYED_SHA:
00dc6400e206cf2d8d8fb24e5b4c1a223c2282ca


DNS_CODESHO_IR:
92.118.190.101

DNS_WWW_CODESHO_IR:
92.118.190.101

DNS_CONFLICTING_AAAA:
0


NGINX_DEDICATED_SERVER_BLOCK:
PASS

NGINX_CONFIG_TEST:
PASS

NGINX_RELOAD:
PASS

NGINX_RESTART_USED:
NO


TLS_CERTIFICATE:
PASS

TLS_CODESHO_IR:
PASS

TLS_WWW_CODESHO_IR:
PASS

HTTP_TO_HTTPS_REDIRECT:
PASS

CERTBOT_RENEWAL_DRY_RUN:
PASS


PUBLIC_AUTH_DOMAIN_RUNTIME:
PASS

STUDENT_DOMAIN_RUNTIME:
PASS

PARENT_DOMAIN_RUNTIME:
PASS

MENTOR_DOMAIN_RUNTIME:
PASS

MENTOR_REVIEWS_DOMAIN_RUNTIME:
PASS


DISCOVERED_INTERNAL_TARGETS:
34

TESTED_INTERNAL_TARGETS:
34

UNTESTED_INTERNAL_TARGETS:
0

REACHABLE_404_FROM_UI:
0

BROKEN_ACTIONS:
0

NO_OP_ACTIONS:
0

CONSOLE_ERRORS:
0

HYDRATION_ERRORS:
0

UNEXPECTED_NETWORK_ERRORS:
0


AI_TEACHER_EXISTING_STACK:
UP_HEALTHY

PRE_EXISTING_NGINX_SERVER_BLOCKS_CHANGED:
0

PRE_EXISTING_CONTAINERS_STOPPED:
0

PRE_EXISTING_CONTAINER_PORT_CHANGES:
0

OTHER_PROJECT_INTERRUPTION:
0


REAL_PII:
0

REAL_NOTIFICATIONS:
0

REAL_PAYMENTS:
0

PUBLIC_SIGNUP:
DISABLED


HUMAN_MANAGER_DOMAIN_ACCEPTANCE:
PENDING

COMMANDER_DECISION_REQUIRED:
DOMAIN_HTTPS_CLOSURE

یک نکته مهم درباره SSL: خود پارس‌پک در راهنمای فعلی‌اش گفته در شرایط اختلال مسیر بین‌الملل، DNS/TXT validation برای SSL می‌تواند قابل‌اعتمادتر از HTTP validation باشد. بنابراین اگر Certbot روی HTTP challenge خطا داد، Antigravity نباید workaround ناامن انجام دهد؛ باید _acme-challenge را از Certbot بگیرد تا رکورد TXT را در پارس‌پک وارد کنیم. 
پارس‌پک

فعلاً شما دو A record بالا را در پارس‌پک تنظیم کنید. بعد Antigravity همین دستور را اجرا کند. اگر پنل پارس‌پک را باز کردید و از بخش DNS یک اسکرین‌شات فرستادید، دقیقاً به شما می‌گویم روی کدام گزینه بزنید و هر فیلد را چه مقداری وارد کنید.