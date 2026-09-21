# CodeSho Design Token Manifest (DS-1.0)

> **Wave 5.12 Phase 1 Artifact**  
> **Status**: APPROVED  
> **Hard Locks Enforced**: `CODE_CHANGE = 0`, `DATABASE_MIGRATION = 0`, `PRODUCTION_CHANGE = 0`, `UI_REFACTOR = LOCKED`

---

## 1. Core Brand Tokens
Unified master brand palette rooted in the reference design directive (`media_1789981802684.png`).

| Token Name | Hex Value | Purpose |
|---|---|---|
| `--color-brand-primary` | `#6d28d9` / `#7c3aed` | Primary action, focus rings, brand anchors |
| `--color-brand-primary-soft` | `#ede9fe` / `#f3e8ff` | Active navigation pill, badge highlights |
| `--color-brand-dark` | `#1e1b4b` | High-contrast governance accents |
| `--color-brand-accent` | `#8b5cf6` | Progress indicators, charts, subtle gradient stops |

---

## 2. Surface & Background Tokens
All component background definitions fail closed to semantic surface tokens.

| Token Name | Hex Value | Purpose |
|---|---|---|
| `--color-surface-bg` | `#f8f9fd` / `#f5f6fa` | Global page viewport background (RTL canvas) |
| `--color-surface-card` | `#ffffff` | Elevated component cards, containers, dialogs |
| `--color-surface-card-subtle` | `#faf5ff` | Highlighted metric cards, soft emphasis boxes |
| `--color-surface-border` | `#eef0f6` | 1px subtle separation borders |
| `--color-surface-overlay` | `rgba(15, 23, 42, 0.45)` | Modal / off-canvas drawer backdrops |

---

## 3. Typography Hierarchy (Vazirmatn Scale)
Standardized Persian-first typographic scale. Zero arbitrary ad-hoc font-sizes allowed.

| Typography Token | Size / Weight | Line Height | Application |
|---|---|---|---|
| `--typography-display` | `2.0rem` (Bold 700) | `2.5rem` | Landing headline, major milestone screens |
| `--typography-h1` | `1.5rem` (Bold 700) | `2.0rem` | Page title (single `<h1>` per view) |
| `--typography-h2` | `1.25rem` (SemiBold 600) | `1.75rem` | Card titles, section headers |
| `--typography-h3` | `1.125rem` (Medium 500) | `1.5rem` | Subsection titles, widget group labels |
| `--typography-body-lg` | `1.0rem` (Regular 400) | `1.6rem` | Primary paragraphs, description text |
| `--typography-body` | `0.875rem` (Regular 400) | `1.5rem` | Table data, standard card content |
| `--typography-caption` | `0.75rem` (Medium 500) | `1.25rem` | Meta timestamps, badge labels, helper text |

---

## 4. Spacing Scale (4px Base Grid)
Harmonized spacing tokens across all layouts, cards, and micro-interactions.

| Token | Dimension | Rem Equivalent | Usage Example |
|---|---|---|---|
| `--space-1` | `4px` | `0.25rem` | Tight tag padding, icon gaps |
| `--space-2` | `8px` | `0.5rem` | Button icon margin, compact row gaps |
| `--space-3` | `12px` | `0.75rem` | Control padding, table cell vertical padding |
| `--space-4` | `16px` | `1.0rem` | Card internal padding (mobile), standard gaps |
| `--space-6` | `24px` | `1.5rem` | Desktop card padding, section separators |
| `--space-8` | `32px` | `2.0rem` | Shell page content gutter, header margins |
| `--space-12` | `48px` | `3.0rem` | Major dashboard grid vertical spacing |

---

## 5. Border Radius Tokens
| Token | Value | Applied To |
|---|---|---|
| `--radius-sm` | `0.375rem` (6px) | Badges, small tooltips |
| `--radius-md` | `0.5rem` (8px) | Input controls, standard buttons, select dropdowns |
| `--radius-lg` | `1.0rem` (16px) | Standard surface cards, widget boxes |
| `--radius-xl` | `1.5rem` (24px) | Modals, off-canvas drawers, hero cards |
| `--radius-pill` | `9999px` | Header search bar, filter chips, active navigation pills |

---

## 6. Elevation & Shadows
| Token | Specification | Application |
|---|---|---|
| `--shadow-sm` | `0 1px 2px rgba(0, 0, 0, 0.05)` | Controls, search bar default state |
| `--shadow-card` | `0 2px 8px rgba(99, 102, 241, 0.04)` | Surface cards, KPI metric widgets |
| `--shadow-floating` | `0 10px 25px -5px rgba(0, 0, 0, 0.1)` | Modals, drawers, popovers, notification bells |

---

## 7. Responsive Breakpoints
| Viewport Profile | Width | Layout Behavioral Rule |
|---|---|---|
| **Mobile** | `390px` | Sidebar converts to drawer / bottom nav; 1-column cards |
| **Tablet** | `768px` | 2-column KPI cards; sticky header; compact sidebar |
| **Desktop Base** | `1440px` | Multi-column grid (3-4 KPI stats, 2-column main area) |
| **Desktop Large** | `1920px` | Max-width centered container (`1600px` max-width content bounding) |
