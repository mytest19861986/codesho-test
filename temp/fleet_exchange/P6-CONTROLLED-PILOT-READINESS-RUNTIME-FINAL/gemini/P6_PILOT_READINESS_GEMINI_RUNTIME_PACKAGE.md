# Phase 6 Controlled Real Pilot Readiness: Gemini Ergonomics & UX Runtime Package

## Overview
- Interface: `ManagerDecisionCockpit.tsx`
- Standards: WCAG 2.2 AA compliant, minimum touch target 44x44px
- Friction & Safety: Two-step confirmation modal for manager authorization, friction modal for emergency suspension
- RTL / BiDi: Full RTL native layout with isolated `<bdi dir="ltr">` for code and UUID identifiers
- Educational Safety: Absolute enforcement of `anti_ranking_validated` and zero student leaderboard / competitive ranking

## Core Artifacts
1. `ManagerDecisionCockpit.tsx`:
   - Visual 14-Gate Pre-Admission Status indicator.
   - FSM state progression and real-world cap display.
   - Friction-controlled dual confirmation modal.
   - Immediate emergency suspension trigger.
2. `operations.module.css`:
   - Polished responsive grid and accessible typography styling.
