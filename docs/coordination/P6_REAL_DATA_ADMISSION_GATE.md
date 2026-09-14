# P6_REAL_DATA_ADMISSION_GATE.md - Codesho / SSD

**TASK**: `P6-CONTROLLED-REAL-PILOT-READINESS-DISCOVERY`
**STATUS**: `LOCKED_SPECIFICATION`
**INVARIANT**: `CURRENT_REAL_DATA_MODE: SYNTHETIC_ONLY` | `REAL_PII: 0`

---

## 1. Objective & Philosophy
The Real Data Admission Gate establishes the impenetrable barrier between synthetic test execution and the introduction of any real human identity into Codesho. No real user record (parent, educator, child) may ever enter PostgreSQL without satisfying 100% of the preconditions outlined herein.

---

## 2. 14 Immutable Pre-Admission Gate Domains
Before the first real record is authorized, all fourteen domains must independently achieve a verified `PASS` status:

1. **MANAGER_AUTHORIZATION**:
   - Cryptographically verifiable authorization recorded in audit trail by Human Manager.
2. **LEGAL_PRIVACY_REVIEW**:
   - Written compliance review confirming alignment with national and international child privacy standards.
3. **CONSENT_OR_LEGAL_BASIS**:
   - Verified digital signature or tokenized consent artifact from parent/guardian for minor learners.
4. **DATA_MINIMIZATION**:
   - Strict schema constraint verification: zero optional sensitive demographics, zero free-text PII storage.
5. **TENANT_AUTHORIZATION**:
   - Signed institutional agreement establishing organizational tenancy and data controller / processor terms.
6. **ACCESS_CONTROL**:
   - Least privilege verification: no single actor possesses both administrative and audit bypass privileges.
7. **RETENTION**:
   - Time-to-live policies configured; automated expiration dates assigned to all temporary session data.
8. **DELETION**:
   - Right-to-be-forgotten / cryptographic erasure procedures verified through end-to-end rehearsal.
9. **OFFBOARDING**:
   - Automated full tenant data export and cryptographic purge pipeline verified.
10. **INCIDENT_RESPONSE**:
    - Dedicated Incident Commander on call with emergency suspension capability (< 5 minutes response time).
11. **SUPPORT_READINESS**:
    - Designated Support Owner and triage queue configured with privacy-safe ticketing.
12. **AUDITABILITY**:
    - Tamper-evident append-only audit log recording all administrative and data access operations.
13. **SECURITY_TESTING**:
    - Automated vulnerability scan and static code analysis passing with 0 critical or high findings.
14. **ANTI_RANKING_VALIDATION**:
    - Strict verification that no leaderboard, public score ranking, or comparative child performance metrics exist in codebase or UI.

---

## 3. Child & Minor Protection Specific Gate
For any organization enrolling learners under age 18:
- **Direct PII Prohibition**: Real child phone numbers, email addresses, or national identification numbers are strictly prohibited from storage.
- **Pseudonymized Identifiers**: Learners are represented internally by immutable UUIDs and localized, non-PII display handles.
- **Guardian Relationship Assertion**: Direct multi-factor guardian verification required prior to learner account activation.
- **Revocation Trigger**: Immediate, automated account de-activation upon parental consent withdrawal.
