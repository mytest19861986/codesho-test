# Reliability Playbook: Incident Classification & Response Protocols

## 1. Operational Philosophy
The CodeSho Reliability Playbook provides standardized, deterministic remediation procedures for operational degradation and infrastructure incidents. Remediation actions prioritize system stability, tenant isolation, and zero student data compromise.

---

## 2. Standardized Incident Response Playbooks

### 2.1 Playbook A: API Latency Degradation (P95 > 250ms)
- **Primary Trigger**: 3 consecutive telemetry intervals with API P95 latency > 250ms.
- **Root Cause Vectors**: High database connection saturation, cache eviction storm, un-optimized nested serialization.
- **Remediation Steps**:
  1. Inspect Redis cache availability and hit ratio (`INFO stats`).
  2. If hit ratio < 75%, trigger automated pre-warming of critical role landing metadata.
  3. Verify PostgreSQL connection pool status via `pg_stat_activity`. Terminate transactions in `idle in transaction` state exceeding 15 seconds.
  4. Dynamically increment Gunicorn worker threads if CPU saturation < 70%.

### 2.2 Playbook B: Database Query & Lock Contention Spike
- **Primary Trigger**: Query duration > 45ms or active row lock queue > 5.
- **Root Cause Vectors**: Missing index, heavy transactional mutation contention, long-running analytic scan.
- **Remediation Steps**:
  1. Identify offending statement using query hash in ephemeral telemetry metrics.
  2. If an unbudgeted query is executing outside `transaction.atomic()`, enforce statement timeout: `SET statement_timeout = '5s'`.
  3. Divert non-critical dashboard read traffic to Redis cached projections.
  4. Flag offending endpoint for query budgeting review under ADR-056.

### 2.3 Playbook C: Redis Queue Lag & Task Backlog (> 200 tasks)
- **Primary Trigger**: Celery queue depth exceeding 200 pending messages.
- **Root Cause Vectors**: Worker memory exhaustion, stuck external provider calls, thread starvation.
- **Remediation Steps**:
  1. Inspect worker health beat telemetry (`WorkerHealthMetric`).
  2. Confirm external provider isolation (Outbox pattern): verify that external calls are strictly asynchronous.
  3. Scale Celery worker concurrency pool (`celery autoscale: 10,4`).
  4. Purge or reroute corrupted telemetry stream messages to Dead Letter Queue.

### 2.4 Playbook D: Telemetry Ingestion Collector Failure
- **Primary Trigger**: Ingestion endpoint HTTP 500 error rate > 1%.
- **Root Cause Vectors**: Malformed client payload flood, Redis stream memory limit reached (`MAXLEN`).
- **Remediation Steps**:
  1. Engage fail-closed rate limiter: throttle client event submission to 20 events / 5 min.
  2. Execute stream trimming: `XTRIM codesho:telemetry:stream MAXLEN ~ 25000`.
  3. If Redis stream is unavailable, switch ingestion endpoint to silent drop mode (HTTP 204) to ensure product user flows remain completely unblocked.
