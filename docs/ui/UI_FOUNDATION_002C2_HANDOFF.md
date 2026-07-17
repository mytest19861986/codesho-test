# UI-FOUNDATION-002C2 Public Shell Foundation

## Scope and outcome

Generic prop-driven `PublicShell`, `PublicHeader`, `PublicFooter`, and
`PublicNavigationDrawer` are implemented. No real Homepage/Courses page,
asset, package, Application Shell, backend, or protected-repository change is
included. The temporary preview route was deleted before this checkpoint.

## Review evidence

| Gate | Score/result | Completion marker |
| --- | --- | --- |
| Desktop Gemini 01A | 100, PASS | `GEMINI_UI_FOUNDATION_002C2_DESKTOP_PUBLIC_SHELL_REVIEW_01A_COMPLETED` |
| Tablet Gemini 01 | 98, PASS | `GEMINI_UI_FOUNDATION_002C2_TABLET_PUBLIC_SHELL_REVIEW_01_COMPLETED` |
| Mobile Gemini 01 | 94, PASS | `GEMINI_UI_FOUNDATION_002C2_MOBILE_PUBLIC_SHELL_REVIEW_01_COMPLETED` |
| Claude drawer review | PASS, no P0 | `CLAUDE_UI_FOUNDATION_002C2_DRAWER_REVIEW_01_COMPLETED` |

Employer UI rules are confirmed: all text, links, icons, CTA and brand are
typed caller content; no raw component colors or screenshot-derived assets;
and no real page or Application Shell was changed.

## Drawer cross-boundary evidence

At 1024px runtime, the trigger reported
`aria-controls="codesho-public-navigation-drawer"` and
`aria-expanded="false"` while the drawer was absent. After activation it
reported the same `aria-controls`, `aria-expanded="true"`, and the matching
element existed with `role="dialog"`.

## Dispositions and known gaps

Claude's visibility-query and initial-focus suggestions were rejected with
current-component invariants. Dialog-local Escape and idempotent cleanup were
accepted. Background inertness and body-scroll locking are deferred known
gaps. Gemini's mobile Legal alignment is non-blocking P2. All three must be
resolved or explicitly re-reviewed in the first real public-page task before
Production.
