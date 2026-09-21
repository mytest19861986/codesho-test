# ADR-052: Storybook & Visual Regression Gate Extension

## Status
**APPROVED** (Commander Wave 5.12 Phase 4 Directive)

## Context
As CodeSho expands across multiple specialized roles, verifying UI changes across hundreds of potential states manually becomes impractical and prone to human oversight.

## Decision
1. **Storybook Catalog as Living Ground Truth**:
   - The visual catalog specified in `docs/design-system/STORYBOOK_ARCHITECTURE.md` serves as the official design system reference.
   - Any new component or variant must be registered in the catalog before production integration.
2. **Visual Gate Extension Process**:
   - Prior to approving any future UI pull request, automated or audited screenshots must be produced for:
     1. **Component Snapshot**: Isolation snapshot covering Default, Loading, and Empty states.
     2. **Viewport Check**: Render validation at `390px` and `1440px`.
     3. **Token Compliance Check**: Zero hardcoded hex colors or inline pixel margins; 100% token adherence.
3. **Hard Lock Enforced**:
   - No production UI code changes are permitted during catalog architecture phases (`CODE_CHANGE = 0`).

## Consequences
- Guarantees absolute design consistency across future iterations.
- Provides immediate visual evidence for Commander and manager reviews.
