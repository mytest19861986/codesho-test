# UI-FOUNDATION-002C1 responsive application shell

Status: visual review passed; checkpoint pending CI and Compose smoke/restore.

## Scope and committed files

This task delivers a generic, prop/slot-driven application shell only. It has
no page, business logic, API, dashboard data, notifications, profile data,
marketing copy, metrics, or licensed assets. Final source is limited to
`frontend/src/styles/tokens.css` and `frontend/src/components/layout/`.

The temporary `frontend/src/app/shell-preview/` route used for captures and
reviews was deleted before the checkpoint commit. Screenshots, exact prompts,
and raw Gemini replies remain outside the repository at
`H:\codesho\ui-foundation-002c1-working`.

## Shell contract

- All brands, labels, icons, navigation items, badges, content, profile and
  header/sidebar regions are caller-provided `ReactNode` props or slots.
- Desktop (`>=1280px`) keeps a 260px sidebar on the visual left through
  RTL-safe logical grid placement. The main region occupies the visual right.
  The desktop brand is sidebar-only. `headerPrimarySlot` is visual-left beside
  the sidebar; actions and profile are visual-right without a visual-only
  keyboard-order reordering.
- Tablet (`768px-1279px`) hides the sidebar, uses a 64px header and a fixed
  72px bottom navigation plus safe-area padding.
- Mobile (`<768px`) uses a 56px header, 64px fixed bottom navigation plus
  safe-area padding, and a single-column content region with 16px outer
  spacing.
- Teacher active navigation uses semantic teal
  `--cs-color-nav-teacher-active-bg` (`#0E7490`) with
  `--cs-color-text-inverse` (`#FFFFFF`): runtime contrast is approximately
  5.36:1. Learner and admin retain semantic violet states.

## Accessibility and interaction evidence

- Navigation rows, menu trigger, action slot and profile slot are at least
  44 by 44 CSS pixels.
- Focus-visible uses the token-based `--cs-focus-ring`; runtime evidence shows
  a 3px ring on the focused active navigation control.
- `NavigationDrawer` provides `aria-expanded`, `aria-controls`, a modal
  navigation region, Escape close, overlay close, focus containment and focus
  restoration to its trigger.
- Captured runtime evidence: Desktop `scrollWidth=1409 < innerWidth=1424`;
  Mobile `scrollWidth=390`, `bodyScrollWidth=390`, 56px header and 65px
  rendered bottom navigation including its border. Tablet has no sidebar,
  64px header and 73px rendered bottom navigation including its border.

## Sequential Gemini visual reviews

| Viewport | Prompt / marker | Score | Result |
|---|---|---:|---|
| Desktop | `GEMINI_UI_FOUNDATION_002C1_DESKTOP_SHELL_REVIEW_01D_V1` / `GEMINI_UI_FOUNDATION_002C1_DESKTOP_SHELL_REVIEW_01D_COMPLETED` | 92 | PASS |
| Tablet | `GEMINI_UI_FOUNDATION_002C1_TABLET_SHELL_REVIEW_01_V1` / `GEMINI_UI_FOUNDATION_002C1_TABLET_SHELL_REVIEW_01_COMPLETED` | 98 | PASS |
| Mobile | `GEMINI_UI_FOUNDATION_002C1_MOBILE_SHELL_REVIEW_01_V1` / `GEMINI_UI_FOUNDATION_002C1_MOBILE_SHELL_REVIEW_01_COMPLETED` | 100 | PASS |

No final review has an unresolved BLOCKING or MAJOR finding.

## Finding dispositions

- Teacher teal active navigation: accepted by Commander as a role accent;
  runtime verifies white foreground and `#0E7490` background.
- Desktop sidebar position: Commander accepted visual-left placement; it is
  implemented with logical grid columns, not physical left/right properties.
- Focus and hit-target observations: rejected with runtime/CSS evidence of a
  3px token focus ring and 44px minimum slot containers.
- Scrollbar observations: rejected with evidence that `overflow-y: auto` is
  used and vertical document scroll comes from intentional preview structure,
  not forced scrollbars or horizontal overflow.

## Employer UI gates

The implementation passes all three blocking policy rules:

- `NO_RAW_COLORS_IN_COMPONENTS`
- `NO_MARKETING_COPY_IN_JSX`
- `NO_FAKE_PRODUCTION_METRICS`

No package manifest changed, no coordination-stage files are part of this
checkpoint, no production page was added, and no protected-repository
promotion was attempted.
