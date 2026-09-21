# ACCESSIBILITY_SPECIFICATION.md — CodeSho WCAG 2.1 AA & Persian RTL Ergonomics Spec

> **Wave 5.13 Phase 1 Architecture Specification**  
> **Status**: SPECIFICATION_STAGED ✅  
> **Hard Locks Enforced**: `CODE_CHANGE = 0`, `DATABASE_MIGRATION = 0`, `PRODUCTION_TOUCH = 0`  
> **Authority**: Commander AI & Human Project Manager  

---

## 1. Architectural Scope & Objectives

The purpose of this specification is to define strict accessibility contracts and Persian keyboard ergonomic rules across all four CodeSho role portals (**Student**, **Mentor**, **Parent**, **Governance Admin**).

### Core Principles
1. **Humane, Non-Punitive Accessibility**: Assistive feedback informs and empowers students without triggering performance anxiety or competitive stress.
2. **Keyboard-First Ergonomics**: Every interactive element must be reachable, operable, and dismissible using standard hardware keyboard commands (`Tab`, `Shift+Tab`, `Space`, `Enter`, `Escape`).
3. **RTL Native Landmark Alignment**: Semantic flow must align perfectly with right-to-left Persian optical hierarchies.

---

## 2. Keyboard Navigation & Focus Ring Contract

### Focus Ring Tokens
All interactive elements (buttons, inputs, links, drawer toggles) must utilize the global accessibility tokens established in Wave 5.12:
- **Outline Width**: `2px solid`
- **Outline Color**: `var(--color-primary-default)` (Student/Mentor) or role-specific primary token
- **Outline Offset**: `2px` (ensuring contrast separation between element boundary and focus ring)
- **Border Radius Match**: Outline must mirror the host element's `--radius-*` token.

### Focus Trap & Modal Ergonomics
When a modal dialog (`MissionDetailModal`) or slide-over drawer (`MentorDrawer`, `ProjectDrawer`) opens:
1. **Initial Focus**: Focus is automatically placed on the first interactive element or the primary dismiss button (`close`).
2. **Tab Containment**: Pressing `Tab` at the final focusable element loops focus back to the first.
3. **Escape Dismissal**: Pressing `Escape` must immediately close the overlay and restore focus to the triggering element.
4. **Scroll Lock**: The underlying `AppShell` viewport must freeze scrolling while preserving scrollbar gutter width (`scrollbar-gutter: stable`).

---

## 3. ARIA Semantics & Screen Reader Specifications

| Component | ARIA Role | Required ARIA Attributes | Screen Reader Announcement (fa-IR) |
|---|---|---|---|
| `AppShell` Navigation | `role="navigation"` | `aria-label="ناوبری اصلی"` | «ناوبری اصلی سامانه» |
| `NotificationBell` | `role="button"` | `aria-haspopup="true"`, `aria-expanded="false/true"` | «اعلان‌ها، باز کردن لیست رویدادها» |
| `MissionCard` | `role="article"` | `aria-labelledby="mission-title-id"` | «ماموریت یادگیری: عنوان پروژه» |
| `StatusBadge` | `role="status"` | `aria-label="وضعیت کیفی"` | «وضعیت: در حال بازبینی کیفی» |
| `DrawerOverlay` | `role="dialog"` | `aria-modal="true"`, `aria-labelledby="drawer-heading"` | «پنجره گفتگو با منتور» |

---

## 4. Persian Typography & Contrast Ratio Baseline

- **Standard Text**: Contrast ratio $\ge 4.5:1$ against background tokens.
- **Large Text / Headings ($\ge 18\text{pt}$ or bold $\ge 14\text{pt}$)**: Contrast ratio $\ge 3.0:1$.
- **Optical Line-Height Preservation**: All Persian headings and body typography must preserve a minimum `line-height` of `1.6` to guarantee that Persian diacritics (Tanvin, Tashdid, Kasreh) are never clipped by bounding boxes.

---

## 5. Phase 1 Verification Checklist
- `CODE_CHANGE: 0`
- `DATABASE_MIGRATION: 0`
- `GOVERNANCE_INTEGRITY: 100% PASS`
- `ANTI_EVALUATION_INVARIANT: 100% PRESERVED`
