# UI-FOUNDATION-002A — Reference Audit & Specification

Status: `UI-FOUNDATION-002A-R`; specification approved pending this document fix  
Owner: Codex  
Task: `UI-FOUNDATION-002A`  
Reference root: `H:\codesho\UI\ui new\desktop+mobile+tablet`  
Repository: `codesho-test` at `667fd9721c1a5abd712c77ddb5e87772690649e4`

This document is a design-system audit and implementation specification only.
It does not authorize changes in `frontend/`, backend changes, production
assets, page implementation, commit, push, or promotion.

## 1. Reference manifest and integrity

SHA-256 was calculated on 2026-07-17 with PowerShell `Get-FileHash -Algorithm
SHA256`. The eight files are the complete reference set; they are not copied
into this repository.

| Reference | SHA-256 |
|---|---|
| `dashboard.png` | `736F8B284DD2C82AF14A3A46BE4805C3BA30E4B11445565A015893496EC29F1B` |
| `dore.png` | `4BF778707E3DE9DF015821472699FF4EBF47D041C749E271EB89035FEFC52EDC` |
| `main.png` | `26A50363F6BDC48E7376CDA0F6ACEDF646BD5AEC5841D02CB1F0EE73792C0166` |
| `mentor.png` | `D6DC1C9215F98D6B2CAC5F217276EAA22711DAA8471BB0A961D8F3B9014CA4C9` |
| `panel admin.png` | `576CB3911C57C5D35446CF57211B0DFC4C0FDB46F7CDA975ED613B0D80865521` |
| `panel teacher.png` | `8B8052C2660373698DEADD25F003B5F402A61776F7958E35F6180AE1A4476BD7` |
| `project+tamrin.png` | `7293931FB698696EFAA94665E3FCAC132158610DAA5EF63180C74184B49DB32A` |
| `signup+onboard.png` | `B5946A0D6AD2088D4BB98CFF15F111775E10F7E0E879729741CC2D86E339271D` |

Gemini was asked to analyze one attachment per request, sequentially. Raw
prompts and responses are retained outside the repository at
`H:\codesho\ui-foundation-002a-working`.

| Reference analyzed | Prompt ID | Completion marker |
|---|---|---|
| `main.png` | `GEMINI_UI_FOUNDATION_002_PUBLIC_ANALYSIS_V1` | `GEMINI_UI_FOUNDATION_002_PUBLIC_ANALYSIS_COMPLETED` |
| `dashboard.png` | `GEMINI_UI_FOUNDATION_002_LEARNER_ANALYSIS_V1` | `GEMINI_UI_FOUNDATION_002_LEARNER_ANALYSIS_COMPLETED` |
| `panel teacher.png` | `GEMINI_UI_FOUNDATION_002_TEACHER_ANALYSIS_V1` | `GEMINI_UI_FOUNDATION_002_TEACHER_ANALYSIS_COMPLETED` |
| `panel admin.png` | `GEMINI_UI_FOUNDATION_002_ADMIN_ANALYSIS_V1` | `GEMINI_UI_FOUNDATION_002_ADMIN_ANALYSIS_COMPLETED` |

All eight references have a completed sequential Gemini audit. Page-level
implementation remains blocked until this fixed specification is accepted.

## 2. Shared foundation

The following is the common intersection of all eight completed analyses,
using the final decisions in Section 7.

### 2.1 Responsive shells and geometry

| Tier | Canvas used by references | Shell | Grid | Outer spacing |
|---|---|---|---|---|
| Desktop | >=1280px; fidelity capture 1440px | Persistent 260px sidebar where applicable; main content fluid | 12 columns; 16–24px gutters | 24–32px outer padding; 72px header |
| Tablet | 768–1279px | Sidebar hidden; hamburger and bottom navigation | 8 columns; 16px gutters | 16–24px padding; 64px header; 72px bottom bar |
| Mobile | <768px; compact sub-breakpoint <=480px | Single column; compact header and fixed bottom navigation | 4 columns or stacked | 12–16px padding; 56px header; 64px bottom bar plus safe area |

