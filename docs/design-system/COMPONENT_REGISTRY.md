# COMPONENT_REGISTRY.md — CodeSho Official Component Registry (DS-1.0)

> **Wave 5.12 Phase 2 Deliverable**  
> **Status**: INVENTORY & CLASSIFICATION COMPLETE  
> **Hard Locks Enforced**: `CODE_CHANGE = 0`, `DATABASE_MIGRATION = 0`, `PRODUCTION_TOUCH = 0`, `UI_REFACTOR = FORBIDDEN`

---

## 1. Registry Architecture Overview

The CodeSho UI ecosystem is organized into 6 standardized component domains:

```text
UI Registry
├── 1. Layout & Shell Domain
├── 2. Navigation Domain
├── 3. Data Display Domain (Cards, Badges, Metrics)
├── 4. Form & Control Primitives
├── 5. Feedback & Overlay Domain
└── 6. Role Intelligence Surface Views
```

---

## 2. Inventory & Classification Catalog

### 2.1. Layout & Shell Domain
| Component Name | Source File | Category | Classification |
|---|---|---|---|
| `AppShell` | `frontend/src/components/layout/AppShell.tsx` | Shell | Global Responsive Shell Container |
| `AppHeader` | `frontend/src/components/layout/AppHeader.tsx` | Header | Top Sticky Application Bar |
| `Sidebar` | `frontend/src/components/layout/Sidebar.tsx` | Navigation | Desktop Right-Aligned RTL Sticky Bar |
| `PublicShell` | `frontend/src/components/layout/PublicShell.tsx` | Public | Unauthenticated Global Shell |
| `PublicHeader` | `frontend/src/components/layout/PublicHeader.tsx` | Public | Unauthenticated Header |
| `PublicFooter` | `frontend/src/components/layout/PublicFooter.tsx` | Public | Landing / Legal Public Footer |

### 2.2. Navigation Domain
| Component Name | Source File | Category | Classification |
|---|---|---|---|
| `NavigationDrawer` | `frontend/src/components/layout/NavigationDrawer.tsx` | Mobile | Off-Canvas RTL Drawer for Viewport < 768px |
| `MobileBottomNav` | `frontend/src/components/layout/MobileBottomNav.tsx` | Mobile | Bottom Fixed App Navigation for Handhelds |
| `PublicNavigationDrawer` | `frontend/src/components/layout/PublicNavigationDrawer.tsx` | Public Mobile | Landing Drawer Menu |

### 2.3. Data Display Domain (Cards, Badges, Metrics)
| Component Name | Source File | Category | Classification |
|---|---|---|---|
| `Card` | `frontend/src/components/ui/Card.tsx` | Surface | Unified Content & KPI Container |
| `CardHeader` | `frontend/src/components/ui/Card.tsx` | Surface | Standard Header with Title & Action Slot |
| `CardBody` | `frontend/src/components/ui/Card.tsx` | Surface | Primary Padded Content Slot |
| `CardFooter` | `frontend/src/components/ui/Card.tsx` | Surface | Bottom Action / Metadata Gutter |
| `Badge` | `frontend/src/components/ui/Badge.tsx` | Indicator | Status Chips, Counters, Role Indicators |
| `Progress` | `frontend/src/components/ui/Progress.tsx` | Indicator | Horizontal Progress Bars & Meters |

### 2.4. Form & Control Primitives
| Component Name | Source File | Category | Classification |
|---|---|---|---|
| `Button` | `frontend/src/components/ui/Button.tsx` | Control | Primary, Secondary, Ghost, Danger CTAs |
| `IconButton` | `frontend/src/components/ui/IconButton.tsx` | Control | Compact Square / Pill Icon Triggers |
| `Input` | `frontend/src/components/ui/Input.tsx` | Form | Text, Password, Search Inputs |
| `Select` | `frontend/src/components/ui/Select.tsx` | Form | Accessible RTL Dropdowns & Pickers |
| `Icons` (Collection) | `frontend/src/components/ui/Icons.tsx` | Vector | Standardized Inline SVG Icon Primitives |

### 2.5. Feedback & Overlay Domain
| Component Name | Source File | Category | Classification |
|---|---|---|---|
| `NotificationPopover` | `frontend/src/components/layout/NotificationPopover.tsx` | Overlay | Bell Triggered Activity & Notification List |

### 2.6. Role Intelligence Surface Views
| Component Name | Source File | Role Target | Classification |
|---|---|---|---|
| `StudentIntelligenceView`| `frontend/src/components/learning_intelligence/StudentIntelligenceView.tsx` | Student (`/student`) | Adaptive AI Learning Recommendations & Growth |
| `MentorIntelligenceView` | `frontend/src/components/learning_intelligence/MentorIntelligenceView.tsx` | Mentor (`/mentor`) | Student Cohort Analytics & Review Priorities |
| `ParentIntelligenceView` | `frontend/src/components/learning_intelligence/ParentIntelligenceView.tsx` | Parent (`/parent`) | Transparent Progress Telemetry & Skill Gauges |
