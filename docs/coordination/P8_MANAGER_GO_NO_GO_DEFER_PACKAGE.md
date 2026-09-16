# P8 Manager GO / NO_GO / DEFER Package Specification

## 1. Cockpit Interface Architecture
The Admission Decision Cockpit must present a clear, non-coercive, fail-closed surface for the Human Manager:

### Required Visual Panels:
1. **Decision Status Header**:
   - Distinct visual state badge: `GO` (Green), `NO_GO` (Red), `DEFER` (Amber).
   - Prominent notice of exclusive human authority: "Requires Human Manager Authentication".
2. **Non-Waivable Hard Stops Dashboard**:
   - Zero tolerance list (Evidence Freshness, Backup Recency, PITR Status, Scope Match, Zero Open Incidents).
   - If any single item is not met, the global status automatically locks to `HARD_STOP_FAIL (NO_GO)`.
   - Explicit prohibition of weighted averages or percentage-based overrides.
3. **Pilot Scope & Boundary Metrics**:
   - Organization: Displayed clearly with name and UUID.
   - Cohort Size: Explicit ceiling (e.g. `12 / 50 Students Admitted`).
   - Duration & Expiry: Countdown timer with explicit timestamp.
4. **Data Admission & Privacy Check**:
   - Verification that only permitted non-identifying data elements are present.
   - Verification of 100% guardian consent coverage.
5. **Emergency Termination Controls**:
   - Two-step confirmation modal for Emergency Kill Switch and Crypto-Shredding.
   - High visual friction to prevent accidental triggers.

### Accessibility & BiDi Standards:
- **WCAG 2.2 AA**: Target touch sizes >= 44x44px, color contrast >= 4.5:1, independent color cues (icons + text).
- **RTL & BiDi**: Native RTL layout with technical tokens, commit SHAs, and UUIDs isolated in `<bdi dir="ltr">`.
