# Deployment, Observability and DR Baseline

## Approved target

- Ubuntu 24.04, 2 vCPU, 4 GB RAM
- Monthly ceiling: 5 million toman
- Docker Compose and Nginx; no Kubernetes initially
- Managed PostgreSQL/Object Storage preferred when the selected provider fits budget

## Capacity decision

On 4 GB RAM, application services and self-hosted PostgreSQL can run for alpha,
but a full Prometheus/Grafana/Loki stack competes with production workload.
Start with provider host metrics, container health checks, JSON logs with rotation,
external uptime checks and an error tracker. Reassess dedicated metrics storage
after measured demand. Redis is capped at 256 MB and uses `noeviction` to avoid
silent job loss.

If self-hosted PostgreSQL is selected, WAL archiving and logical-backup I/O must
be included in the measured 4 GB / 2 vCPU resource budget; a dedicated metrics
stack remains deferred until that budget is demonstrated.

## Recovery objectives

- Target RPO: 15 minutes, conditional on provider capabilities and budget.
- Target RTO: 4 hours.
- PostgreSQL: managed point-in-time recovery preferred; otherwise encrypted
  incremental/WAL archive plus daily logical backup stored off-host.
- Object Storage: versioning and lifecycle policy; master files are never kept
  only on the application VPS.
- Restore drill: restore into an isolated database, run migrations/checks and
  record measured RPO/RTO. A backup without a successful restore drill is not
  accepted for production.

## Production gate

Provider selection, encrypted off-host destination, alert recipient, release
owner, DNS names, a backup-I/O resource budget for self-hosted PostgreSQL (if
chosen), and a successful restore drill must be recorded before launch.

## PostgreSQL deployment roles

Migrations run only with `codesho_migrator`; the web process, Celery worker
and Celery beat use only `codesho_runtime`. The runtime role has no superuser,
RLS-bypass, role/database creation or `CREATE`-on-application-schema power.
Deployments must run the migration step to completion before starting runtime
services. Restore drills preserve migrator object ownership and runtime grants;
they are rejected if either condition is missing.

The dedicated `audit` schema is part of the restore contract. Its immutable
credential-security table must remain owned by `codesho_migrator`; the runtime
role must have only schema `USAGE` and table `INSERT`, and no `SELECT` access.
Restore verification rejects a backup when this ownership or insert-only grant
is missing.
