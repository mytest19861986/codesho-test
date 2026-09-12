ادامه مأموریت به این شکل ابلاغ می‌شود: از این نقطه Codex باید مستقیماً Closure سراسری Phase 3 را اجرا کند و دیگر وارد هیچ Feature جدیدی نشود.

COMMANDER_P3_FINAL_SYSTEM_CLOSURE_EXECUTION_SEQUENCE

TYPE:
COMMANDER_P3_FINAL_SYSTEM_CLOSURE_EXECUTION_SEQUENCE

PROJECT:
Codesho / SSD

TASK_ID:
P3-FINAL-SYSTEM-CLOSURE-AND-PRE-PILOT-GO-NO-GO

STATUS:
ACTIVE_EXECUTION

BRANCH:
codex/phase3-product-platform-foundation

MODE:
SYSTEM_STABILIZATION

Fetch remote state.

Verify authorized branch.

Record actual full SHA:

PHASE3_BASE_SHA:
<40_HEX_SHA>

Verify:

WORKTREE_CLEAN:
TRUE

UNCOMMITTED_PRODUCT_CHANGES:
0

UNTRACKED_PRODUCT_FILES:
0

Feature development is now frozen.

Only defect remediation and closure evidence are authorized.

Normalize final evidence for:

P3-MACRO-EPIC-20-22
P3-MACRO-EPIC-23-25
P3-MACRO-EPIC-26-28

Do NOT reopen completed implementations.

Record actual final evidence already available.

If missing final Runtime Fleet reviews genuinely do not exist, defer their validation into the Phase 3 integrated final Fleet review instead of repeating three separate Epic-level review cycles.

Target administrative state:

EPIC_20_22:
CLOSED_OR_SUBSUMED_BY_PHASE3_FINAL

EPIC_23_25:
CLOSED_OR_SUBSUMED_BY_PHASE3_FINAL

EPIC_26_28:
CLOSED_OR_SUBSUMED_BY_PHASE3_FINAL

No fabricated PASS values.

Execute full relevant backend test suite against real PostgreSQL test runtime.

Required areas:

AUTH
TENANCY
RLS
OUTBOX
FSM
IDEMPOTENCY
CONCURRENCY
CURRICULUM
ASSESSMENTS
MENTOR_OPERATIONS
GOVERNANCE
LEGAL_HOLD
PILOT_READINESS

Required result:

BACKEND_PHASE3_REGRESSION:
PASS

Report:

TESTS_COLLECTED:
X

TESTS_PASSED:
X

TESTS_FAILED:
0

TESTS_SKIPPED:
X

Any skipped security-critical test requires explicit justification.

Inspect final PostgreSQL schema and full migration history.

Required proof:

POSTGRESQL_17:
PASS

MIGRATION_GRAPH:
PASS

UNAPPLIED_MIGRATIONS:
0

MIGRATION_DRIFT:
0

RLS:
PASS

FORCE_RLS:
PASS

NOBYPASSRLS:
PASS

COMPOSITE_FK:
PASS

BARE_TENANT_UUID:
0

CROSS_TENANT_LEAKAGE:
0

AUDIT_MUTATION_ALLOWED:
0

LEGAL_HOLD_BYPASS:
0

Explicitly verify runtime DB role cannot bypass tenant isolation.

Run integrated negative authorization tests across roles.

Actors should include all relevant project roles such as:

student

mentor

admin

delegated admin

privileged reviewer

unauthorized user

Validate:

CROSS_TENANT_ACCESS:
DENY

PRIVILEGE_SELF_GRANT:
DENY

INVALID_SECOND_APPROVER:
DENY

REVOKED_ACCESS_REUSE:
DENY

UNAUTHORIZED_AUDIT_MUTATION:
DENY

LEGAL_HOLD_BYPASS:
DENY

UNAUTHORIZED_READINESS_EXCEPTION:
DENY

STUDENT_RANKING:
0

Discover every active Phase 3 API endpoint.

Generate exact inventory.

Report:

API_ENDPOINTS_DISCOVERED:
X

API_ENDPOINTS_VERIFIED:
X

Hard requirement:

API_ENDPOINTS_VERIFIED

API_ENDPOINTS_DISCOVERED

Verify:

AUTHORIZATION:
PASS

TENANT_SCOPING:
PASS

INPUT_VALIDATION:
PASS

OPENAPI_PARITY:
PASS

UNDOCUMENTED_ENDPOINTS:
0

ORPHAN_ENDPOINTS:
0

Execute:

FRONTEND_LINT
FRONTEND_TYPECHECK
FRONTEND_PRODUCTION_BUILD

Required:

FRONTEND_LINT:
PASS

FRONTEND_TYPECHECK:
PASS

FRONTEND_BUILD:
PASS

Build success does not authorize deployment.

Discover the entire executable frontend route set.

Do not manually guess the list.

Classify routes as applicable:

public

student

mentor

admin

governance/control

