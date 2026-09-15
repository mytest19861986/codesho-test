# P7 Real Data Admission Decision Package
## Phase 7 Real Pilot Manager Decision & Admission Preparation

This document establishes the real data governance rules, cryptographic destruction mechanisms, and data classification boundaries.

### 1. Data Classification Scheme
- **CLASS A: Minor Identity Data**: Strictly synthetic during discovery/rehearsal; zero real child PII allowed.
- **CLASS B: Guardian Contact**: Mock/synthetic only; zero real SMS/telecom egress permitted.
- **CLASS C: Academic Records**: Course progression, non-competitive assessment logs. **Zero student ranking allowed**.
- **CLASS D: Operational Telemetry**: Tenant-scoped request latency, error logs (scrubbed of all PII).

### 2. Crypto-Shredding Engine
Each admitted tenant possesses a dedicated 256-bit AES key envelope stored in hardware security module / vault:
- **Deletion Protocol**: Upon pilot conclusion, offboarding, or parental revocation, the tenant key is cryptographically destroyed (`SHREDDED`).
- **Cryptographic Receipt**: An immutable, signed receipt containing the key ID, shred timestamp, operator ID, and zeroized hash is permanently recorded in the audit log.
- **Fail-Closed Verification**: Post-shredding database queries return ciphertext unrecoverable garbage.
