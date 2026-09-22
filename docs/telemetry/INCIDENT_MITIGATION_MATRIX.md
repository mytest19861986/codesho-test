# Incident Mitigation Matrix

| Incident Vector | Detection Mechanism | Containment Protocol | Recovery & Normalization Action |
|---|---|---|---|
| **API Latency Spike (P95 > 250ms)** | Telemetry Stream Aggregator (`api_p95_ms`) | Enforce connection pool limits; divert read endpoints to cached projections | Pre-warm Redis dashboard cache; scale web server concurrency |
| **Database Lock & Query Spikes** | Postgres Query Hash Watcher (`db_query_duration_ms > 45ms`) | Kill long-running statements (`statement_timeout = 5s`); isolate offending transaction | Enforce `select_related` on query plan; add missing index; verify ADR-056 compliance |
| **Redis Queue Backlog (> 200 tasks)** | Celery Health Inspector (`queue_lag_count`) | Throttle background non-critical batch jobs; isolate queue namespaces | Scale worker consumer threads (`celery autoscale: 10,4`); sweep dead-letter tasks |
| **Worker Heartbeat Failure (> 30s)** | Worker Heartbeat Telemetry Watchdog | Mark worker node degraded; reroute tasks to healthy worker pods | Restart worker process; verify Redis broker connection health |
| **Telemetry Ingestion Corruption** | Ingestion Gate Error Rate (`error_code: TELEM_CORRUPT`) | Engage fail-closed silent dropping (HTTP 204); clamp per-IP rate limits | Execute stream trim (`XTRIM`); purge malformed payloads to quarantine sink |
| **PII / Evaluation Token Leak Attempt** | Sanitizer Rejection Gate (`INVALID_TOKEN_REJECTED`) | Drop event immediately with zero reflection to client; log ephemeral security alert | Audit client telemetry dispatch code; verify zero PII persistence |
