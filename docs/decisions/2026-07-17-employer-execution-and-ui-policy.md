# Employer execution and UI policy gates

Date: 2026-07-17
Status: approved by Commander; employer decision remains authoritative

## Scope

Before UI shell or page implementation, the repository must enforce:

- `NO_RAW_COLORS_IN_COMPONENTS`: production components and pages use semantic
  tokens; raw colors and direct-color gradients are prohibited outside the
  token layer. The three approved legacy files are hash-pinned exemptions.
- `NO_MARKETING_COPY_IN_JSX`: user-facing marketing copy is supplied through
  typed content under `frontend/src/content/` or `frontend/src/i18n/fa/`.
- `NO_FAKE_PRODUCTION_METRICS`: production does not ship fabricated metrics,
  testimonials, prices, discounts or claims. Preview/test fixtures cannot be
  imported by production routes or components.

Any violation is BLOCKING. Legacy exemptions are temporary and their removal
is tracked by the future `UI-HOME-002` task.

## Decision protocol

When a product, employer, legal, asset, or scope decision is required:

- `T+0`: present the question, mutually exclusive options, Commander
  recommendation, and the impact of each option.
- `T+10m`: send exactly one reminder if no answer arrived.
- No answer: park the blocked task and checkpoint it; continue only work that
  was independently authorized before the decision.
- Never infer, self-approve, expand scope, or repeat reminders indefinitely.
- When the employer returns, re-present the pending decision before acting.
- If no independent authorized task exists, enter safe standby.

Waiting must be non-blocking: do not use long sleeps or busy-wait loops as a
policy mechanism.
