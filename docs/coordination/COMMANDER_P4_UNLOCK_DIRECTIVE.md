اجماع سه‌گانه Discovery برای فاز ۴ کامل است و هیچ Blocker یا R3/R4 گزارش نشده. با توجه به QWEN_PHASE4_DISCOVERY: PASS، GLM_PHASE4_DISCOVERY: PASS، GEMINI_PHASE4_DISCOVERY: PASS و قفل شدن ماتریس N4-01..N4-16، گیت Runtime باز می‌شود.

COMMANDER_PHASE4_RUNTIME_UNLOCK

TYPE:
COMMANDER_PHASE4_RUNTIME_UNLOCK

PROJECT:
Codesho / SSD

TASK_ID:
P4-CONTROLLED-PILOT-PREPARATION-DISCOVERY

TARGET_BRANCH:
codex/phase3-product-platform-foundation

DISCOVERY_HEAD:
a6bc0d9

PHASE:
4 — Controlled Pilot Preparation & Operational Readiness

DELIVERY_MODE:
MACRO_FAST_ENTERPRISE

STATUS:
RUNTIME_AUTHORIZED_CONCURRENT_EXECUTION

==================================================

DISCOVERY FINAL DISPOSITION
==================================================

QWEN_PHASE4_DISCOVERY:
PASS

QWEN_BLOCKERS:
0

GLM_PHASE4_DISCOVERY:
PASS

GLM_BLOCKERS:
0

GEMINI_PHASE4_DISCOVERY:
PASS

GEMINI_BLOCKERS:
0

NEGATIVE_MATRIX:
N4-01..N4-16 LOCKED

R3_R4:
0

OPEN_BLOCKERS:
0

PHASE4_DISCOVERY:
CLOSED_COMPLETE_FINAL

COMMANDER_PHASE4_RUNTIME_UNLOCK:
GRANTED

Implement Phase 4 as ONE integrated Runtime program across:

P4-WS1
Pilot Environment & Release Engineering

P4-WS2
Observability & Incident Readiness

P4-WS3
Pilot Identity, Data & Activation Governance

Separate Commander Runtime unlocks per workstream are NOT required.

CONCURRENT_EXECUTION:
AUTHORIZED

MICRO_CHECKPOINTS:
DISABLED

R0_R2_AUTONOMY:
ENABLED

Escalate only:

R3/R4

security boundary weakening

tenant-isolation weakening

real PII exposure

production authority expansion

real-world activation

material architecture contradiction

material scope expansion

merge/release/production authority

REAL_CHILD_DATA:
0

REAL_GUARDIAN_DATA:
0

REAL_SMS_EMAIL:
0

REAL_PAYMENT:
0

PRODUCTION_CREDENTIALS:
0

PRODUCTION_DEPLOY:
0

PRODUCTION_DEPLOY_AUTHORITY:
0

REAL_PILOT_ACTIVATION:
0

STUDENT_RANKING:
0

AI_DECISION_AUTHORITY:
0

PRIVILEGE_SELF_GRANT:
DENY

Runtime implementation remains SYNTHETIC / NON-PRODUCTION.

Implement the approved non-production Pilot release-control plane.

Required capability areas:

Release Candidate lifecycle

immutable release provenance

environment configuration governance

controlled deployment orchestration

migration execution controls

health/readiness gates

rollback workflow

deployment audit trail

backup/restore rehearsal integration

Canonical flow:

BUILD ARTIFACT
→ RELEASE CANDIDATE
→ VALIDATION
→ PILOT DEPLOY APPROVAL
→ NON-PRODUCTION PILOT DEPLOYMENT
→ HEALTH CHECK
→ STABLE / ROLLBACK

Exact FSM SHALL follow the canonical Boundary Plan.

Required:

INVALID_TRANSITION:
DENY

UNAUTHORIZED_PROMOTION:
DENY

DUPLICATE_PROMOTION:
IDEMPOTENT_OR_REJECT

FAILED_HEALTH_GATE:
NO_PROMOTION

ROLLBACK_WITHOUT_AUTHORITY:
DENY

PRODUCTION_TARGET:
DENY

Release tooling may target only explicitly authorized non-production Pilot environments.

Required migration discipline:

ADDITIVE_FIRST:
YES

