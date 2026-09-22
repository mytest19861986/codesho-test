# Telemetry Event Schema Contract Specification

## 1. Schema Versioning & Strict Allowed / Prohibited Rules

- **Schema Version**: `1.0.0`
- **Schema Strictness**: `additionalProperties: false` (Any unexpected field is rejected immediately).

---

## 2. Event Types & Allowed Payloads

### 2.1 Allowed Event Types
1. `PLATFORM_LATENCY_OBSERVED`: Frontend and backend duration observations.
2. `INFRASTRUCTURE_HEALTH_BEAT`: PostgreSQL, Redis, and Celery operational state.
3. `QUEUE_DEPTH_REPORT`: Celery task backlog and outbox sweep telemetry.
4. `CLIENT_PERF_SAMPLE`: Core Web Vitals (FCP, LCP, CLS, Hydration).

### 2.2 Prohibited Fields & Semantic Tokens
The following tokens must never exist in any key, value, tag, or context:
- `score`, `scoring`, `student_score`
- `rank`, `ranking`, `class_rank`
- `grade`, `grading`, `mark`
- `iq`, `capability`, `slow_learner`, `fast_learner`
- `user_national_id`, `mobile_number`, `student_real_name`

---

## 3. Canonical JSON Schema Definitions

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CodeShoTelemetryEvent",
  "type": "object",
  "required": ["event_id", "schema_version", "event_type", "timestamp_utc", "tenant_hash", "payload"],
  "additionalProperties": false,
  "properties": {
    "event_id": {
      "type": "string",
      "format": "uuid"
    },
    "schema_version": {
      "type": "string",
      "enum": ["1.0.0"]
    },
    "event_type": {
      "type": "string",
      "enum": [
        "PLATFORM_LATENCY_OBSERVED",
        "INFRASTRUCTURE_HEALTH_BEAT",
        "QUEUE_DEPTH_REPORT",
        "CLIENT_PERF_SAMPLE"
      ]
    },
    "timestamp_utc": {
      "type": "string",
      "format": "date-time"
    },
    "tenant_hash": {
      "type": "string",
      "pattern": "^[a-f0-9]{64}$"
    },
    "payload": {
      "type": "object",
      "required": ["metric_name", "metric_value"],
      "additionalProperties": false,
      "properties": {
        "metric_name": {
          "type": "string",
          "enum": [
            "fcp_ms", "lcp_ms", "cls_ratio", "hydration_ms",
            "api_p95_ms", "db_query_duration_ms", "db_query_count",
            "redis_hit_ratio", "celery_queue_lag", "outbox_pending_count"
          ]
        },
        "metric_value": {
          "type": "number",
          "minimum": 0
        },
        "role_context": {
          "type": "string",
          "enum": ["STUDENT", "MENTOR", "PARENT", "ADMIN"]
        },
        "route_canonical": {
          "type": "string",
          "pattern": "^/[a-zA-Z0-9_\\-/:]*$"
        },
        "error_code": {
          "type": "string",
          "pattern": "^[A-Z0-9_]{3,32}$"
        }
      }
    }
  }
}
```
