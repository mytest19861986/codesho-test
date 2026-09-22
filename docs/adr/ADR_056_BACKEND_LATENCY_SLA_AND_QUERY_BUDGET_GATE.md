# ADR-056: Backend Latency SLA, Query Budgeting & Reliability Gate

## Context & Problem Statement
High database query counts (e.g. N+1 queries in nested role serializers), slow unindexed queries, and blocking transactional operations degrade backend throughput and compromise PostgreSQL connection pools. To guarantee high availability and sub-150ms P95 API responses under concurrent tenant load, strict architectural query budgeting and cache contracts must be codified.

## Decision
We enforce a mandatory **Backend Latency SLA & Query Budgeting Gate**:

1. **Query Budget per HTTP Request**:
   - `GET` Read requests: Maximum **4 queries** per transaction. N+1 queries strictly disallowed (`select_related` and `prefetch_related` enforced on all foreign keys/M2M).
   - Mutation requests (`POST`/`PUT`/`DELETE`): Maximum **6 queries** inside `transaction.atomic()`.
   - Maximum query execution duration: P95 **< 15ms**.
2. **Outbox Pattern & Worker Asynchrony**:
   - External notifications, telemetry batch flushes, and heavy recalculations must never execute inside the web request lifecycle or database transactions.
   - All asynchronous work must leverage transactional Outbox persistence and Celery workers inheriting `BaseTenantTask`.
3. **Redis Multi-Layer Caching**:
   - Cache-aside pattern for role dashboards and learning metadata with TTL <= 300s.
   - Cache key format: `codesho:tenant:{tenant_id}:{resource}:{id_hash}`.

## Consequences
- **Positive**:
  - Predictable database load with connection pool protection.
  - Zero out-of-band external network delays in user-facing endpoints.
  - Fail-closed tenant context guaranteed on all cached and asynchronous operations.
- **Negative**:
  - Complex nested queries require explicit query plan optimization and serializer pre-fetching.

## Compliance & Verification
- Enforced via Django test suite asserting `assertNumQueries(n)` across all public endpoints and Celery task isolation checks.
