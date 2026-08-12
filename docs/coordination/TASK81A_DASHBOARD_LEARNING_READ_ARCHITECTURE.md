# Task81A Dashboard Learning Read Architecture Coordination

TASK_ID: `SPRINT1-UI-LEARNING-DASHBOARD-READ-INTEGRATION-ARCHITECTURE-81A`

STATUS: `ARCHITECTURE_ONLY / AUTHORIZED`

BASE_SHA: `29b1b4d03f2043f9a45bd791b4af26260fa71c55`

BRANCH: `codex/task81a-dashboard-learning-read-architecture`

PRIMARY_DECISION:
`docs/decisions/2026-08-11-student-dashboard-learning-read-integration-architecture-81a.md`

## Scope

Task81A defines the later Dashboard-to-Course/Lesson read integration. It does
not implement frontend behavior or change backend, OpenAPI, tests,
dependencies, migrations, workflows, Compose, or production state.

## Inspected contracts

- Dashboard entry: `frontend/src/app/dashboard/page.tsx`
- Data boundary: `frontend/src/features/dashboard/DashboardDataBoundary.tsx`
- Session boundary: `frontend/src/features/auth/authClient.ts`
- Dashboard model/screen/state and focused tests under
  `frontend/src/features/dashboard/`
- API contract: `docs/openapi.yaml` CourseResults/LessonResults operations
- Architecture authority: Task80A ADR/review/coordination and merged Task80B

## Required provider sequence

1. Gemini: advisory UI/RTL/accessibility/product review.
2. Qwen: independent architecture/security challenge.
3. Claude: architecture hard gate after complete evidence and raw prior
   responses are available.

No provider verdict is inferred or fabricated. Task81B remains unauthorized
until Commander receives a real Claude PASS and issues a separate task.

## Current blockers

`PROVIDER_REVIEWS_PENDING` — this is the required review sequence, not an
architecture failure. Runtime implementation remains unauthorized by scope.

## Validation target

Before commit: exact-base check, coordination/decision-only changed paths,
full diff review, `git diff --check`, no secrets/PII, and no runtime changes.
