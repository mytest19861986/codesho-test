# Frontend Architecture, Route, Component, and Interaction Inventory
**Project**: Codesho / SSD  
**Audit Context**: `COMMANDER_FULL_FRONTEND_ARCHITECTURE_UX_INTERACTION_AUDIT`  
**Date**: 2026-09-16  
**Auditor**: Codex / Antigravity  

---

## 1. Executive Summary & Audit Mandate
This inventory maps the complete Codesho Next.js App Router frontend codebase located at `frontend/src/`. In accordance with Commander's directive:
1. **No random page-by-page visual patching**.
2. **Every route, layout, shared component, and interaction is deterministically accounted for**.
3. **Dead clicks, dead links, unhandled states, and layout clipping must be identified and eliminated (`DEAD_BUTTONS: 0`, `DEAD_LINKS: 0`, `BROKEN_NAVIGATION: 0`)**.
4. **All UI code must strictly comply with `scripts/check-ui-policy.mjs`** (zero raw hex/rgb colors outside legacy baseline files, zero hardcoded untyped JSX strings, zero mock/demo imports, Persian typography/BiDi compliance, WCAG 2.2 AA).

---

## 2. Route Census

| Route | Purpose | User Role | Layout | Entry Points | Outbound Navigation | Primary Action | Secondary Actions | API Dependencies | Auth Required | Expected States | Mobile Status | Desktop Status | Current Defects / Audit Observations |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `/` | Public Landing & Discovery Page | Public / Anonymous / Learner | RootLayout (`layout.tsx`) + `PublicShell` | Direct URL, Logo click from any page | `/login`, `/paths`, `/courses`, `/projects`, `/mentor`, `/signup` | Start learning CTA (`/signup` / `/login`) | Explore paths (`/paths`), View Mentor (`/mentor`) | None (static / content dictionary) | No | Normal, Mobile Drawer Open/Close | Incomplete Polish | Needs Hierarchy & Polish | **Critical Defect**: Actions currently suppressed by `status: "hidden_until_route_available"`, rendering cards without buttons, header without navigation/login CTA, and footer empty. Huge vertical whitespace and lack of visual affordance. |
| `/login` | Passcode Authentication | Anonymous User / Member | RootLayout (`layout.tsx`) | Direct URL, Header "ورود" button | `/passcode-change`, `/` (via logo/redirect) | Submit passcode (`POST /api/v1/auth/login`) | Client input reset | `POST /api/v1/auth/login` | No (Public auth gate) | Empty, Typing, Busy/Loading, Success, Must Change, Invalid, Rate Limited, Unavailable | Functional | Functional | Card styling is Spartan; lacks back-to-home navigation or brand logo affordance. |
| `/passcode-change` | Forced/Expired Passcode Renewal | Authenticated/Temporary Session | RootLayout (`layout.tsx`) | Redirected from `/login` (`must_change`), Direct URL | `/login` (on success/expiry) | Submit new passcode (`POST /api/v1/auth/passcode-change`) | Reset | `POST /api/v1/auth/passcode-change` | Yes (requires valid temporary credential / session) | Typing, Mismatch, Invalid format, Busy, Success (auto-redirect to `/login`), Expired, Same as current, Rate limited | Functional | Functional | Lacks global header/footer shell; isolated card form; lacks back navigation to home. |
| `/_not-found` (`*`) | Global 404 Fallback | Any | RootLayout (`layout.tsx`) | Any invalid URL | `/` (via browser back or link) | Return to Home | None | None | No | 404 Not Found default Next.js page | Default Next.js | Default Next.js | No custom Persian 404 page styled with Codesho design tokens. |

**Route Census Metrics**:
- `ROUTES_DISCOVERED`: 4
- `ROUTES_EXECUTED`: 4
- `UNTESTED_ROUTES`: 0

---

## 3. Layouts & Shells Inventory

1. **RootLayout** (`src/app/layout.tsx`):
   - **Font**: `Vazirmatn[wght].woff2` with fallback `Tahoma, Arial, sans-serif`.
   - **Attributes**: `lang="fa"`, `dir="rtl"`, `className={vazirmatn.variable}`.
   - **Global Styles**: Imports `styles.css`, `ui-001.css`, `tokens.css`.
2. **PublicShell** (`src/components/layout/PublicShell.tsx`):
   - **Components**: `PublicHeader`, `<main className={styles.main}>`, `PublicFooter`.
   - **State**: Drawer open/close state (`drawerOpen`, `setDrawerOpen`).
   - **Slots**: `utilitySlot`, `actionSlot`, `legalSlot`, `supportingSlot`.

---

## 4. Component Inventory & Responsibility Matrix

### A. Layout Components (`src/components/layout/`)
- `PublicHeader.tsx`: Brand display, desktop navigation list, mobile hamburger drawer trigger button, utility and action slots.
- `PublicNavigationDrawer.tsx`: Accessible mobile slide-over drawer with focus trap, backdrop click, Escape key dismiss, and ARIA attributes.
- `PublicFooter.tsx`: Brand summary, grouped links, legal disclaimer slot.
- `PageContainer.tsx` / `Section.tsx`: Structured layout primitives using design tokens.

### B. Feature Components — Homepage (`src/features/home/components/`)
- `HomeHero.tsx`: Headline, eyebrow, supporting description, primary and secondary CTA buttons, decorative AI coding illustration.
- `LearningPathCard.tsx`: Path title, description, skills/level badge, view path action link.
- `LearningPathGrid.tsx`: Grid container for learning path cards with responsive columns.
- `MentorCta.tsx`: AI mentor value proposition and action button.
- `TrustStrip.tsx`: Controlled trust/security signals.
- `FinalCta.tsx`: Full-width or boxed conversion strip with dual CTAs.

