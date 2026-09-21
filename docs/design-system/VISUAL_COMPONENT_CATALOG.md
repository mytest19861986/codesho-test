# VISUAL_COMPONENT_CATALOG.md — CodeSho Visual Component Catalog

> **Wave 5.12 Phase 4 Deliverable**  
> **Status**: CATALOG_CREATED ✅  
> **Hard Locks Enforced**: `CODE_CHANGE = 0`, `DATABASE_MIGRATION = 0`, `PRODUCTION_TOUCH = 0`

---

## 1. Shell & Framework Components

```yaml
Component: AppShell
Category: Layout
Purpose: Master multi-role responsive container managing persistent RTL sidebar, header, and off-canvas drawers.
Used Roles: Student, Mentor, Parent, Admin
Variants:
  - Desktop: 2-column RTL sticky grid (`grid-column: 2` for sidebar)
  - Mobile: Full width 1-column canvas with sliding overlay drawer
States:
  - Default: Standard authenticated view
  - DrawerOpen: Modal backdrop overlay active (`--color-surface-overlay`)
Responsive Behavior: Fluid collapsing at 768px breakpoint
Token Dependencies:
  - `--color-surface-bg`
  - `--cs-shell-sidebar`
  - `--cs-shell-header-desktop`
Screenshot Reference: temp/audit_02_student_main_1440x900.png
```

```yaml
Component: AppHeader
Category: Layout
Purpose: Sticky top navigation bar containing branding, user profile, theme toggle, and search trigger.
Used Roles: Student, Mentor, Parent, Admin
Variants:
  - Default: Pill search input + notification bell + user chip
  - Compact: Hamburger toggle + brand mark + user avatar
States:
  - Default: Inactive search
  - Active: Search focused with elevated drop shadow (`--shadow-sm`)
Responsive Behavior: Search input collapses to icon trigger on mobile viewports (< 640px)
Token Dependencies:
  - `--radius-pill`
  - `--color-surface-card`
  - `--color-surface-border`
Screenshot Reference: temp/audit_01_dashboard_admin_1440x900.png
```

---

## 2. Data Display & Card Components

```yaml
Component: Card
Category: Data Display
Purpose: Universal elevated surface container for KPI widgets, learning paths, and administrative modules.
Used Roles: Student, Mentor, Parent, Admin
Variants:
  - default: Pure white surface (`#ffffff`) with subtle 1px border (`#eef0f6`)
  - subtle: Soft grayish-violet tinted canvas (`#faf5ff`)
  - highlight: Soft lavender glow (`#ede9fe`)
States:
  - Default: Neutral elevation (`--shadow-card`)
  - Hover: Subtle translate-y micro-interaction (`-2px`)
  - Loading: Skeleton shimmer placeholder
Responsive Behavior: Multi-column grid on desktop; full-width vertical stack on mobile
Token Dependencies:
  - `--color-surface-card`
  - `--radius-lg`
  - `--space-4` / `--space-6`
Screenshot Reference: temp/audit_06_mentor_panel_1440x900.png
```

```yaml
Component: Badge
Category: Data Display
Purpose: Compact metadata chip for status flags, role tags, and progress counters.
Used Roles: Student, Mentor, Parent, Admin
Variants:
  - primary: Soft brand purple background with bold violet text
  - success: Soft emerald background (`#dcfce7`) with green text (`#15803d`)
  - warning: Soft amber background with warning text
States:
  - Default: Static inline-block pill
Responsive Behavior: Scales with typography; text wraps or truncates safely
Token Dependencies:
  - `--radius-pill`
  - `--space-1` / `--space-2`
  - `--typography-caption`
Screenshot Reference: temp/audit_08_parent_observatory_1440x900.png
```

---

## 3. Control & Action Primitives

```yaml
Component: Button
Category: Forms & Controls
Purpose: Interactive trigger for workflows, modal actions, and navigation.
Used Roles: Student, Mentor, Parent, Admin
Variants:
  - primary: Solid purple brand CTA
  - secondary: Soft brand tint
  - ghost: Transparent with hover outline
States:
  - Default: Active interactive
  - Hover: Subtle brightness increase
  - Active/Pressed: Scale down (`0.98`)
  - Disabled: Reduced opacity (`0.5`), cursor not-allowed
  - Loading: Spinner animation replacing text
Responsive Behavior: Min touch target `44px` on handheld touch devices
Token Dependencies:
  - `--color-brand-primary`
  - `--radius-md`
  - `--space-3`
Screenshot Reference: temp/audit_07_mentor_reviews_1440x900.png
```
