# UI-HOME-002C1-HERO handoff

## Scope and production boundary

- Implemented the typed, reusable `HomeHero` and `HomepageFrame` only; the production `/` route and legacy homepage remain untouched.
- The Hero reads its Persian content and image dimensions/path exclusively from `HomepageAlphaContent`.
- The employer-approved `hero-ai-coding-alpha.png` is rendered without any resize, conversion, optimization, or re-encoding.
- CTA links render only when their typed destination is available; no route or marketing copy was invented.
- The temporary `/hero-preview` fixture used for visual and behavior verification was deleted before commit.

## PublicShell fixes

- `PublicNavigationDrawer` now portals its dialog layer to `document.body`, isolates pre-existing body siblings with inert and `aria-hidden` while open, locks both document and body scroll, and restores every original value on close or unmount.
- Escape, focus trapping, initial close-button focus, and trigger-focus restoration were retained and browser-verified.
- Mobile legal content uses RTL logical alignment (`text-align: start` and mobile `justify-content: flex-start`) without adding footer text or routes.

## Verification

- Browser evidence at 1440, 1024, and 390 pixels: no horizontal overflow.
- Runtime computed typography for Hero title and description: Vazirmatn stack.
- Browser Drawer evidence: open state locks `body` and `documentElement`, isolates background, and focuses the close control; Escape restores scroll, isolation, and trigger focus.
- Browser Mobile Legal fixture evidence: parent computed `justify-content: flex-start`.

## Independent reviews

- `GEMINI_UI_HOME_002C1_DESKTOP_HERO_REVIEW_01A_V1_COMPLETED`: score 92, no blocking or major findings.
- `GEMINI_UI_HOME_002C1_TABLET_HERO_REVIEW_01_V1_COMPLETED`: score 95, no blocking or major findings.
- `GEMINI_UI_HOME_002C1_MOBILE_HERO_REVIEW_01_V1_COMPLETED`: score 100, no findings.
- `CLAUDE_UI_HOME_002C1_HERO_REVIEW_01_V1_COMPLETED`: no blocking or major findings.
- `CLAUDE_UI_HOME_002C1_DRAWER_REVIEW_02_V1_COMPLETED`: no blocking or major findings.
- Exact prompts, captures, provider logs, and raw responses are retained outside the repository under `H:\codesho\ui-home-002c1-working`.

## Commander disposition

`COMMANDER_DISPOSITION_UI_HOME_002C1_DESKTOP_REVIEW_01_V1` clarified that Footer completeness and source-illustration identity are outside this slice; desktop/tablet geometry, Vazirmatn runtime evidence, and Hero whitespace were remediated before the passing revised Desktop review.