Desktop content must reserve the sidebar width. Tablet and mobile content must
reserve bottom-navigation safe-area space and must not horizontally overflow.
Use CSS logical properties and `dir="rtl"`; do not encode the shell with
physical left/right assumptions.

### 2.2 Candidate semantic tokens

The analyses agree on the semantic roles below. Final brand values are fixed
by Section 7; page-specific exceptions require a cited reference.

| Token | Candidate value | Use |
|---|---|---|
| `color-bg-base` | `#F8FAFC` | Application canvas |
| `color-bg-surface` | `#FFFFFF` | Cards, tables, inputs |
| `color-text-primary` | `#0F172A` | Headings and key values |
| `color-text-secondary` | `#475569` | Descriptions and metadata |
| `color-text-muted` | `#94A3B8` | Placeholder and non-essential support text |
| `color-border-subtle` | `#E2E8F0` | Card borders and dividers |
| `color-brand-primary` | `#5D26DF` | Primary action and active state |
| `color-brand-primary-hover` | `#4B1BB8` | Primary hover state |
| `color-brand-primary-active` | `#3F149F` | Pressed/active state |
| `color-brand-primary-soft` | `#F1EDFF` | Selected/soft brand surface |
| `color-brand-indigo` | `#4F46E5` | Secondary indigo accent |
| `color-brand-dark` | `#0F0F2D` | Teacher/Admin sidebar |
| `color-brand-dark-gradient-end` | `#1E1B4B` | Teacher/Admin sidebar gradient end |
| `color-accent-teal` | `#06B6D4` | Accent only; never primary action |
| `color-success` | `#10B981` | Completion/published state |
| `color-warning` | `#F59E0B` | Review/rating/in-progress state |
| `color-danger` | `#EF4444` | Destructive/error state |
| `color-info` | `#3B82F6` | Informational state |

Gradient usage is limited to hero/CTA and AI-assistant surfaces. The approved
dark shell gradient is `linear-gradient(135deg, #0F0F2D, #1E1B4B)`.
Raw color literals may appear only in the token layer; components must consume
semantic tokens. This is the `NO_HARDCODED_BRAND_COLORS` rule.

### 2.3 Typography

Use the approved self-hosted `Vazirmatn` family; do not add remote font
dependencies. Use a separate local Latin/code face only where it improves
numeric, technical, or code readability. The common
hierarchy is:

Font evidence: `frontend/src/app/fonts/Vazirmatn[wght].woff2`, SHA-256
`4E3FA217D38FDAFC1FEA4414CEB58CA5E662CF0AB5FA735A8C8C20E8B42CAD92`;
license record: `frontend/THIRD_PARTY_LICENSES_Vazirmatn.txt`, SHA-256
`E6F4CE7B6C830D5A25A4F8AC777C267CD7D3C180BC2A7150CA57CBB9B280C4B7`.

| Token | Weight | Desktop | Mobile | Line height |
|---|---:|---:|---:|---:|
| `font-display` | 700 | 32px | 22px | 1.4 |
| `font-heading-xl` | 700 | 20–24px | 18–20px | 1.4–1.5 |
| `font-heading-lg` | 600 | 16–18px | 15–16px | 1.4–1.5 |
| `font-body-md` | 400 | 14px | 13–14px | 1.5–1.6 |
| `font-caption` | 400–500 | 11–12px | 10–12px | 1.4–1.6 |
| `font-code` | 400 | 13px | 12–13px | 1.5 |

Mixed Persian/Latin strings must use isolated inline direction where required;
percentages, IDs, dates, and code remain readable LTR inside RTL containers.

### 2.4 Spacing, shape, and elevation

Use a 4px base scale with the shared practical steps `4, 8, 12, 16, 24,
32, 48, 64px`. Candidate shape tokens are `radius-sm: 6px`, `radius-md:
12px`, `radius-lg: 16px`, and `radius-pill: 9999px`. A 1px subtle border is
the default structural boundary. Candidate card elevation is a soft shadow,
approximately `0 4px 12px rgba(0,0,0,.03)`; stronger shadows belong only to
floating menus/dialogs. Mobile bottom sheets use a 24px top radius.

