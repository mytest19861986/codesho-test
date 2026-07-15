# Sprint Zero Threat Model

## Passcode credential foundation (S1-002)

Passcodes are accepted only as six ASCII digits, HMACed with a versioned
server-side Pepper, and then hashed with Argon2id. Raw passcodes and HMAC
digests are never persisted or logged. Production requires an active Pepper ID
and Base64 Pepper values decoding to at least 32 bytes; rotation is detected by
the credential's Pepper ID. Login, rate limiting, recovery and public APIs are
out of scope until separately approved.

Status: baseline; update when payment, SMS and video providers are selected.

## Assets and trust boundaries

- Teen identity, guardian links, consent and aging-out state
- Tenant memberships, roles and learning records
- Session cookies, CSRF tokens and staff/admin privileges
- Payment ledger and provider callbacks
- Uploaded assignments, master video files and transcripts
- Browser → Nginx → Django/Next.js boundary
- Django/Celery → PostgreSQL/Redis/Object Storage boundary
- External provider callbacks and background jobs

## P0 threats and controls

| Threat | Primary controls | Verification |
|---|---|---|
| Cross-tenant data access | App authorization + PostgreSQL RLS, fail closed without context | PostgreSQL RLS and connection-reuse tests |
| Tenant header/host spoofing | Candidate slug is untrusted; membership checked only after DB context | Middleware tests |
| Context leak through pooling/jobs | `SET LOCAL` inside atomic transaction; `BaseTenantTask`; statement pooling forbidden | Reuse test + task tests |
| Session theft/CSRF | HttpOnly, Secure, SameSite=Lax, CSRF middleware, same-origin proxy | Django deploy check + E2E before staging |
| Teen passcode spraying | Account/IP/device limits, global detection, progressive delay, first-login rotation | Required before Identity Sprint |
| Privileged admin misuse | Least privilege, MFA for staff, immutable audit trail | Required before staging |
| Malicious upload | Size/type checks, magic-byte validation, object quarantine, malware scan, signed downloads from a cookieless origin separate from the app | Required before upload feature |
| Forged payment callback | Signature verification, replay protection, idempotency key, ledger reconciliation | Required before payment integration |
| Data loss/ransomware | Encrypted off-host backups, object versioning, restore drills | Restore drill before production |

## Residual risks / open decisions

- Provider-specific callback and storage threats remain open until providers are selected.
- Final teen passcode entropy and UX must be approved before Identity implementation.
- Guardian notification for anomalous teen sign-in or lockout requires employer approval before Identity implementation.
- Legal rules for retention, consent and aging-out require counsel before paid production.
- Session recording is disabled in MVP by default.

### S1-003 abuse-control deployment note

The internal passcode abuse engine uses one atomic Redis Lua script across the
account, account-device, IP, device and global keys. Redis must therefore run as
a single-node service (the Compose/CI Redis service); Redis Cluster is not an
approved topology for this foundation unless the key design is changed to use
hash tags and re-reviewed. Redis or malformed-script failures fail closed.
