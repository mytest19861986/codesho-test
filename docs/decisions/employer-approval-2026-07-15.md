# Employer Approval — Sprint Zero

Date: 2026-07-15
Status: Approved to start Sprint Zero

## Approved Architecture

- Django 5.2 LTS + Django REST Framework;
- Next.js App Router + TypeScript;
- Modular Monolith;
- PostgreSQL with `codesho` main schema and limited auxiliary schemas;
- secure Django session, HttpOnly cookie and CSRF;
- staged RLS plus application authorization;
- PgBouncer transaction pooling when needed; statement pooling prohibited;
- Django Admin for foundation operations and custom Next.js workflows for sensitive operations;
- REST + OpenAPI generated client;
- Outbox and `BaseTenantTask`;
- limited payment ledger without wallet/general accounting;
- Docker without Kubernetes initially;
- AI runtime excluded from MVP;
- code/CI module enforcement with approved cross-domain FKs.

## Infrastructure Input

- Target: Ubuntu 24.04 cloud Linux;
- Capacity: 2 vCPU, 4 GiB RAM;
- Monthly production ceiling: IRR-equivalent budget stated as 5 million toman;
- Domain/DNS: acquired;
- Managed PostgreSQL/Object Storage: technically acceptable, provider to be selected.

The 2 vCPU/4 GiB host is an Alpha topology, not an Enterprise capacity promise. PostgreSQL may need a managed or separate host as load grows.

## Commander Defaults

- VIP alpha capacity: 8 learners, configurable;
- founder is the primary alpha mentor;
- mentor capacity assumption: 8 hours/week, to be validated before sales;
- reservation TTL: 15 minutes, configurable;
- installment grace period: 7 days, configurable;
- upgrade closes at configured `upgrade_closes_at`, default seven days before the final skill gate, and always requires free capacity;
- simple waitlist enabled without automatic assignment;
- clinic/debug sessions limited to VIP;
- teen passcode: minimum six digits, five attempts, timed lockout, account/IP/device/global abuse controls and mandatory first-login change;
- aging-out transition workflow approved;
- support calendar proposal: Saturday–Wednesday 10:00–18:00 and Thursday 10:00–14:00, Asia/Tehran, configurable;
- stop VIP sales when available mentor capacity is exhausted or rolling SLA breach exceeds the configured threshold.

## Deferred Product Decisions

- final Self-paced and VIP pricing;
- final project, rubric and skill gate;
- payment, SMS, video, object storage and meeting providers;
- final support capacity and marketing launch dates.

These do not block Sprint Zero. They block their integration or production release gates.

## Privacy and Legal Defaults

- legal review of Terms, Privacy Notice, immediate service activation and child-data rules is mandatory before paid Production;
- session recording is disabled in MVP by default;
- if enabled later: separate consent, access log, encryption and default 90-day retention;
- raw OTP secret is purged after consumption/expiry; minimal security metadata follows a versioned policy;
- personal project files default to one year after enrollment/account closure unless legal or educational policy requires otherwise;
- support content defaults to two years after closure;
- financial receipts, consent evidence, security audit and dispute records follow counsel-approved statutory retention;
- account closure preserves only required financial/legal/audit evidence and removes or anonymizes other personal derivatives;
- the 18-year transition preserves historical purchase/audit facts and requires new consent/ownership rules approved by counsel.

All durations remain policy-versioned and must be approved by legal counsel before Production.

## UI and Content Defaults

- Gemini starts from employer-provided samples and creates the design system;
- brand tokens remain pending until logo/color/font approval;
- transcript is required for core learning videos;
- captions are required for the free lesson and critical launch content, then completed for all core videos before broad paid release;
- incomplete sales, FAQ and first-two-week content are tracked as product release dependencies.

## Development Authorization

The employer explicitly authorized Codex to create the Sprint Zero skeleton, Docker/CI setup, security PoCs and Foundation migrations in the `codesho-test` repository.

Final Production release authority remains with the employer until another owner is explicitly assigned.
