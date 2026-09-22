# Performance Baseline & Telemetry Domain Model

## 1. Domain Overview & Purpose
The Performance Baseline Architecture establishes system health and rendering efficiency standards without altering product runtime behavior, modifying database schemas, or infringing on student privacy.

This domain model adheres strictly to the **Zero-PII & Zero-Evaluation Invariant**:
- **System Observability Only**: Collects operational metrics (durations, memory, payload size, network latencies, failure codes).
- **Anti-Evaluation Guarantee**: Strictly prohibits collecting or projecting student performance ranks, comparative learning scores, completion speed scoring, or behavioral grading labels.

---

## 2. Core Entities & Schema Contracts

### 2.1 Frontend Performance Metric Contract (`FrontendPerfMetric`)
| Field | Type | Description | PII / Evaluation Check |
|---|---|---|---|
| `metric_id` | `UUIDv4` | Unique client event identifier | System generated, non-correlatable |
| `route_landmark` | `Enum` | Architectural route (`STUDENT_DASHBOARD`, `MENTOR_PANEL`, `PARENT_OBSERVATORY`, `ADMIN_GOVERNANCE`) | Role landmark, no child ID |
| `metric_name` | `Enum` | Metric key (`FCP`, `LCP`, `HYDRATION_MS`, `RENDER_COST_MS`, `BUNDLE_PARSE_MS`) | Technical measurement |
| `metric_value_ms`| `Float` | Measured value in milliseconds | Continuous technical telemetry |
| `viewport_bucket`| `Enum` | `MOBILE_390`, `TABLET_768`, `DESKTOP_1440`, `LARGE_1920` | Responsive layout bracket |
| `timestamp_utc` | `TIMESTAMPTZ` | Measurement capture time in UTC | Temporal tracking |

### 2.2 Backend Latency & Query Metric Contract (`BackendLatencyMetric`)
| Field | Type | Description | PII / Evaluation Check |
|---|---|---|---|
| `trace_id` | `UUIDv4` | Distributed tracing correlation ID | Ephemeral trace context |
| `endpoint_path` | `String` | Normalized route pattern (`/api/v1/learning/portfolio/`) | No parameterized identifiers |
| `http_method` | `Enum` | `GET`, `POST`, `PUT`, `DELETE` | Standard HTTP verb |
| `duration_ms` | `Float` | Server-side execution duration | Latency budget compliance |
| `db_query_count`| `Integer` | Number of executed SQL statements | Query budget tracking |
| `db_duration_ms`| `Float` | Aggregated database execution time | Query performance |
| `cache_hit` | `Boolean`| Redis cache hit or miss indicator | Cache efficiency |
| `status_code` | `Integer`| HTTP status response code | Fault classification |

### 2.3 Outbox & Asynchronous Worker Health Metric (`WorkerHealthMetric`)
| Field | Type | Description | Budget / Health Target |
|---|---|---|---|
| `queue_name` | `String` | Celery queue designation | `default`, `high_priority`, `telemetry` |
| `queue_lag_count` | `Integer` | Backlogged messages waiting for execution | `< 50 messages` |
| `task_duration_ms`| `Float` | Execution duration per asynchronous task | P95 `< 1200ms` |
| `outbox_unprocessed`| `Integer` | Pending outbox records awaiting worker sweep | `< 10 records` |
| `worker_concurrency`| `Integer` | Active worker thread capacity | Scaled dynamically |

---

## 3. Frontend Performance Budget Contract

```yaml
frontend_performance_budget:
  core_web_vitals:
    fcp_ms:
      target: 800
      max_allowed: 1200
    lcp_ms:
      target: 1500
      max_allowed: 2200
    cls:
      target: 0.01
      max_allowed: 0.05
    hydration_ms:
      target: 180
      max_allowed: 350
  bundle_weight_budget_kb:
    main_shared_bundle_gzip: 85
    vendor_chunk_gzip: 160
    route_chunk_max_gzip: 45
    css_total_gzip: 25
```

---

## 4. Backend Performance & Latency SLA

```yaml
backend_performance_sla:
  api_endpoints:
    read_p50_latency_ms: 45
    read_p95_latency_ms: 120
    write_p95_latency_ms: 250
  database_query_budget:
    max_queries_per_read_request: 4
    max_queries_per_mutation: 6
    p95_query_duration_ms: 12
    n_plus_one_tolerance: 0
  cache_strategy:
    redis_l1_target_hit_ratio: 0.92
    session_cache_ttl_seconds: 900
    portfolio_metadata_ttl_seconds: 300
```
