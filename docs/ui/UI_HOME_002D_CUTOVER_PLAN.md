# UI-HOME-002D0 Cutover Readiness Plan

Status: analysis only; no cutover, route change, source edit, commit, push, or production promotion has been performed.

Base SHA: `dafaf5051da08511510d37bd1036469796f5cb59`

## Frozen current production homepage manifest

The current `/` route is `frontend/src/app/page.tsx`.  It is a legacy static
homepage and imports no local component or image module.  Its visible content
is implemented directly in that file and styled by the root layout's imports.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `frontend/src/app/page.tsx` | 8,095 | `380F4F5C7E5FF105ABAF6C421991160E122BB9E92138141C5E5F0E454D781AB8` |
| `frontend/src/app/styles.css` | 11,136 | `955AFDE37693F2521310D1B677E1CB8C50CB77BF505C8F968E6079270A50EF73` |
| `frontend/src/app/ui-001.css` | 976 | `E66ADDC2479820FC4A7C314CAC4F79BDC9317270D86BE45B8E8B5021C582910B` |
| `frontend/src/app/layout.tsx` | 764 | `CDEE669DC8C4A32D1DC8F1837DA44B65084ADC9973A5B0F43D6049C53FBDFE6A` |
| `frontend/src/app/fonts/Vazirmatn[wght].woff2` | 111,152 | `4E3FA217D38FDAFC1FEA4414CEB58CA5E662CF0AB5FA735A8C8C20E8B42CAD92` |

The three legacy UI files above are hash-pinned by
`frontend/scripts/check-ui-policy.mjs`.  A future cutover must deliberately
update that policy and its tests in the same reviewed change; it must not
delete the legacy files as an incidental cleanup.

Current legacy dependencies and behaviour:

- `layout.tsx` imports `styles.css`, `ui-001.css`, and shared `tokens.css`.
- The legacy page uses only in-page fragment links (`#top`, `#courses`,
  `#paths`, `#projects`, `#mentor`, `#footer`) plus `mailto:hello@codesho.ir`.
- Its visible sections are Hero, numeric statistics, benefits, Learning Paths,
  Projects, Mentor, and Footer.  It includes hard-coded, non-verified numbers.
- No legacy page-specific static image asset is imported; the local Vazirmatn
  font is the only root-layout binary dependency.

## Approved Alpha inventory and constraints

The approved Alpha implementation already exists but is not imported by `/`:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `frontend/src/features/home/HomepageFrame.tsx` | 939 | `C908B2AF97CF09F4F0C11EDAE62267F930BB60C001707F0759D39DC3F1D0EE18` |
| `frontend/src/content/fa/homepage.alpha.ts` | 3,920 | `1CF4F299B7F67514D830FF7E3AF07412729854B89B5BBDC4E932AF7B4585EF40` |
| `frontend/src/features/home/home.types.ts` | 3,637 | `996C2D1C0D450BEF2703951A1BD7A5A2B4A465BAB0EF61766B3A0E84BEE1C5D2` |
| `frontend/public/assets/home/hero-ai-coding-alpha.png` | 2,307,522 | `87833FBDBFAAC930C268304A67B056D6E9592C421CB80C2DA98CD902E6F47B37` |

The approved hero PNG is exactly `1448x1086`, 2,307,522 bytes, and has the
approved SHA-256 above.  It must be used byte-for-byte: no resize, conversion,
optimization, or re-encoding.  Its Alpha metadata is explicitly
`productionRights: pending_metadata_review`; that is a release gate, not a
claim of production clearance.

`HomepageFrame` renders `HomeHero`, `LearningPathGrid`, `TrustStrip`,
`MentorCta`, and `FinalCta` inside `PublicShell`.  `HomepageFrame` currently
requires all `PublicShellProps`; no page currently supplies those props.  A
future cutover therefore needs an explicit, reviewed presentation mapping for
the header/footer shell rather than inventing routes or rendering fake links.

## Visibility and CTA matrix

