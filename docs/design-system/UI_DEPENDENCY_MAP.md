# UI_DEPENDENCY_MAP.md — CodeSho UI Dependency & Token Chain

> **Wave 5.12 Phase 2 Deliverable**  
> **Status**: COMPLETED  
> **Hard Locks Enforced**: `CODE_CHANGE = 0`, `DATABASE_MIGRATION = 0`, `PRODUCTION_TOUCH = 0`

---

## 1. Architectural Chain Pattern
The CodeSho Design System mandates a strict 4-tier dependency chain:
$$\text{Page Surface} \longrightarrow \text{Domain Section} \longrightarrow \text{UI Component} \longrightarrow \text{Design Token}$$

No page is permitted to bypass components and access raw styles directly.

---

## 2. Representative UI Dependency Traces

### 2.1. Student Dashboard Surface (`/student`)
```text
Page: /student
  └── Section: StudentCommandHero
        └── Component: Card (variant: highlight)
              ├── Token: --color-brand-primary-soft (#ede9fe)
              ├── Token: --color-surface-card (#ffffff)
              └── Token: --radius-lg (1.0rem / 16px)
        └── Component: Progress
              ├── Token: --color-brand-accent (#8b5cf6)
              └── Token: --space-2 (8px)
  └── Section: WeeklyLearningTrajectory
        └── Component: Card (variant: default)
              └── Token: --color-surface-border (#eef0f6)
        └── Component: Badge (variant: growth)
              └── Token: --color-status-success (#10b981)
```

### 2.2. Mentor Review Panel Surface (`/mentor/reviews`)
```text
Page: /mentor/reviews
  └── Section: ReviewQueueSection
        └── Component: Card (variant: default)
              ├── Token: --color-surface-card (#ffffff)
              └── Token: --shadow-card (0 2px 8px rgba(99, 102, 241, 0.04))
        └── Component: Button (variant: primary)
              ├── Token: --color-brand-primary (#6d28d9)
              └── Token: --radius-md (0.5rem / 8px)
```

### 2.3. Parent Growth Observatory Surface (`/parent`)
```text
Page: /parent
  └── Section: ChildGrowthGauges
        └── Component: ParentIntelligenceView
              └── Component: Card (variant: subtle)
                    ├── Token: --color-surface-card-subtle (#faf5ff)
                    └── Token: --typography-h2 (1.25rem / Bold 700)
```