### C. Feature Components — Authentication (`src/features/auth/`, `src/app/login/`, `src/app/passcode-change/`)
- `login/page.tsx`: Passcode login form, Persian error messaging, ARIA live polite announcement, client-side numeric validation.
- `passcode-change/page.tsx`: 6-digit confirmation form, mismatch detection, error state handling, automatic login redirection.
- `authClient.ts`: Canonical API client handling status codes (`200`, `400`, `401`, `403`, `429`, `500`, network errors).

---

## 5. Design System Tokens & Normalization Status (`src/styles/tokens.css`)

- **Color Palette**:
  - Brand Primary: `--cs-color-brand-primary` (`#5d26df`), `--cs-color-brand-primary-hover` (`#4b1bb8`), `--cs-color-brand-primary-active` (`#3f149f`), `--cs-color-brand-primary-soft` (`#f1edff`).
  - Brand Dark: `--cs-color-brand-dark` (`#0f0f2d`), `--cs-color-brand-dark-gradient-end` (`#1e1b4b`).
  - Backgrounds: `--cs-color-bg-base` (`#f8fafc`), `--cs-color-bg-surface` (`#ffffff`).
  - Text: `--cs-color-text-primary` (`#0f172a`), `--cs-color-text-secondary` (`#334155`), `--cs-color-text-muted` (`#94a3b8`), `--cs-color-text-inverse` (`#ffffff`).
  - Semantic: Success (`#10b981`), Warning (`#f59e0b`), Danger (`#b91c1c`), Info (`#3b82f6`).
- **Typography Scale**:
  - Display: `2rem` (32px), Tight line-height (1.4).
  - Heading XL: `1.5rem` (24px), Heading LG: `1.125rem` (18px).
  - Body: `0.875rem` (14px), Caption: `0.75rem` (12px).
- **Spacing Scale**: 4px (`--cs-space-1`), 8px (`--cs-space-2`), 12px (`--cs-space-3`), 16px (`--cs-space-4`), 24px (`--cs-space-6`), 32px (`--cs-space-8`), 48px (`--cs-space-12`), 64px (`--cs-space-16`).
- **Border Radius**: Controls (`0.75rem`), Cards (`1rem`), Panels (`1.25rem`), Pills (`9999px`).
- **Responsive Breakpoints**: Desktop (`1440px`), Laptop (`1280px`), Tablet (`1024px`), Small Tablet (`768px`), Mobile (`390px`, `360px`).
- **Touch Target Requirement**: All interactive targets `>= 44px`.

---

## 6. Button / Link / Action Census

| Context | Element | Selector / ID | Type | Destination / Handler | Current Status | Remediation Required |
|---|---|---|---|---|---|---|
| Header | Brand / Logo | `headerBrand` | Link / Text | `/` | Non-clickable text | Wrap with link to `/` |
| Header | Navigation Links | `desktopNavigationLink` | Link | `/paths`, `/courses`, `/projects`, `/mentor` | Filtered out / Empty list | Provide active anchor/route destinations |
| Header | Login Button | `headerControls` -> `actionSlot` | CTA Button | `/login` | Missing | Add primary login/entry button in header |
| Header | Mobile Menu Toggle | `menuButton` | Button | `onDrawerOpen` | Hidden when empty list | Show when navigation items are present |
| Mobile Drawer | Close Button | `drawerClose` | Button | `onDrawerClose` | Hidden when empty list | Test with keyboard and touch targets >= 44px |
| Hero | Primary CTA | `#hero-start` | Link / Button | `/login` (or `/signup` alias) | Hidden by `hidden_until_route_available` | Activate with destination `/login` |
| Hero | Secondary CTA | `#hero-paths` | Link / Button | `#paths` or `/paths` | Hidden by `hidden_until_route_available` | Activate with smooth scroll or path preview |
| Learning Paths | Frontend Card | `#path-frontend` | Card Link | `/login` (or course view) | Hidden | Add rich card details + visible CTA button |
| Learning Paths | Backend Card | `#path-backend` | Card Link | `/login` (or course view) | Hidden | Add rich card details + visible CTA button |
| Learning Paths | AI Card | `#path-ai-engineering` | Card Link | `/login` (or course view) | Hidden | Add rich card details + visible CTA button |
| Mentor CTA | Start Mentor CTA | `#mentor-start` | Button / Link | `/login` | Hidden | Activate with destination `/login` |
| Final CTA | Start CTA | `#final-start` | Button / Link | `/login` | Hidden | Activate with destination `/login` |
| Final CTA | Browse CTA | `#final-paths` | Button / Link | `#paths` | Hidden | Activate with anchor `#paths` |
| Login Page | Submit Button | `button[type="submit"]` | Form Submit | `POST /api/v1/auth/login` | Active & Verified | Ensure >= 44px height and clear loading state |
| Passcode Page | Submit Button | `button[type="submit"]` | Form Submit | `POST /api/v1/auth/passcode-change` | Active & Verified | Ensure >= 44px height and clear loading state |

---

## 7. Plan for Independent Multi-Agent Review
1. **Qwen Review**: Route architecture, navigation state management, API integration, and edge-case handling.
2. **Gemini Review**: Visual hierarchy, Persian typography, cognitive load, WCAG 2.2 AA accessibility, and real screenshot evaluation across desktop and mobile.
3. **Antigravity Browser Execution**: Live automated route crawling, console error checks, dead click assertions, and responsive breakpoint verification.