### 2.5 Interaction and accessibility contract

- Primary, outline, navigation, card, status-badge, dropdown, chart-tooltip,
  bottom-sheet, and destructive states must have explicit default, hover,
  active, focus, disabled, and error behavior where applicable.
- Keyboard focus must be visible and have at least a 2px high-contrast ring;
  menus close with Escape and preserve logical RTL tab order.
- Every interactive target is at least 44×44px, with 48px preferred on touch
  surfaces. Fixed bottom navigation must expose a safe-area inset.
- Text and essential status indicators target WCAG 4.5:1 contrast; color alone
  never communicates status. Charts need text/ARIA summaries.
- Destructive actions require confirmation or an undo path; error states must
  preserve input context and provide a Persian-readable message.

## 3. Shell and component inventory

### Public shell (`main.png`)

Desktop header/navigation, hero or CTA banner, course/feature cards, tags,
ratings, footer groups, brand mark, and licensed robot/code illustrations.
Mobile collapses navigation to a compact header and stacked content; public
footer groups become accordions or vertical sections.

### Learner shell (`dashboard.png`)

Desktop fixed sidebar, greeting and stats, active-course/promo banner, AI
mentor quick actions, project cards and menu, weekly progress chart and course
list. Tablet hides the sidebar and introduces hamburger navigation; mobile adds
five-item bottom navigation and stacks content.

### Teacher shell (`panel teacher.png`)

Desktop sidebar plus search/profile/notification header, metric cards, course
data grid, status badges, analytics charts, and AI-assistant promo. Tablet and
mobile collapse the grid/charts and move core navigation to hamburger/bottom
navigation; a teal-accent FAB is an optional page-specific pattern.

### Admin shell (`panel admin.png`)

Desktop sidebar and header, dashboard/data-grid widgets, status feedback,
modals and charts. Tablet hides the sidebar and uses a 72px bottom bar;
mobile uses a 64px bottom bar and bottom sheets. Table ordering is RTL with
primary subject at the right and actions at the left.

### Shared component inventory

`AppShell`, `Header`, `Sidebar`, `MobileBottomNav`, `HamburgerDrawer`,
`Button`, `IconButton`, `Input`, `Select`, `Card`, `Badge`, `StatusBadge`,
`Progress`, `MetricCard`, `DataGrid`, `Chart`, `Tooltip`, `DropdownMenu`,
`Modal`, `BottomSheet`, `Accordion`, `Avatar`, `Pagination`, `Toast`, and
`Footer`. Each component needs an RTL story/spec and keyboard/touch states
before implementation is approved.

## 4. Asset dependency register

The reference screenshots are audit inputs, not production assets. Original,
licensed files are required for: CodeSho logotype/mark, robot or mentor
illustrations, course/project banners, avatars, category/system icons, chart
illustrations, and any brand marks (Next.js, Python, OpenAI, etc.). Do not crop,
trace, extract, or ship screenshot pixels. Asset ownership, license, dimensions,
alt text, dark/light variants, and fallback must be recorded before use.

The four unreviewed reference images are blocking page-specific asset/layout
claims: `dore.png`, `mentor.png`, `project+tamrin.png`, and
`signup+onboard.png`.

## 5. Conflicts and decisions required

