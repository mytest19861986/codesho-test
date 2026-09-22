# Runtime Safety Contract

## 1. Permitted vs. Forbidden Operational Actions

| Domain | Strictly Permitted Actions (Authorized ✅) | Strictly Forbidden Actions (Hard-Locked ❌) |
|---|---|---|
| **Documentation & Auditing**| Topography mapping, dependency reviews, configuration inspection | Altering architectural directives without Commander approval |
| **Validation & Testing** | Synthetic testing, mock connection tests, isolated harnesses | Real user data injection, production environment execution |
| **Database Boundary** | Connection pooling verification, read isolation checks | Executing `makemigrations` or `migrate`, schema mutations |
| **Configuration** | Inspecting `.env.example`, validating non-secret environment defaults | Committing secrets, tokens, API keys, passwords, or PII |
| **Pedagogy & Telemetry** | Observing system health, latency, query budgets | Computing student grades, competitive ranks, capability percentiles |
| **Release & Deployment** | Staging qualification, release artifact packaging | Direct promotion or push to protected production remotes |

---

## 2. Invariant Commitments
1. `CODE_CHANGE: 0` in production runtime.
2. `DATABASE_MIGRATION: 0` (Schema is 100% frozen).
3. `REAL_USER_TRAFFIC: 0` (All validation relies on synthetic harnesses).
4. `SECRET_EXPOSURE: 0` (Zero credentials logged or pushed).
