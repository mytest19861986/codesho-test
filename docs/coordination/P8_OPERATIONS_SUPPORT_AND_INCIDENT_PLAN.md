# P8 Operations Support and Incident Plan

## 1. Incident Severity Classification & SLA
- **SEV-1 (Critical Block)**: Data breach, cross-tenant leak, unauthorized token activation, or system-wide outage.
  - *Response Time*: < 15 minutes.
  - *Immediate Action*: Trigger Emergency Kill Switch (`execute_emergency_kill_switch`), pause pilot, notify Human Manager.
- **SEV-2 (Major Impact)**: Service degradation, single-tenant admission failure, stale evidence alert.
  - *Response Time*: < 1 hour.
- **SEV-3 (Minor / Informational)**: Non-blocking UI glitch, minor telemetry drift.
  - *Response Time*: Next business day.

## 2. On-Call Roles and Responsibilities
- **Incident Commander (Human Manager)**: Sole authority to approve SEV-1 communications, scope alterations, or pilot abort.
- **Technical Lead (Commander AI / Codex)**: Diagnostics, isolated patch generation, verification and evidence collection.
- **Reviewer Fleet (Qwen, GLM, Gemini)**: Independent audit of remediation diffs prior to any promotion.