| Topic | Evidence conflict | Decision required |
|---|---|---|
| Primary brand | Public `#5011DF`; learner `#5E35B1`; teacher `#4F46E5`; admin `#5D5FEF` | Choose one canonical primary and permitted role-specific accents |
| Dark shell | Public gradient `#1E1B4B`; teacher `#130F30`; admin `#0F0F2D` | Choose canonical dark token and gradient stops |
| Canvas | Public white; learner/teacher `#F8FAFC`; admin `#F4F6FA` | Choose base canvas and whether public shell is an exception |
| Header | 56px mobile, 60px learner, 64px tablet, 72px desktop | Confirm exact shell heights and safe-area behavior |
| Breakpoint | Admin hides sidebar below 1280; other reviews only state tablet ranges | Confirm sidebar collapse breakpoint |
| Bottom nav | Learner 64px mobile; teacher/admin 72px tablet; admin 64px mobile | Confirm bar heights, item count, and FAB ownership |
| Shape | Cards range 12–24px; learner reports 20px desktop/16px mobile | Confirm canonical card radius by shell |
| Font | Reports suggest several Persian families | Final: self-hosted Vazirmatn with recorded license and hash |
| Unreviewed pages | Four references have no Gemini analysis marker | Run four additional sequential reviews before page implementation |

Until these decisions are recorded by Commander/employer, implementation must
not infer a token value outside the final token table.

## 6. Supplementary reference audits

The four remaining references were audited sequentially after Commander
authorized `UI-FOUNDATION-002A-R`. They are still analysis inputs only.

| Reference | Prompt ID | Completion marker |
|---|---|---|
| `dore.png` | `GEMINI_UI_FOUNDATION_002_COURSES_ANALYSIS_V1` | `GEMINI_UI_FOUNDATION_002_COURSES_ANALYSIS_COMPLETED` |
| `mentor.png` | `GEMINI_UI_FOUNDATION_002_MENTOR_ANALYSIS_V1` | `GEMINI_UI_FOUNDATION_002_MENTOR_ANALYSIS_COMPLETED` |
| `project+tamrin.png` | `GEMINI_UI_FOUNDATION_002_PROJECT_ANALYSIS_V1` | `GEMINI_UI_FOUNDATION_002_PROJECT_ANALYSIS_COMPLETED` |
| `signup+onboard.png` | `GEMINI_UI_FOUNDATION_002_AUTH_ONBOARD_ANALYSIS_V1` | `GEMINI_UI_FOUNDATION_002_AUTH_ONBOARD_ANALYSIS_COMPLETED` |

Raw prompts and responses are outside the repository at
`H:\codesho\ui-foundation-002a-working`.

### Courses (`dore.png`)

The shared rules reinforce a 12-column desktop shell, 2-column tablet course
grid, 1-column 390px mobile grid, 4/8/16/24/32/48px spacing, 16px structural
card radius, and local Persian typography. Page-specific elements are search,
category/level/price/sort filters, course cards, badges, pagination,
recommended-path carousel, and a newsletter/footer block. Mobile hides or
condenses filters and uses horizontal path scrolling.

Conflicts: the report gives a 1280px max container and 48–64px desktop outer
padding, while an earlier shared audit used 1200px/24px; it reports royal-indigo
variants `#4F46E5`/`#3F51B5`; and it deliberately places the English CodeSho mark
on the visual left in a hybrid RTL header. These require a shell-level decision,
not page-local overrides.

### Mentor (`mentor.png`)

The shared rules reinforce a 72px desktop header, 64px tablet header, 56px
mobile header, 12px mobile margins, 48px touch targets, local fonts, and an
RTL chat composer. Page-specific elements are a three-column desktop workspace
(chat history, conversation, context/resources), context drawers, message
bubbles, suggested prompts, code/result accordion, attachments and a send
composer. Tablet and mobile collapse side panels into drawers or a context
summary card.

Conflicts: the report proposes a 56px tablet/mobile bottom bar, while other
audits propose 64/72px; it places the CodeSho mark on the visual left; and it
observes a left-edge search icon in one history input while recommending a
right-edge RTL placement. These are recorded as component-level evidence and
the final shell rule remains RTL logical placement. No AI provider or runtime
behavior is inferred.

### Project and exercise (`project+tamrin.png`)

The shared rules reinforce white cards with approximately 12–16px radius,
purple primary/ghost actions, notification/profile controls, RTL headers, and
mobile bottom navigation. Page-specific elements are project breadcrumbs and
hero, completion/progress, status and category badges, tab bar, next-step
checklist, resources, feedback, submission, and a tablet FAB.

