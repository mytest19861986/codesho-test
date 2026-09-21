# ADR-051: Visual Regression Gate

## Status
**APPROVED** (Commander Wave 5.12 Architecture Directive)

## Context
Rapid iterative development and multi-role feature additions introduce silent CSS bleed, layout distortion, and visual drift across viewports and RTL alignments.

## Decision
1. **Mandatory Evidence Contract Before Merge**:
   - No UI-affecting code change may be merged or deployed without an accompanying automated Visual Regression Audit.
2. **Audit Dimensions**:
   - **Resolutions**: Desktop 1440px, Desktop 1920px, Mobile 390px.
   - **Directionality**: 100% RTL verification (`dir="rtl"`, no inverted SVG icons or misaligned meta chips).
   - **Artifacts**: Minimum 8-10 representative route screenshots saved to `docs/evidence/` or temporary GitHub artifacts before approval.
3. **Hard Lock During Audits**:
   - Refactor hold is strictly enforced during visual audits (`CODE_CHANGE = 0`, `UI_REFACTOR = LOCKED`). Code changes are only unlocked once the audit dossier is officially accepted by Commander.

## Consequences
- Completely eliminates accidental visual regressions on production.
- Ensures absolute compliance with the CodeSho Global Design System Directive.
