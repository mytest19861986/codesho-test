# UI-HOME-002D1 Alpha Homepage Cutover Handoff

Status: Commander static review complete; commit, push, and exact-SHA remote
verification are authorized. Protected-repository promotion remains forbidden.

## Delivered change

- `/` now composes the approved typed `HomepageFrame`.
- Title, description, OpenGraph title, and OpenGraph description derive from
  typed Alpha content. No canonical URL or OpenGraph image is emitted.
- The public shell uses typed Persian accessibility labels. With no available
  navigation items it renders no navigation, menu trigger, drawer, or links;
  the brand stays at the visual-left container boundary.
- The public homepage is no longer a legacy UI-policy exemption. It is scanned
  by the active raw-color, JSX-copy, and import policy checks.

## Commander review trail and authorized scope expansions

- `COMMANDER_UI_HOME_002D1_PAGE_STATIC_REVIEW_01_DISPOSITION`: authorized
  typed metadata, typed shell labels, and the initial page baseline update.
- `..._DISPOSITION_B`: required the page baseline exemption to be removed and
  authorized `PublicHeader.tsx` to suppress empty navigation controls.
- `COMMANDER_SCOPE_EXPANSION_UI_HOME_002D1_POLICY_GATE_V1`: authorized the
  minimal policy checker and its existing test file so `page.tsx` is actively
  scanned rather than hash-exempted.
- `..._DISPOSITION_C`: authorized the conditional `PublicHeader` class and
  `public-shell.module.css` logical margin that preserves visual-left brand
  placement without an empty placeholder.
- `COMMANDER_UI_HOME_002D1_PAGE_STATIC_REVIEW_01_COMPLETED`: PASS; no
  unresolved P0, P1, or P2. Commander substituted its static review for the
  Claude gate and passed the reviewed-component-equivalence visual gate.

## Local evidence

- `npm run test:ui-policy`: 10/10 tests passed. The added checks prove that
  `page.tsx` needs no baseline entry and that an injected page raw-color
  violation is rejected.
- `npm run check:ui-policy`, `npm run typecheck`, `npm run lint`, `npm run
  build`, and `git diff --check` passed.
- Production runtime checks at 1440, 1024, and 390 pixels showed no anchors,
  menu trigger, drawer/dialog, or horizontal overflow. The brand aligned at
  the left container boundary: x=80, 32, and 24 respectively.
- The non-empty navigation fixture preserves one trigger with the existing
  `aria-controls` and closed `aria-expanded` semantics.
- The approved hero PNG remains byte-identical at SHA-256
  `87833FBDBFAAC930C268304A67B056D6E9592C421CB80C2DA98CD902E6F47B37`.

## Scope and rollback

Only the homepage composition, typed content/type definitions, PublicHeader
and its existing CSS module, UI-policy checker/tests/baseline, and UI handoff
documents are in this task. No CSS file beyond the authorized existing module,
asset, dependency, package, route, production data, or unavailable link was
introduced. No preview server or browser artifact is a tracked file.

Rollback is non-destructive: revert the final cutover commit as one unit,
restoring the legacy `/` composition and its previous policy treatment; rerun
the same frontend gates and remote workflows. Do not reset history, force-push,
or promote to the protected `codesho` repository.

## Remaining finalization

Commit with `feat(ui): activate approved alpha homepage`, push only to
`codesho-test/main`, and verify CI plus Compose smoke/restore on that exact
SHA before declaring completion.