Create exact route inventory.

Required final accounting:

ROUTES_DISCOVERED:
X

ROUTES_EXECUTED:
X

UNTESTED_EXECUTABLE_ROUTES:
0

Execute every discovered executable route using REAL browser execution.

Required viewports:

1440x900

390x844

For applicable surfaces verify:

NORMAL
LOADING
EMPTY
ERROR
FORBIDDEN
API_SUCCESS
API_FAILURE
SESSION_FAILURE
REFRESH
NAVIGATION
FORM_VALIDATION
MODALS
DESTRUCTIVE_CONFIRMATION
KEYBOARD_ACCESS
RTL_BIDI
RESPONSIVE_LAYOUT

Required:

ANTIGRAVITY_PHASE3_FULL:
PASS

ROUTES_EXECUTED:
ROUTES_DISCOVERED

CONSOLE_ERRORS:
0

UNEXPECTED_NETWORK_ERRORS:
0

Capture current screenshots from representative surfaces.

After machine/browser gates pass, prepare final Phase 3 evidence.

QWEN package:

temp/fleet_exchange/P3-PHASE3-FINAL-CLOSURE/qwen/

Must contain exact evidence needed to audit:

domain architecture

FSMs

authorization

idempotency

historical integrity

anti-ranking

learner agency

governance semantics

GLM package:

temp/fleet_exchange/P3-PHASE3-FINAL-CLOSURE/glm/

Must contain:

final schema

migration inventory

RLS/FORCE RLS evidence

role/privilege evidence

composite FK evidence

concurrency results

tenant-isolation proof

Legal Hold/audit proof

Gemini package:

temp/fleet_exchange/P3-PHASE3-FINAL-CLOSURE/gemini/

Must contain current screenshots for representative:

learner

mentor

curriculum/admin

governance/control-center

at both desktop and mobile where materially applicable.

Before committing Fleet evidence:

REAL_PII_SCAN:
0

SECRET_SCAN:
0

TOKENS:
0

PASSWORDS:
0

AUTH_HEADERS:
0

SESSION_COOKIES:
0

PRODUCTION_CREDENTIALS:
0

UNRELATED_FILES:
0

ZERO_WILDCARDS:
PASS

STOP only at this point for the mandatory transfer approval.

Return:

TYPE:
FLEET_TRANSFER_PRECHECK

TASK_ID:
P3-PHASE3-FINAL-CLOSURE

For each agent include:

TARGET_AGENT:
PURPOSE:
EXACT_FILES:
COMMIT:
IMMUTABLE_RAW_URLS:
HTTP_STATUS:
PII_SCAN:
SECRET_SCAN:

DO NOT dispatch Qwen / GLM / Gemini before Commander approval.

After Commander transfer approval:

dispatch simultaneously to:

Qwen
GLM
Gemini

Required terminal results:

QWEN_PHASE3_FINAL:
PASS

GLM_PHASE3_FINAL:
PASS

GEMINI_PHASE3_UI_FINAL:
PASS

Required blockers:

0
0
0

R0-R2:
AUTO_REMEDIATE_AND_REREVIEW

R3-R4:
ESCALATE

Only after machine, browser and Fleet gates are green:

execute the canonical Pilot Readiness assessment.

Valid results:

READY

NOT_READY

BLOCKED

EXCEPTION_REQUIRED

READY means:

TECHNICALLY_READY_FOR_CONTROLLED_PILOT_PREPARATION

READY does NOT authorize:

production deploy
real child data
real guardian data
payments
SMS/email providers
production credentials

Before final Phase 3 report:

RAW_AGENT_RESPONSES_IN_REPO:
0

REAL_PII:
0

SECRETS:
0

UNAUTHORIZED_TEMP:
0

TEMP_FINAL_DIFF:
NONE

WORKTREE:
CLEAN

Remove Fleet transport artifacts when no longer needed using normal forward commits.

Never rewrite history.

Return ONE:

TYPE:
P3_PHASE3_FINAL_SYSTEM_CLOSURE_REPORT

Do not send intermediate routine reports.

Only interrupt Commander for:

R3
R4

or:

FLEET_TRANSFER_PRECHECK

BEGIN_STAGE_1:
AUTHORIZED

CONTINUE_THROUGH_STAGE_11:
AUTONOMOUS

STOP_AT_STAGE_12:
MANDATORY_COMMANDER_PRECHECK

FEATURE_DEVELOPMENT:
FROZEN

PRODUCTION_DEPLOY:
NOT_AUTHORIZED

END_DIRECTIVE

بنابراین اقدام فوری Codex روشن است: از Stage 1 شروع کند و بدون گزارش‌های میانی تا تکمیل Regression سراسری، Audit دیتابیس/API، Build فرانت و Antigravity Full Regression پیش برود. تنها توقف روتین بعدی باید هنگام آماده‌شدن بسته انتقال نهایی برای Qwen/GLM/Gemini باشد.