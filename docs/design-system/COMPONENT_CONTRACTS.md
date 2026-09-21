# COMPONENT_CONTRACTS.md — Official Component Interface Contracts

> **Wave 5.12 Phase 2 Deliverable**  
> **Status**: CONTRACT SPECIFICATION COMPLETE  
> **Hard Locks Enforced**: `CODE_CHANGE = 0`, `DATABASE_MIGRATION = 0`, `PRODUCTION_TOUCH = 0`

---

## 1. AppShell Contract
```yaml
Component: AppShell
Purpose: Global application framework managing RTL layout grid, sticky sidebar, top header, and mobile drawers.
Owner: Layout Team
Used By:
  - app/admin/**
  - app/student/**
  - app/mentor/**
  - app/parent/**
Props:
  role: 'student' | 'mentor' | 'parent' | 'admin'
  userProfile: { name: string, roleTitle: string, avatarUrl?: string }
  navigationItems: Array<{ label: string, href: string, icon: Component, badge?: string | number }>
  children: ReactNode
Variants:
  - Default (Full Desktop 2-column RTL grid)
  - MobileCollapsible (Off-canvas drawer + bottom nav)
Theme Compatibility: All Roles (Student, Mentor, Parent, Admin)
RTL Support: 100% Native (`grid-template-columns: minmax(0, 1fr) var(--cs-shell-sidebar)`)
Mobile Behavior: Sidebar hides at < 768px; Header hamburger button exposes NavigationDrawer.
Screenshot Reference: temp/audit_02_student_main_1440x900.png
```

---

## 2. Card & CardHeader Contract
```yaml
Component: Card
Purpose: Universal elevated surface container for all KPI statistics, learning courses, review tables, and metrics.
Owner: Foundation UI Team
Used By: All modules (>65 active instances across platform)
Props:
  variant: 'default' | 'subtle' | 'bordered' | 'highlight'
  padding: 'none' | 'sm' | 'md' | 'lg'
  children: ReactNode
Variants:
  - default: `#ffffff` background with subtle 1px border (`#eef0f6`)
  - subtle: `#f8f9fd` tinted background for nested widgets
  - highlight: soft lavender border highlight for active tasks
Theme Compatibility: Fully theme-isolated via `--color-surface-card`
RTL Support: Natural box model; content inherits document RTL
Mobile Behavior: 100% width fluid scaling; auto margin
Screenshot Reference: temp/audit_01_dashboard_admin_1440x900.png
```

---

## 3. Button Primitive Contract
```yaml
Component: Button
Purpose: Interactive trigger for primary workflows, filters, dialog submissions, and task progression.
Owner: Foundation UI Team
Used By: Global Application
Props:
  variant: 'primary' | 'secondary' | 'ghost' | 'danger'
  size: 'sm' | 'md' | 'lg'
  icon?: Component
  iconPosition?: 'start' | 'end'
  isLoading?: boolean
  disabled?: boolean
Variants:
  - primary: Filled brand primary (`#6d28d9`), white text
  - secondary: Subtle brand soft (`#ede9fe`), violet text
  - ghost: Transparent background, hover tint
  - danger: Semantic red soft fill for irreversible governance actions
Theme Compatibility: Respects role accent on focus ring and primary fill
RTL Support: Inline icon positions dynamically adapt to start/end in RTL
Mobile Behavior: Touch-friendly min-height (`44px` on mobile screens)
Screenshot Reference: temp/audit_06_mentor_panel_1440x900.png
```

---

## 4. Role Intelligence View Contract
```yaml
Component: StudentIntelligenceView | MentorIntelligenceView | ParentIntelligenceView
Purpose: Role-tailored learning analytics, progress telemetries, and personalized guidance insights.
Owner: Learning Intelligence Team
Used By:
  - `/student`
  - `/mentor`
  - `/parent`
Props:
  data: IntelligenceProjectionPayload
  refreshIntervalMs?: number
Theme Compatibility: Role-locked (Student = Growth, Mentor = Guidance, Parent = Trust)
RTL Support: Persian numerals, right-aligned charts and progress dials
Mobile Behavior: Multi-metric grid stacks vertically into a clean 1-column feed
Screenshot Reference: temp/audit_08_parent_observatory_1440x900.png
```
