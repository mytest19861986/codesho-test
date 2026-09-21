# STORYBOOK_ARCHITECTURE.md — CodeSho Storybook & Visual Catalog Architecture

> **Wave 5.12 Phase 4 Deliverable**  
> **Status**: STORYBOOK_ARCHITECTURE_DEFINED ✅  
> **Execution Mode**: ARCHITECTURE SPECIFICATION ONLY (Zero code installation/refactor)

---

## 1. Directory & Category Hierarchy

The official Storybook workspace structure mirrors the 3-tier Design System layers:

```text
.storybook/
src/stories/
├── 1. Foundations
│   ├── Colors.stories.tsx
│   ├── Typography.stories.tsx
│   ├── Spacing.stories.tsx
│   ├── Shadows.stories.tsx
│   └── Breakpoints.stories.tsx
│
├── 2. Core Primitives
│   ├── Button.stories.tsx
│   ├── IconButton.stories.tsx
│   ├── Input.stories.tsx
│   ├── Select.stories.tsx
│   ├── Badge.stories.tsx
│   ├── Progress.stories.tsx
│   └── Card.stories.tsx
│
├── 3. Shell & Navigation
│   ├── AppShell.stories.tsx
│   ├── AppHeader.stories.tsx
│   ├── Sidebar.stories.tsx
│   └── NavigationDrawer.stories.tsx
│
└── 4. Role Experiences (Persona Storyboards)
    ├── StudentDashboard.stories.tsx
    ├── MentorReviewQueue.stories.tsx
    ├── ParentObservatory.stories.tsx
    └── AdminGovernance.stories.tsx
```

---

## 2. Storybook Parameter Standards
1. **RTL First Decorator**:
   - Every story is wrapped in an RTL decorator container (`dir="rtl"`, Persian font family Vazirmatn).
2. **Multi-Viewport Addon Profiles**:
   - Preset viewports: Mobile (`390px`), Tablet (`768px`), Desktop Base (`1440px`), Desktop Large (`1920px`).
3. **Role Theme Selector**:
   - Interactive toolbar switch dynamically toggles `--role-theme` attribute between `student`, `mentor`, `parent`, and `admin`.