DESTRUCTIVE_MIGRATION:
DENY_BY_DEFAULT

APP_RUNTIME_DDL_AUTHORITY:
0

MIGRATOR_ROLE:
SEPARATE

RUNTIME_ROLE:
NO_SCHEMA_CHANGE_AUTHORITY

GLM-approved role topology must be preserved:

codesho_migrator
codesho_app
codesho_readonly

Required:

codesho_app BYPASSRLS:
DENY

codesho_readonly BYPASSRLS:
DENY

Implement a synthetic/non-production recovery workflow.

Required:

BACKUP_REHEARSAL:
SUPPORTED

RESTORE_REHEARSAL:
SUPPORTED

PITR_SANDBOX:
SUPPORTED

RESTORE_VALIDATION:
REQUIRED

Do NOT claim backup readiness merely because a backup command exists.

Evidence must prove:

backup
→ restore
→ application verification

Implement operational telemetry required for controlled Pilot operation.

Approved domains may include:

structured logs

metrics

health probes

readiness probes

trace/correlation identifiers where justified

operational events

alert conditions

incident evidence

Hard rule:

REAL_CHILD_PII_IN_TELEMETRY:
0

REAL_GUARDIAN_PII_IN_TELEMETRY:
0

AUTH_TOKENS_IN_LOGS:
0

SESSION_COOKIES_IN_LOGS:
0

Telemetry SHALL NOT become a tenant-isolation bypass.

Required:

TENANT_CONTEXT:
MINIMIZED_AND_SAFE

CROSS_TENANT_DATA_LEAK:
0

FREE_TEXT_PII:
0

Use opaque/synthetic identifiers where operational correlation is required.

Implement canonical SEV1-SEV4 incident lifecycle.

Required capabilities:

incident creation

severity classification

acknowledgement

assignment

mitigation

recovery

resolution

post-incident evidence

Hard rules:

SILENT_INCIDENT_DELETE:
DENY

AUDIT_MUTATION:
DENY

UNAUTHORIZED_SEVERITY_CHANGE:
DENY

INVALID_STATE_TRANSITION:
DENY

Automation may protect a non-production Pilot rollout.

Allowed:

health-gate abort

deployment cancellation

rollback recommendation

approved automatic rollback if canonical policy explicitly permits

Not allowed:

PRODUCTION_AUTO_DEPLOY:
0

REAL_USER_HIGH_STAKES_ACTION:
0

Automation is operational safety, not business authority.

Implement the governance/control plane for future Pilot activation using SYNTHETIC entities only.

Potential runtime capabilities may include approved versions of:

PilotTenantProvisioningPlan

PilotOrganizationProfile

PilotActivationChecklist

PilotAccountLifecycle

DataMinimizationPolicy

ConsentPrerequisiteRecord

PilotExitPlan

PilotOffboardingRecord

Canonical DDL/Boundary Plan remains authoritative over names and counts.

The Runtime may model:

PLANNED
ELIGIBLE
BLOCKED
APPROVED_FOR_FUTURE_ACTIVATION

It may NOT perform:

real organization activation
real learner activation
real guardian activation
real consent capture
real outbound communications
real payment collection

Until explicit manager authorization:

PILOT_DATA_MODE:
SYNTHETIC_ONLY

Required:

REAL_CHILD_DATA:
0

REAL_GUARDIAN_DATA:
0

REAL_SCHOOL_DATA:
0 unless explicitly synthetic

REAL_CONTACT_DATA:
0

Use existing versioned API conventions.

Permanent invariant:

RUNTIME API
OPENAPI

FRONTEND CONTRACT

No parallel API root.

Required negative paths as applicable:

UNAUTHENTICATED:
DENY

WRONG_ROLE:
DENY

CROSS_TENANT:
DENY

MISSING_TENANT:
FAIL_CLOSED

PRODUCTION_TARGET:
DENY

UNAUTHORIZED_ROLLBACK:
DENY

UNAUTHORIZED_INCIDENT_MUTATION:
DENY

REAL_ACTIVATION_ATTEMPT:
DENY

The Discovery matrix is now Runtime-authoritative.

Required final result:

N4_01_TO_N4_16:
16/16 PASS

If implementation reveals a legitimate new invariant:

