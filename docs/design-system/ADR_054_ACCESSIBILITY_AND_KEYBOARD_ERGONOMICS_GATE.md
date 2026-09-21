# ADR_054_ACCESSIBILITY_AND_KEYBOARD_ERGONOMICS_GATE.md

## Status
ACCEPTED

## Context
CodeSho is committed to delivering a humane, non-punitive, accessible educational platform. As the design system and visual catalog were frozen in Wave 5.12, Wave 5.13 establishes formal architectural controls for accessibility, keyboard navigation, and screen reader announcements across all 4 role portals (Student, Mentor, Parent, Governance Admin).

## Decision
1. **WCAG 2.1 AA Compliance Mandate**:
   - All text must satisfy a 4.5:1 contrast ratio against container surfaces (3:1 for headers).
   - Diacritics and Persian ligature rendering must preserve an optical line-height $\ge 1.7$.
2. **Predictable Keyboard Containment**:
   - Focus traps must automatically contain focus inside modal dialogs (`MissionDetailModal`) and drawers (`MentorDrawer`, `ProjectDrawer`).
   - Focus must restore cleanly to trigger elements upon `Escape` dismissal.
3. **Non-Competitive Audio Feedback**:
   - Screen reader output must announce progression as qualitative steps (`گام ۳ از ۵`), explicitly forbidding rank, comparative percentiles, or competitive callouts.

## Consequences
- No UI component may merge without passing the ARIA semantic and keyboard containment gate.
- Code changes remain `0` in Wave 5.13 (Architecture & Governance Specification phase).
