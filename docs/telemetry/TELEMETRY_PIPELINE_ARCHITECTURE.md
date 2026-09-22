# Telemetry Pipeline Architecture Specification

## 1. Architectural Invariant & Zero-PII Guarantees
The CodeSho Telemetry Pipeline is engineered with a strict **fail-closed, zero-PII, zero-evaluation architecture**. It exists exclusively to track platform infrastructure reliability, query performance, and front-end rendering budgets without collecting personal identifying data or generating student evaluations.

```mermaid
flowchart TD
    subgraph Sources [1. Event Sources]
        ClientUI[Next.js Client Components]
        DjangoAPI[Django DRF REST Endpoints]
        CeleryWorker[Celery Background Workers]
        PostgreSQL[PostgreSQL Query Metrics]
    end

    subgraph Ingestion [2. Ingestion & Sanitization Gate]
        Collector[Edge / Ingestion API Endpoint]
        Sanitizer[PII & Evaluation Token Sanitizer]
        Validator[Schema Contract Validator]
    end

    subgraph Buffering [3. Buffering & Rate Limiting]
        RedisStream[(Redis Stream: codesho:telemetry:stream)]
        DeadLetter[(Quarantine / Dead Letter Queue)]
    end

    subgraph Storage [4. Storage & Metrics Aggregation]
        WorkerConsumer[Celery Stream Consumer]
        TSDB[(Time-Series DB / Prometheus TSDB)]
        ReliabilityDashboard[Admin Reliability Observatory]
    end

    Sources --> Collector
    Collector --> Sanitizer
    Sanitizer -->|Valid & Clean| Validator
    Sanitizer -->|Contains PII / Prohibited Tokens| DeadLetter
    Validator -->|Conforms to Schema| RedisStream
    Validator -->|Malformed Schema| DeadLetter
    RedisStream --> WorkerConsumer
    WorkerConsumer --> TSDB
    TSDB --> ReliabilityDashboard
```

---

## 2. Pipeline Components & Operational Contracts

### 2.1 Ingestion Collector
- **Endpoint**: `/api/v1/telemetry/events/` (HTTP POST).
- **Authentication**: Tenant-scoped ephemeral JWT or anonymous HMAC token.
- **Rate Limit**: 100 events per client session per 5-minute sliding window. Exceeded budgets are dropped silently (HTTP 204) to prevent DOS.

### 2.2 PII & Evaluation Token Sanitizer
Every event payload undergoes synchronous regex and dictionary filtering before entering the buffer:
1. **Masking Identifiers**: National IDs (10 digits), phone numbers (`09...`), email addresses, and student UUIDs are matched and purged.
2. **Evaluation Token Rejection**: Any key or payload containing prohibited semantic stems (`score`, `grade`, `rank`, `percentile`, `speed_rank`, `eval_label`) causes immediate dropping of the event to the quarantine sink.

### 2.3 Validation & Quarantine Sink
- Payloads must strictly parse against `TELEMETRY_EVENT_SCHEMA.md`.
- Failed payloads are logged to an ephemeral in-memory quarantine sink with stripped details for security monitoring.

### 2.4 Redis Stream Buffering
- Stream Key: `codesho:telemetry:stream`.
- Maximum length: `MAXLEN ~ 50000` entries to bound memory usage.
- Multi-worker consumer group ensures exactly-once aggregation processing.
