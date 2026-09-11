# P3-MACRO-EPIC-26-28 DISCOVERY DOSSIER

**EPIC_ID**: `P3-MACRO-EPIC-26-28-ENTERPRISE-GOVERNANCE-DATA-LIFECYCLE-AND-PILOT-READINESS`  
**FA_TITLE**: حاکمیت سازمانی، چرخه عمر داده و مرکز آمادگی پایلوت  
**CANONICAL_DISCOVERY_HEAD**: `0e752bd560c6423e3faa8e26649946df6a693c93`  

---

## 1. Discovery Overview & Business Goals
As Codesho concludes the functional curriculum delivery and release operations, the platform requires enterprise administrative governance, deterministic data retention/disposition controls, and an authoritative pre-pilot technical assessment mechanism.

### Key Tenets
1. **Advisory Readiness**: The Readiness Center evaluates technical criteria but possesses `0` automated production deployment authority.
2. **Deterministic Data Retention**: Retention policies and automated disposition schedules must honor active statutory `LegalHold` records unconditionally.
3. **Privileged Access Control**: Self-granting, un-scoped admin privileges, and silent elevation are strictly blocked (`PRIVILEGE_SELF_GRANT: DENY`, `SILENT_PRIVILEGE_ESCALATION: DENY`).
4. **Immutability of Audit Trails**: `REVOKE UPDATE, DELETE` enforced on all governance audit trails.

---

## 2. Integrated Negative Matrix Specification (N1 - N36)
The implementation will be validated against a unified 36-point negative verification matrix:
- **N1 - N4**: Missing tenant context fails closed (`FAIL_CLOSED`), malformed tenant GUC rejection.
- **N5 - N8**: Cross-tenant isolation violation prevention across assignments, grants, retention policies, and legal holds.
- **N9 - N12**: Privileged self-grant prevention (`user_id == granted_by_id` blocked), un-scoped admin privilege rejection.
- **N13 - N16**: Expired access assignment rejection, revoked privilege denial, concurrent access review race handling.
- **N17 - N20**: Legal hold bypass attempt blocked, disposition of held records denied.
- **N21 - N24**: Retention policy override without multi-approver authorization denied, destructive deletion of audit logs blocked.
- **N25 - N28**: 21-key PII guard enforcement across policy reasons, finding summaries, and attestation notes.
- **N29 - N32**: Readiness evidence tampering attempt denied, non-authoritative boundary verification (readiness run cannot deploy code).
- **N33 - N36**: Anti-ranking query denial (`STUDENT_RANKING: 0`), idempotent review decision replay without double side-effects.

---

## 3. Fleet Review Plan
Upon commit and push of this discovery package:
1. **Qwen**: Validates authorization domains, separation of duties, access review FSM, and retention lifecycle.
2. **GLM (Database Security Reviewer)**: Audits PostgreSQL 17 FORCE RLS, composite foreign keys, and audit immutability.
3. **Gemini**: Audits Enterprise Control Center UX, BiDi/RTL isolation, contrast, and cognitive load.