Conflicts: the reference uses a 1440px desktop, 1024–1439px tablet range and
360–767px mobile range rather than the final breakpoint; some
progress bars fill left-to-right despite RTL; the primary next chevron points
right; and tab sets differ by viewport (four desktop, five tablet, four mobile).
Tablet resources also lose text labels in favor of icons, which is an
accessibility regression and must not be reproduced without an accessible
labelled alternative.

### Authentication and onboarding (`signup+onboard.png`)

The shared form rules reinforce 48px controls, 12px input/button radius,
right-aligned Persian labels, visible focus/error states, local Persian fonts,
and a 4/8/12/16/24px spacing scale. Page-specific elements are selectable
goal/skill cards, five-step onboarding, progress/strength indicators, weekly
commitment controls, completion/mentor presentation, and form validation.

Conflicts: the report estimates primary `#5D26DF`, canvas `#F8F9FC`, and
text-secondary `#64748B`, which differ from the final tokens. It also
mentions social-login and Remember Me as reference content; those are visual
elements only and do not authorize backend authentication behavior. Persian
and Western digit handling must be decided with product/security owners; a
mobile five-step bar must collapse below 370px to avoid overflow.

## 7. Decision matrix — final Commander decisions

The following decisions are authoritative for the next implementation task.
They replace the earlier candidate values; components must use semantic tokens,
and raw brand literals are prohibited outside the token layer.

| Decision | Final decision | Evidence/exception |
|---|---|---|
| Primary brand | `#5D26DF`; hover `#4B1BB8`; active `#3F149F`; soft `#F1EDFF` | `#4F46E5` is the secondary `brand-indigo`; teal is accent only |
| Dark shell vs light canvas | Public/auth white; learner `#F8FAFC`; teacher/admin dark sidebar gradient `#0F0F2D` to `#1E1B4B`; teacher/admin content light | Role-specific shell exception is intentional |
| Breakpoints | Mobile `<768px`; tablet `768–1279px`; desktop `>=1280px`; fidelity capture 1440px; compact mobile `<=480px` | Sidebar collapses below 1280px |
| Header heights | Desktop 72px; tablet 64px; mobile 56px | Applies across shells unless a future reference exception is approved |
| Bottom navigation | Tablet 72px; mobile 64px plus safe-area inset | Mentor must not use the reported 56px bar |
| Radius | Control 12px; card 16px; large panel 20px; modal/bottom sheet 24px; pill 9999px | Any page exception must cite its reference |
| Font/license | Self-hosted Vazirmatn with the recorded local license file and hash | Remote fonts are forbidden |

`NO_HARDCODED_BRAND_COLORS` is mandatory. Any exception affecting an
authentication screen still requires the existing product/security approval
path.

## 8. Fidelity gate

No fidelity score is claimed by this analysis. After implementation is
explicitly authorized, score each reference and each viewport independently:

| Criterion | Weight |
|---|---:|
| Layout and geometry | 30 |
| Typography | 15 |
| Color/border/shadow/gradient | 15 |
| Spacing and RTL alignment | 15 |
| Components and states | 15 |
| Responsive behavior | 10 |
| Total | 100 |

Pass requires Desktop >=90, Tablet >=90, Mobile >=90, no missing major
section, and no horizontal overflow. A reviewer other than the implementer
must perform the visual comparison; this document is not self-approval.

## 9. Audit evidence and handoff

- `git diff --check`: passed.
- Worktree: only pre-existing modifications in
  `docs/coordination/CURRENT_TASK.md`, `PROJECT_STATE.md`, and `WORKLOG.md`;
  no coordination file was changed by this task.
- Backend/frontend source was not changed.
- No commit or push was performed, per `UI-FOUNDATION-002A` instruction.
- Local raw Gemini artifacts, exact prompts, and provider responses remain
  outside the repository.
- `SOURCE_IMPLEMENTATION = BLOCKED_PENDING_SPEC_APPROVAL`.
- `UI_FOUNDATION_002A-R = APPROVED_PENDING_DOCUMENT_FIXES`.
