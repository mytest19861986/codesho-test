# Task81B Acceptance-Criteria Evidence Matrix (AC-01..AC-43)

TASK_ID=SPRINT1-UI-LEARNING-DASHBOARD-READ-INTEGRATION-81B
PR=#42
HEAD_UNDER_REVIEW=e98d1c575903f7b5657a20c004ea2802189e4394

## Provenance

This matrix is an auditable reconstruction of the Commander-provided Task81B
hard-gate checklist and the 38-point Claude V5 assessment exposed in the
coordination conversation. It is evidence guidance, not a fabricated claim
that the implementation passes. Claude must independently verify each item
against the supplied evidence and may mark any item unverified.

## Criteria

- AC-01: Course collection request uses the exact approved endpoint shape.
- AC-02: Lesson collection request uses the exact approved endpoint shape.
- AC-03: Requests use same-origin credentials.
- AC-04: Requests do not accept or send tenant identifiers.
- AC-05: Requests do not accept or send role/slug authority inputs.
- AC-06: Course item runtime validation rejects malformed identifiers.
- AC-07: Lesson item runtime validation rejects malformed identifiers.
- AC-08: Runtime validation rejects oversized or malformed values.
- AC-09: Runtime validation accepts only published resource state.
- AC-10: Course and lesson result cardinality is bounded.
- AC-11: Pagination is truthful and no fabricated totals/links are emitted.
- AC-12: Missing, hidden, draft, archived, and cross-tenant parents use a
  non-enumerating backend 404 boundary.
- AC-13: Empty course state is distinct and truthful.
- AC-14: Empty lesson state is distinct and truthful.
- AC-15: Unauthenticated state is distinct and truthful.
- AC-16: Forbidden/boundary state is distinct and truthful.
- AC-17: Task81A P2-01 typed-domain-item requirement is explicitly disposed.
- AC-18: Task81A P2-02 explicit state/error strategy is explicitly disposed.
- AC-19: Parent-not-found state is represented truthfully.
- AC-20: Invalid-request state is represented truthfully.
- AC-21: Recoverable-error state is represented truthfully.
- AC-22: Stale-session state is represented or safely prevented by guards.
- AC-23: Focus behavior after state transitions is keyboard-safe and evidenced.
- AC-24: Course selection clears stale lessons before loading the new course.
- AC-25: Session-generation changes prevent late responses from mutating state.
- AC-26: Lesson AbortController/current-selection guards prevent late mutation.
- AC-27: Course identifiers are UUID-like validated before URL construction.
- AC-28: Selected course identifiers are validated before lesson requests.
- AC-29: No learner progress or fabricated metrics are exposed.
- AC-30: Course markup uses semantic native buttons.
- AC-31: Course selection exposes `aria-pressed` semantics.
- AC-32: RTL/Persian direction and live-region semantics are preserved.
- AC-33: Frontend typecheck evidence is present for the exact reviewed HEAD.
- AC-34: Frontend lint evidence is present for the exact reviewed HEAD.
- AC-35: Production build evidence is present for the exact reviewed HEAD.
- AC-36: Diff integrity and `git diff --check` are independently evidenced.
- AC-37: Exact-head CI completed successfully with readable job/step evidence.
- AC-38: Exact-head Compose smoke/restore completed successfully with readable
  configuration, RLS, backup/restore, evidence, and cleanup steps.
- AC-39: The implementation scope is exactly the authorized seven frontend
  files; backend, migrations, OpenAPI, and unrelated files are unchanged.
- AC-40: Fresh Qwen review is for the exact HEAD and is PASS with zero P0/P1
  blockers and the required final marker.
- AC-41: Claude reviews the exact implementation HEAD, not the evidence branch
  HEAD, and verifies evidence completeness before verdict.
- AC-42: PR identity and base/head provenance are exact (`#42`, authoritative
  base, and HEAD `e98d1c575903f7b5657a20c004ea2802189e4394`).
- AC-43: No Ready, merge, release, deployment, Production action, or protected
  `codesho` promotion occurs before valid independent Claude PASS and Commander
  disposition.

## Current evidence pointers

AC-01..AC-11, AC-13..AC-16, AC-19..AC-22, AC-24..AC-32 are primarily assessed
by the seven implementation files and the prior Claude V5 result. AC-12,
AC-17..AC-18, and AC-33..AC-38 require the authority/evidence files in this
packet. AC-39..AC-43 are provenance and governance gates. No PASS is inferred.