| Area | Alpha state at cutover readiness | Required production behaviour |
| --- | --- | --- |
| Hero | enabled | Render typed copy and approved decorative hero image; both actions remain absent until their destinations are marked `available`. |
| Learning Paths | enabled | Render the three typed cards; their actions remain absent because `/paths` is not available. |
| Mentor CTA | enabled | Render typed heading only; omit action because `/mentor` is not available. |
| Final CTA | enabled | Render typed heading only; omit both actions because `/signup` and `/paths` are not available. |
| Statistics / Trust Strip | `hidden_until_verified_data` | Do not render numbers, counters, or the strip. |
| Projects | `hidden_until_verified_data` | Do not render. |
| Courses | `hidden_until_verified_data` | Do not render. |
| Testimonials | `omitted_until_permissioned` | Do not render. |
| Footer | `hidden_until_route_available` | Do not render navigational/footer links until approved destinations and copy exist. |

All typed destinations (`/login`, `/signup`, `/paths`, `/courses`,
`/projects`, `/mentor`) are currently `hidden_until_route_available`.
No navigation item or CTA may render a live anchor before its status is changed
with Commander/employer-authorized route evidence.  This is a typed status on
`HomepageDestination`, not a production-route availability assertion.

## SEO, accessibility, and rendering assessment

Current root metadata only defines a title and description.  It has no
explicit `metadataBase`, canonical URL, OpenGraph metadata, Twitter metadata,
or robots policy in `layout.tsx`.  A cutover must not guess the public origin,
canonical URL, social image, or indexing policy; those are explicit release
inputs.

Alpha's semantic components use section/headings and the hero image has empty
alt text because it is marked decorative.  Primary risks to verify are:

- `PublicShell` is a client component; its drawer state must not be required
  to access the initial render or basic content.
- Header/footer props are absent from the Alpha content model, so any shell
  mapping must preserve keyboard navigation, drawer labels, focus handling,
  and no-JavaScript reading order without fabricated destinations.
- Confirm RTL direction, heading order, image sizing/CLS, and that no hidden
  action leaves an empty focus target.
- Validate the initial server-rendered page and a JavaScript-disabled/basic
  render manually in addition to automated checks.

## Required regression matrix

| Viewport | Required evidence before cutover approval |
| --- | --- |
| 1440px desktop | Header/shell geometry, Hero image and text balance, three Learning Path cards, Mentor and Final CTA headings, and absent hidden sections/actions. |
| 1024px tablet | No horizontal overflow, stable Hero media sizing, readable card grid, and keyboard-operable responsive navigation with no unavailable link exposed. |
| 390px mobile | RTL reading order, menu/drawer focus and close behaviour, no clipped image/text, one-column readable content, and absent hidden sections/actions. |

For all three viewports, capture the rendered `/` result after the approved
cutover candidate is built; compare it with the approved Alpha review evidence
and record any intentional responsive variance.  This plan contains no visual
approval by itself.

## Content and token controls

The Alpha components use their scoped CSS modules and the shared token layer;
the future change must retain token-only color usage and pass the UI-policy
check.  All copy rendered by the Alpha frame comes from the typed
`HomepageAlphaContent` model.  This plan authorizes neither new external copy
nor invented production data: non-verified numerical claims and unpermissioned
testimonials remain hidden, and the mentor description remains unrendered
while its transcription is pending.

## Controlled future cutover procedure

1. Obtain the employer's explicit A/B decision, production-rights clearance
   for the approved hero asset, public-origin/canonical/robots decisions, and
   approved shell/route data.  Do not infer any of them.
2. Re-check this base SHA and re-hash the full manifest above.  If any frozen
   file changed, stop and refresh this plan before editing.
3. Create a dedicated approved cutover branch from the approved base.  Keep
   legacy source present until the replacement has passed CI and review.
4. In the smallest Commander-approved change, replace the `/` page composition
   with `HomepageFrame` plus a typed, unavailable-route-safe `PublicShell`
   mapping; add only employer-approved metadata.  Update the UI policy hashes
   and tests intentionally as part of that same change.
