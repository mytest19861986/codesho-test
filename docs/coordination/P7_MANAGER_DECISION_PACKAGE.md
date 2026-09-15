# P7 Manager Decision Package
## Phase 7 Real Pilot Manager Decision & Admission Preparation

This document defines the formal decision package delivered to the Human Manager for final determination (`GO` / `NO_GO` / `DEFER`).

### 1. Decision Header
- **Decision ID**: Cryptographically random UUIDv4.
- **Decision Version**: Monotonically increasing integer (starts at 1).
- **Tenant ID**: Bound target tenant identifier.
- **Scope Hash**: SHA-256 digest of approved scope envelope parameters.
- **Release Candidate ID**: Commit SHA of the audited platform build.
- **Activation Window**: Valid time interval (ISO 8601 start and end).
- **Token Expiry**: Maximum validity duration for the decision token.
- **Authorized Operators**: Explicit list of authorized operator public keys/identities.
- **Nonce**: Single-use cryptographic salt preventing token replay.
- **Audit Reference**: Permanent immutable audit transaction ID.

### 2. Available Outcomes
- **`GO`**: Authorizes deployment and activation within exact bound scope.
- **`NO_GO`**: Terminates candidate application permanently.
- **`DEFER`**: Holds decision pending specific additional evidence or audit resolution.
