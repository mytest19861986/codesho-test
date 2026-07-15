# Load Test Scenarios (P0 Definition)

Execution is P1 after representative APIs exist. Baselines are measured on the
approved 2 vCPU / 4 GB Ubuntu 24.04 target or an equivalent staging host.

## Initial workload model

- Alpha: 8 concurrent VIP learners plus mentor/admin activity.
- Normal launch: 100 concurrent authenticated learners, 10 writes/second peak.
- Burst: 250 concurrent users for 10 minutes during enrollment/payment opening.
- Background: two Celery workers processing notification/outbox work.

## Scenarios and provisional gates

| Scenario | Duration | Gate |
|---|---:|---|
| Liveness/readiness | 5 min | p95 < 150 ms, 0% errors |
| Authenticated dashboard read | 15 min | p95 < 500 ms, p99 < 1 s, errors < 0.5% |
| Lesson progress write | 15 min | p95 < 750 ms, errors < 0.5%, no duplicates |
| Enrollment reservation burst | 10 min | no oversell; p95 < 1 s |
| Tenant isolation mixed load | 15 min | zero cross-tenant rows/context leaks |
| Worker backlog recovery | 30 min | backlog drains without request latency breach |

Resource gate: sustained CPU below 75%, memory below 80%, PostgreSQL connection
usage below 70% of configured pool. These are provisional SLOs, not customer SLA.
