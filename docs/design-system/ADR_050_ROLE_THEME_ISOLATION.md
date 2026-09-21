# ADR-050: Role Theme Isolation

## Status
**APPROVED** (Commander Wave 5.12 Architecture Directive)

## Context
CodeSho serves four distinct user roles across the platform:
1. Student (`/student`)
2. Mentor (`/mentor`)
3. Parent (`/parent`)
4. Administrator (`/admin`)

To ensure long-term visual coherence without enforcing a sterile, identical appearance across disparate personas, a role-themed architectural contract is required.

## Decision
1. **Separation of Appearance and Semantics**:
   - Role themes may modify visual attributes (`accent-color`, `subtle-tint`, `icon-badge-background`).
   - Role themes **MUST NEVER** alter interaction semantics, accessibility attributes, navigation primitives, or business logic.
2. **Standardized Role Identity Palette**:
   - **Student**: Core Purple (`#6d28d9`) + Growth Mint (`#10b981`) + Discovery Sky (`#0284c7`). Tone: Encouraging, friendly, non-punitive.
   - **Mentor**: Deep Royal Purple (`#581c87`) + Analytical Slate (`#475569`). Tone: Professional, structured, high-efficiency.
   - **Parent**: Warm Violet (`#7c3aed`) + Trust Emerald (`#059669`) + Soft Neutral (`#f8fafc`). Tone: Reassuring, clear, transparent.
   - **Admin**: Deep Indigo/Navy (`#1e1b4b`) + Governance Amber (`#d97706`). Tone: High-density, operational, controlled.

## Consequences
- Prevents rogue component forks per role.
- All roles share the exact same `AppShell`, `Card`, `Table`, and `Button` foundation components.