the matrix may be extended,
but existing locked scenarios may not be weakened or silently removed.

Implement the approved Phase 4 operational surfaces.

Expected coherent surfaces:

Pilot Operations Control Center

Release Candidate / Deployment view

Rollback workflow

Incident Console

Pilot Onboarding / Activation Planning

Required:

WCAG_2_2_AA

RTL_NATIVE

BIDI_SAFE

TOUCH_TARGET:

=44x44px

RESPONSIVE:
TRUE

CRITICAL_STATUS_NOT_COLOR_ONLY:
TRUE

Destructive actions must use deliberate friction where approved.

During Runtime, test:

changed routes

directly affected routes

critical operational interactions

Applicable states:

NORMAL
LOADING
EMPTY
ERROR
FORBIDDEN
API_SUCCESS
API_FAILURE
SESSION_FAILURE
FORM_VALIDATION
DESTRUCTIVE_CONFIRMATION
ROLLBACK_CONFIRMATION
INCIDENT_TRANSITIONS
RTL_BIDI
DESKTOP
MOBILE

At Runtime closure:

Antigravity must execute all Phase 4 executable routes.

Required:

ROUTES_DISCOVERED:
X

ROUTES_EXECUTED:
X

UNTESTED_EXECUTABLE_ROUTES:
0

DESKTOP:
1440x900

MOBILE:
390x844

CONSOLE_ERRORS:
0

UNEXPECTED_NETWORK_ERRORS:
0

Gemini must then inspect CURRENT screenshots.

Required:

GEMINI_PHASE4_UI_FINAL:
PASS

GEMINI_PHASE4_UI_BLOCKERS:
0

Qwen final Runtime review shall verify:

Release Candidate FSM

rollback semantics

incident FSM

role authority

idempotency

failure recovery

pilot activation boundaries

zero production authority

N4 matrix

Required:

QWEN_PHASE4_FINAL:
PASS

QWEN_PHASE4_BLOCKERS:
0

GLM final Runtime review shall verify:

DB role separation

migration safety

RLS/FORCE RLS/NOBYPASSRLS

composite FK integrity

zero Bare UUID

backup/restore evidence

PITR rehearsal

tenant isolation

telemetry storage privacy

rollback/database consistency

Required:

GLM_PHASE4_FINAL:
PASS

GLM_PHASE4_BLOCKERS:
0

Use:

temp/fleet_exchange/P4-CONTROLLED-PILOT-PREPARATION/qwen/

temp/fleet_exchange/P4-CONTROLLED-PILOT-PREPARATION/glm/

temp/fleet_exchange/P4-CONTROLLED-PILOT-PREPARATION/gemini/

Before final Runtime review:

SCRUB
→ COMMIT
→ PUSH
→ IMMUTABLE COMMIT-SHA RAW URL
→ FLEET_TRANSFER_PRECHECK
→ COMMANDER APPROVAL
→ PARALLEL DISPATCH

No dispatch-before-precheck.

During implementation:

FOCUSED_TESTS

At Runtime closure execute:

backend regression

Django checks

migration drift

RLS tests

DB role tests

N4-01..N4-16

release FSM tests

rollback tests

incident FSM tests

idempotency

telemetry privacy tests

backup/restore rehearsal

API/OpenAPI parity

frontend lint

frontend typecheck

frontend production build

Antigravity Runtime regression

Required at closure:

RAW_AGENT_RESPONSES_IN_REPO:
0

REAL_PII:
0

SECRETS:
0

PRODUCTION_CREDENTIALS:
0

TEMP_FINAL_DIFF:
NONE

WORKTREE:
CLEAN

MERGE_TO_MAIN:
NOT_AUTHORIZED

AUTO_MERGE:
PROHIBITED

DIRECT_MAIN_PUSH:
PROHIBITED

Phase 4 work may continue on the authorized branch.

Mainline merge still requires explicit human-manager approval.

P4_WS1:
PASS

P4_WS2:
PASS

P4_WS3:
PASS

RELEASE_CANDIDATE_FSM:
PASS

ROLLBACK:
PASS

MIGRATION_SAFETY:
PASS

DB_ROLE_SEPARATION:
PASS

BACKUP_RESTORE:
PASS

