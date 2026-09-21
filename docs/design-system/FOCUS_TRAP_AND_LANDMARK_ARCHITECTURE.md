# FOCUS_TRAP_AND_LANDMARK_ARCHITECTURE.md — CodeSho Focus Management & Persian RTL Landmark Architecture

> **Wave 5.13 Phase 3 Architecture Specification**  
> **Status**: SPECIFICATION_DELIVERED ✅  
> **Hard Locks Enforced**: `CODE_CHANGE = 0`, `DATABASE_MIGRATION = 0`, `PRODUCTION_TOUCH = 0`  
> **Authority**: Commander AI & Human Project Manager  

---

## 1. Executive Summary & Architectural Invariant

This document establishes the official focus management, keyboard trap containment, and landmark routing architecture across CodeSho.

In accordance with our **Humane Pedagogical Architecture**, focus handling must be predictable and seamless, preventing user disorientation or disruptive jumps across RTL surfaces.

---

## 2. Navigational Landmark Architecture (Persian RTL)

All page layouts must expose explicit HTML5 landmarks with unique descriptive Persian labels:

```text
<body>
  ├── <header role="banner" aria-label="سربرگ و نوار دسترسی سریع">
  ├── <nav role="navigation" aria-label="منوی اصلی ناوبری سامانه‌ها">
  ├── <main role="main" id="main-content" aria-label="محتوای اصلی یادگیری">
  └── <aside role="complementary" aria-label="پانل اطلاعات تکمیلی و راهنما">
```

### Skip-to-Content Link
- **Anchor**: First focusable child in DOM (`<a href="#main-content" class="skip-link">رفتن به محتوای اصلی</a>`).
- **Styling Tokens**: Visually hidden off-screen (`top: -999px`) until focused (`:focus`), where it renders at `top: 16px; right: 16px;` using `--color-primary-default` and `--radius-pill`.

---

## 3. Focus Trap Engine Specification (Drawers & Modals)

### State Machine Lifecycle
```text
[CLOSED]
   │
   ▼ User triggers open (Click / Enter / Space)
[OPENING]
   │  1. Cache document.activeElement (Origin Element)
   │  2. Attach keydown listener (Tab, Shift+Tab, Escape)
   │  3. Set body overflow to hidden with scrollbar gutter reservation
   ▼
[OPEN & TRAPPED]
   │  4. Send focus to first interactive child (or close button)
   │  5. Tab at last child wraps to first child
   │  6. Shift+Tab at first child wraps to last child
   ▼ User triggers close (Escape / Backdrop click / Dismiss button)
[CLOSING]
   │  1. Detach keydown listener
   │  2. Restore body scroll
   │  3. Restore focus to cached Origin Element
   ▼
[CLOSED]
```

### Component Coverage Matrix
| Overlay Component | Role Surface | First Focus Target | Escape Behavior | Origin Focus Restored |
|---|---|---|---|---|
| `MissionDetailModal` | Student | Primary Close Button | Dismisses modal | MissionCard Action Button |
| `MentorDrawer` | Student | Mentor Message Input | Dismisses drawer | Mentor Drawer Toggle Chip |
| `ProjectDrawer` | Student | Project Artifact Spec Tab | Dismisses drawer | Project Details Trigger |
| `CoachingFeedbackDrawer`| Mentor | Feedback Reflection Textarea| Dismisses drawer | Review Item Trigger |

---

## 4. Phase 3 Invariant Verification
- `CODE_CHANGE: 0`
- `DATABASE_MIGRATION: 0`
- `KEYBOARD_ACCESSIBILITY_INTEGRITY: 100% SPECIFIED`
- `RTL_OPTICAL_PRESERVATION: 100% PASS`