5. Do not change the approved PNG bytes.  Do not enable statistics, projects,
   courses, testimonials, or unavailable CTAs.
6. Run `npm run lint`, `npm run typecheck`, `npm run test:ui-policy`,
   `npm run check:ui-policy`, `npm run build`, `git diff --check`, and the
   required CI workflow.  Inspect `/` at 1440px, 1024px, and 390px; test
   keyboard flow, responsive drawer, no-JS/basic render, and image layout.
7. Have Commander complete the required visual/release review and obtain the
   employer's separate protected-repository promotion approval before any
   promotion.

Likely future cutover commit scope, subject to the missing employer inputs:

- `frontend/src/app/page.tsx` — replace the legacy composition.
- `frontend/src/app/layout.tsx` — only if employer-approved metadata is ready.
- `frontend/scripts/check-ui-policy.mjs` and
  `frontend/scripts/check-ui-policy.test.mjs` — update the deliberate legacy
  hash policy for the changed page.
- A new, explicitly approved typed shell-content mapping file, if the existing
  Alpha content is not extended in a reviewed decision.
- `frontend/src/content/fa/homepage.alpha.ts` only for approved route,
  footer, or production-rights metadata; never to fabricate data.

Existing Alpha components, their CSS modules, `tokens.css`, and the approved
PNG should remain unchanged unless a separately reviewed defect requires it.
No package or lockfile change is expected.

## Reversible rollback

Before deployment, retain the exact pre-cutover commit and the frozen hashes.
If a regression appears, create a new rollback commit that restores the prior
`page.tsx` composition and its matching UI-policy expected hash; do not use
destructive reset, force push, or deletion of history.  Re-run the same checks
and CI, then deploy only under the authorized release process.  Preserve the
Alpha files and evidence for diagnosis.

## Required decision and stop condition

Commander must ask the employer once to choose:

- A: controlled Alpha cutover with the rollback procedure above.
- B: retain/defer the current homepage.

After ten minutes without an answer, issue one reminder.  If still unanswered,
park the cutover and perform only independently authorized work.  This plan
makes no employer decision and authorizes no production promotion.

## D1 remediation checkpoint (2026-07-17)

Commander accepted employer option A and authorized `UI-HOME-002D1-ALPHA-CUTOVER`.
The static-review disposition accepted the route cutover and required only two
P1 remediations before its completion marker:

- `page.tsx` now derives title, description, OpenGraph title, and OpenGraph
  description from typed Alpha content.  It adds neither a canonical URL nor
  an OpenGraph image.
- The typed Alpha content now supplies meaningful Persian menu, drawer-close,
  and navigation accessibility labels; `page.tsx` consumes those values.

Current D1-owned changes are limited to:

- `frontend/src/app/page.tsx`
- `frontend/src/features/home/home.types.ts`
- `frontend/src/content/fa/homepage.alpha.ts`
- `frontend/ui-policy-baseline.json` (only the authorized hash entry for
  `src/app/page.tsx`)
- this authorized readiness/checkpoint document

No layout, CSS, token, asset, dependency, route, or protected-repository
change was made.  The approved hero asset remains byte-identical:
`87833FBDBFAAC930C268304A67B056D6E9592C421CB80C2DA98CD902E6F47B37`.

Remediation verification so far passed: `npm run typecheck`, `npm run lint`,
`npm run test:ui-policy` (8/8), `npm run check:ui-policy`, and
`git diff --check`.

The subsequent `npm run build` was blocked locally with
`EBUSY: resource busy or locked, rmdir '...\\frontend\\.next\\standalone'`.
The lock is attributable to a temporary local standalone server used only for
SSR inspection.  Before resuming, safely stop only that known temporary server
process (after identifying its PID), rerun the production build and fresh SSR
metadata assertions, then send the Commander remediation packet.  Do not
commit or push until Commander returns
`COMMANDER_UI_HOME_002D1_PAGE_STATIC_REVIEW_01_COMPLETED`.
