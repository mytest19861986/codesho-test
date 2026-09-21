# COMPONENT_STATE_MATRIX.md — CodeSho Component State & Edge-Case Matrix

> **Wave 5.12 Phase 4 Deliverable**  
> **Status**: STATE_MATRIX_CREATED ✅  
> **Hard Locks Enforced**: `CODE_CHANGE = 0`, `DATABASE_MIGRATION = 0`, `PRODUCTION_TOUCH = 0`

---

## 1. State Coverage Matrix

| Component | Default | Loading / Skeleton | Empty State | Error / Alert | Disabled | Mobile (<768px) | RTL (Right-to-Left) |
|---|---|---|---|---|---|---|---|
| `AppShell` | Full 2-col Grid | Header Skeleton | — | Toast Alert Overlay | — | Off-canvas Drawer | Right-aligned Sidebar |
| `AppHeader` | Padded Bar | Shimmer User Avatar | — | Connection Badge | Search Disabled | Compact Hamburger | RTL Layout (`direction: ltr` wrapper for search/profile balance) |
| `Card` | `#ffffff` Surface | Shimmer Body Box | Centered Graphic | Red Border Accent | Muted Opacity | 100% Fluid Width | Box model RTL |
| `Button` | Filled Purple | Animated Spinner | — | Danger Variant | `opacity: 0.5` | Min Touch 44px | Icon at right/start |
| `Input` | 1px Gray Border | Pulse Placeholder | Clearable Cross | Red Border + Text | Gray Background | Full Width Block | Right-aligned text & caret |
| `Select` | Dropdown Pill | Disabled Skeleton | "No results" Option | Error Helper Text | Not-allowed cursor | Native Option Picker | Arrow on left in RTL |
| `Badge` | Static Status Pill | — | — | Red Counter | — | Fluid Wrapping | Inline RTL alignment |
| `Progress` | Progress Fill Bar | Indeterminate Slide | 0% Blank Meter | Red Alert Segment | Inactive Gray | Responsive Bar | Fills right to left |
| `ReviewTable` | Striped Rows | Row Skeleton Shimmer| "No pending tasks" | Retry Fetch Button | Locked Row | Horizontal Scroll | Table headers right-aligned |

---

## 2. Edge-Case Invariants
1. **Network Disruption**: UI components fail gracefully to cached states or prominent retry triggers without crashing the parent shell.
2. **Empty Content**: Every data-driven component (e.g. review queue, child notes, course list) must implement a dedicated empty state graphic and helpful call-to-action.
3. **Persian Numbers & Dates**: All counters, percentages, and timestamps must render Jalali dates with Persian digits (`۰-۹`).
