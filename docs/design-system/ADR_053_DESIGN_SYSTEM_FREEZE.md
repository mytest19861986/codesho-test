# ADR-053: Design System Governance Freeze

## Status
**APPROVED** (Commander Wave 5.12 Phase 5 Final Closure Directive)

## Context
Following the completion of Wave 5.12 (Phases 1 through 5), the CodeSho Design System (DS-1.0) is officially codified, verified across all four user roles, and audited against visual drift. To prevent subsequent waves or sprint tasks from degrading visual harmony, permanent governance constraints must be frozen.

## Decision

### Permanent Architectural Laws:
1. **Rule 1: No Uncontrolled Tokens**
   - Any new color, spacing, elevation, or typography value must be formally added to `docs/design-system/DESIGN_TOKEN_MANIFEST.md` before use. Inline ad-hoc CSS values are strictly prohibited.
2. **Rule 2: No Duplicated Components**
   - Before any new component is created, `docs/design-system/COMPONENT_REGISTRY.md` must be inspected. Reusable components must be composed rather than duplicated.
3. **Rule 3: No Role Theme Leakage**
   - Visual tokens of one persona theme (e.g. Student growth badges) must never infiltrate another persona's domain logic or visual layout without explicit contract updates.
4. **Rule 4: No Direct Styling Bypass**
   - Pages and feature views must never bypass the design system by importing external styling libraries or applying un-tokenized global style overrides.
5. **Rule 5: Visual Regression Gate Enforcement**
   - Every future pull request affecting UI surfaces must provide automated screenshot artifacts across mobile (390px) and desktop (1440px) viewports before merge approval.

## Consequences
- The design system state transitions to `RESTING_DESIGN_SYSTEM_STATE`.
- Unlocks predictable, modular frontend development for future waves.
