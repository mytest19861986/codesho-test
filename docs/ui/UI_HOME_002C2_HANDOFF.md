# UI-HOME-002C2-PATHS-TRUST handoff

## Scope

- Adds the employer-approved, typed `learningPathsHeading` value and the three existing typed Learning Paths to the reusable `HomepageFrame` only.
- Each card reads its title and description from typed content. Hidden destinations do not render links.
- `TrustStrip` fails closed: unverified data renders no visible DOM, heading, statistics, or spacing.
- Production `/` is unchanged. The temporary `/paths-preview` route is pending deletion before any commit.

## Independent verification

- Local policy test and policy gate passed.
- ESLint, TypeScript typecheck, and production build passed after the implementation update.
- Runtime preview evidence at 1440, 1024, and 390 confirms three cards, zero card links, the exact typed heading, no TrustStrip node, and no horizontal overflow. Captures and raw evidence are retained outside the repository at `H:\codesho\ui-home-002c2-working`.
- Raw color/gradient scan of the feature files returned no matches; all card styling uses existing semantic tokens.
- `CLAUDE_UI_HOME_002C2_PATHS_REVIEW_01_V1_COMPLETED`: no blocking or major finding.
- `CLAUDE_UI_HOME_002C2_TRUST_REVIEW_02_V1_COMPLETED`: no blocking or major finding.

## Visual-review gate

- Commander disposition `COMMANDER_DISPOSITION_UI_HOME_002C2_GEMINI_OUTAGE_V1` classifies Gemini as temporarily unavailable and fidelity as unproven, not failed.
- The first revised Desktop submission exhausted configured providers with 429/503. A temporary external 2.5-flash guide also exhausted providers with 404 and did not change the runner or repository.
- Per Commander direction: no Tablet/Mobile submission, commit, or push until the required single post-recovery Desktop retry passes or Commander authorizes an independent bounded fallback.

## Final visual disposition

- `GEMINI_UI_HOME_002C2_DESKTOP_PATHS_REVIEW_01A_V1_COMPLETED`: score 100, no findings.
- `GEMINI_UI_HOME_002C2_TABLET_PATHS_REVIEW_01_V1_COMPLETED`: score 96, no findings after the 1024px two-column breakpoint correction.
- Gemini Mobile providers became unavailable after the accepted Desktop and Tablet gates. Commander performed the authorized bounded fallback review.
- `COMMANDER_UI_HOME_002C2_MOBILE_VISUAL_REVIEW_01_COMPLETED`: score 94, PASS, no blocking or major finding. The recorded card-height and trailing-spacing observations are non-blocking polish only.
- Commander confirmed that all visual gates are satisfied and authorized final scoped commit/push and exact-SHA CI/Compose verification.
