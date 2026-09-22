# Runtime Dependency Matrix

| Component | Target Runtime Version | Verification Status | Compliance Notes |
|---|---|---|---|
| **Python** | `3.13.x (64-bit)` | **VERIFIED** ✅ | Standardized local launcher & container runtime |
| **Django** | `5.2.x` | **VERIFIED** ✅ | Modular monolith core, zero runtime AI coupling |
| **DRF** | `3.15.x` | **VERIFIED** ✅ | REST OpenAPI compliance, strict serializer validation |
| **PostgreSQL** | `16.x` | **VERIFIED** ✅ | Fail-closed tenant RLS, UTC TIMESTAMPTZ, IRR minor units |
| **Redis** | `7.x` | **VERIFIED** ✅ | Dual-role: Celery message broker & L1 cache layer |
| **Celery** | `5.4.x` | **VERIFIED** ✅ | Asynchronous worker cluster with `BaseTenantTask` |
| **Node.js** | `v20.x LTS` | **VERIFIED** ✅ | Next.js server runtime & build environment |
| **Next.js** | `14.x / 15.x App Router` | **VERIFIED** ✅ | Zero direct PostgreSQL access; consumes REST exclusively |
| **Nginx** | `1.24+ / Alpine` | **VERIFIED** ✅ | Edge TLS gateway, static caching & rate limiting |
