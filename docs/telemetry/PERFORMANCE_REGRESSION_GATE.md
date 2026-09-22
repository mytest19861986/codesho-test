# Performance Regression Gate Specification

## 1. Objectives & CI Governance
The Performance Regression Gate blocks any deployment or branch promotion that violates latency baselines, query budgets, cache effectiveness, or bundle size constraints.

---

## 2. Hard Enforcement Thresholds

| Governance Dimension | Baseline Target | Regression Threshold (Hard Failure) | Verification Method |
|---|---|---|---|
| **API P95 Latency** | `<= 120ms` | `> 180ms` (Any regression > 25%) | Automated Synthetic Load Runner |
| **Database Query Count (Read)** | `<= 4 queries` | `> 4 queries` (N+1 strictly forbidden) | Django `assertNumQueries` Test Gate |
| **Database Query Count (Mutation)**| `<= 6 queries` | `> 6 queries` | Django `assertNumQueries` Test Gate |
| **Cache Hit Ratio (L1)** | `>= 90%` | `< 80%` | Redis Mocking / Hit Rate Validator |
| **Client Shared Bundle Size** | `<= 85 KB (gzip)` | `> 90 KB (gzip)` | `@next/bundle-analyzer` CI Artifact Gate |
| **Hydration Cost (4x CPU Throttling)**| `<= 200ms` | `> 350ms` | Headless Lighthouse CI Gate |
| **Cumulative Layout Shift (CLS)** | `<= 0.01` | `> 0.05` | Persian Typography Layout Shift Gate |

---

## 3. Regression Gate Circuit Breaker Flow

```mermaid
flowchart TD
    Build[CI Build Triggered] --> BundleCheck[1. Bundle Size Analyzer]
    BundleCheck -->|<= 85KB| QueryCheck[2. Query Budget Validation]
    BundleCheck -->|> 90KB| RejectBuild[Hard Fail: BUNDLE_BUDGET_EXCEEDED]
    
    QueryCheck -->|<= 4 Read / <= 6 Write| LatencyCheck[3. Synthetic Latency & Stress Run]
    QueryCheck -->|> Budget or N+1| RejectBuild2[Hard Fail: QUERY_BUDGET_EXCEEDED]
    
    LatencyCheck -->|P95 <= 180ms| CacheCheck[4. Cache Effectiveness Assertion]
    LatencyCheck -->|> 180ms| RejectBuild3[Hard Fail: LATENCY_REGRESSION_DETECTED]
    
    CacheCheck -->|Hit Ratio >= 80%| PassGate[Gate Certified: GA Promotion Allowed]
    CacheCheck -->|< 80%| RejectBuild4[Hard Fail: CACHE_EFFICIENCY_DEGRADED]
```