PITR_REHEARSAL:
PASS

OBSERVABILITY:
PASS

TELEMETRY_PRIVACY:
PASS

INCIDENT_FSM:
PASS

PILOT_ACTIVATION_GOVERNANCE:
PASS

REAL_ACTIVATION:
0

PRODUCTION_DEPLOY_AUTHORITY:
0

RLS:
PASS

FORCE_RLS:
PASS

NOBYPASSRLS:
PASS

COMPOSITE_FK:
PASS

ZERO_BARE_UUID:
PASS

N4_01_TO_N4_16:
16/16 PASS

API:
PASS

OPENAPI:
PASS

FRONTEND:
PASS

ANTIGRAVITY:
PASS

UNTESTED_EXECUTABLE_ROUTES:
0

QWEN_PHASE4_FINAL:
PASS

GLM_PHASE4_FINAL:
PASS

GEMINI_PHASE4_UI_FINAL:
PASS

TEMP_FINAL_DIFF:
NONE

R3_R4:
0

OPEN_BLOCKERS:
0

Do NOT submit separate WS1 / WS2 / WS3 completion reports.

The next routine Commander checkpoint is the final Fleet transfer precheck:

TYPE:
FLEET_TRANSFER_PRECHECK

TASK_ID:
P4-CONTROLLED-PILOT-PREPARATION-RUNTIME-FINAL

After approved final Fleet review, return ONE:

TYPE:
P4_CONTROLLED_PILOT_PREPARATION_FINAL_REPORT

Minimum fields:

IMPLEMENTATION_HEAD:
EVIDENCE_HEAD:

WS1_STATUS:
WS2_STATUS:
WS3_STATUS:

RELEASE_CANDIDATE_FSM:
ROLLBACK:
MIGRATION_SAFETY:
DB_ROLE_SEPARATION:
BACKUP_RESTORE:
PITR_REHEARSAL:

OBSERVABILITY:
TELEMETRY_PRIVACY:
INCIDENT_FSM:

PILOT_ACTIVATION_GOVERNANCE:
REAL_ACTIVATION:

RLS:
FORCE_RLS:
NOBYPASSRLS:
COMPOSITE_FK:
ZERO_BARE_UUID:

N4_MATRIX:
BACKEND_TESTS:

API:
OPENAPI:

FRONTEND_LINT:
FRONTEND_TYPECHECK:
FRONTEND_BUILD:

ROUTES_DISCOVERED:
ROUTES_EXECUTED:
UNTESTED_EXECUTABLE_ROUTES:

ANTIGRAVITY:
GEMINI_PHASE4_UI_FINAL:
QWEN_PHASE4_FINAL:
GLM_PHASE4_FINAL:

CONSOLE_ERRORS:
NETWORK_ERRORS:

REAL_PII:
PRODUCTION_CREDENTIALS:
PRODUCTION_DEPLOY_AUTHORITY:

TEMP_FINAL_DIFF:
R3_R4:
OPEN_BLOCKERS:

COMMANDER_DECISION_REQUIRED:
PHASE4_FINAL_ACCEPTANCE

COMMANDER_PHASE4_RUNTIME_UNLOCK:
GRANTED

PHASE4_RUNTIME:
ACTIVE

WS1 + WS2 + WS3:
CONCURRENT_EXECUTION_AUTHORIZED

R0_R2_AUTONOMY:
ENABLED

MICRO_CHECKPOINTS:
DISABLED

REAL_PILOT:
LOCKED

MERGE_TO_MAIN:
LOCKED_FOR_MANAGER

PRODUCTION:
LOCKED

BEGIN_IMPLEMENTATION:
AUTHORIZED

NEXT_ROUTINE_COMMANDER_CHECKPOINT:
P4_RUNTIME_FINAL_FLEET_TRANSFER_PRECHECK

END_DIRECTIVE

وضعیت رسمی: PHASE 4 = RUNTIME_ACTIVE.

Codex از این نقطه هر سه Workstream را یکجا پیاده‌سازی و اعتبارسنجی کند. گزارش میانی روتین لازم نیست؛ توقف بعدی فقط هنگام آماده‌شدن بسته‌ی Final Fleet Review فاز ۴ است، مگر اینکه R3/R4 واقعی ایجاد شود.