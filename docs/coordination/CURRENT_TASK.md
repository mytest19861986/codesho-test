# Current Task: P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME

## Phase 7 Real Pilot Manager Decision & Admission Preparation Runtime — 2026-09-15

- Status: `RUNTIME_ACTIVE_IMPLEMENTATION`
- Task ID: `P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME`
- Authority: `COMMANDER_P7_RUNTIME_UNLOCK: GRANTED`
- Discovery Closeout: `COMMANDER_P7_DISCOVERY_FINAL_ACCEPTANCE: GRANTED`
- Program Mode: `MACRO_FAST_ENTERPRISE`
- Base Discovery HEAD: `555203752b52f7c27039d4914b72e9fad6d163aa`
- Current Branch: `codex/phase3-product-platform-foundation`

### Triple Discovery Fleet Consensus Baseline:
- Qwen Discovery Review: `PASS / 0 BLOCKERS` (`docs/coordination/P7_FLEET_QWEN_DISCOVERY.md`)
- GLM Discovery Review: `PASS / 0 BLOCKERS` (`docs/coordination/P7_FLEET_GLM_DISCOVERY.md`)
- Gemini Discovery Review: `PASS / 0 BLOCKERS` (`docs/coordination/P7_FLEET_GEMINI_DISCOVERY.md`)
- Discovery Consensus Document: `docs/coordination/P7_FLEET_CONSENSUS_DISCOVERY.md`

### Runtime Workstreams & Scope (Synthetic & Control Plane Only):
1. **P7-RT1: MANAGER_DECISION_LEDGER_AND_AUTHORITY_RUNTIME**
   - Immutable, versioned decision ledger (`ManagerDecisionLedger`) with FSM:
     `DRAFT` -> `EVIDENCE_COLLECTION` -> `DUE_DILIGENCE_REVIEW` -> `SECURITY_REVIEW` -> `PRIVACY_REVIEW` -> `OPERATIONAL_REVIEW` -> `SCOPE_REVIEW` -> `GO_NO_GO_READY` -> `MANAGER_DECISION_REQUIRED` -> `GO` | `NO_GO` | `DEFER` -> `REVOKED` | `EXPIRED`
   - Invariants: `HUMAN_MANAGER_ONLY` issuer, `SELF_APPROVAL: DENY`, `AGENT_MANAGER_EMULATION: DENY`, `SUPERSEDED_DECISION_REUSE: DENY`, `DECISION_VERSION_ROLLBACK: DENY`.
2. **P7-RT2: EVIDENCE_SNAPSHOT_AND_STALENESS_RUNTIME**
   - Immutable evidence snapshots binding 12 domains (`SECURITY_REVIEW`, `PRIVACY_REVIEW`, `LEGAL_REVIEW`, `BACKUP_RESTORE`, `PITR`, `DATABASE_QUALIFICATION`, `ACCESS_REVIEW`, `RELEASE_CANDIDATE`, `OBSERVABILITY`, `INCIDENT_READINESS`, `SUPPORT_READINESS`, `CANDIDATE_DUE_DILIGENCE`).
   - Freshness lifecycle: `FRESH`, `STALE`, `EXPIRED`, `SUPERSEDED`. Automatic invalidation upon material changes.
3. **P7-RT3: SCOPE_RELEASE_AND_ACTIVATION_BINDING_RUNTIME**
   - Deterministic canonical serialization with cryptographic SHA-256 `scope_hash` binding tenant, capacity limits, features, data classes, channels, release candidate, activation window, and exit policy.
   - Synthetic activation token runtime: single-use, non-transferable, non-replayable, tenant-bound, scope-bound, release-bound, time-bound, revocable, audited.
4. **P7-RT4: EXCEPTION_REVOCATION_AND_EXIT_RUNTIME**
   - Dual-custody exception lifecycle: `DRAFT` -> `REQUESTED` -> `REVIEW` -> `APPROVED` | `REJECTED` -> `EXPIRED` | `REVOKED`.
   - `NON_WAIVABLE_GATE_EXCEPTION: DENY` (Hard stops cannot be waived).
   - Manager revocation and exit control plane: disable access, revoke tokens, crypto-shredding per tenant subject with non-repudiable shred receipt.
5. **P7-RT5: MANAGER_GO_NO_GO_COCKPIT_RUNTIME**
   - Next.js Cockpit UI in `/admin/governance`: tri-state decision (`GO` / `NO_GO` / `DEFER`), hard stop prominence, intentional 2-step destructive friction, WCAG 2.2 AA ($\ge 44\text{px}$, contrast $>4.5:1$), BiDi/RTL isolation, zero student ranking.
   - Antigravity visual qualification on 1440x900 and 390x844 with 0 console/network errors.
6. **P7-RT6: SYNTHETIC_DECISION_REHEARSAL_AND_NEGATIVE_QUALIFICATION**
   - 40 Negative Matrix Tests (`N7-01` .. `N7-40`) at 100% PASS.
   - 20 Synthetic Decision Rehearsals (`P7_R1` .. `P7_R20`) at 100% PASS.
   - Mandatory fulfillment of GLM Runtime Gates `F1` - `F6`.
   - Full backend regression pass and PostgreSQL 17.10 runtime qualification.

### Strictly Preserved Invariants & Manager Boundaries:
- `REAL_PILOT`: LOCKED (NOT_AUTHORIZED)
- `REAL_DATA`: LOCKED (`REAL_CHILD_DATA`: 0, `REAL_GUARDIAN_DATA`: 0, `REAL_PII`: 0)
- `REAL_ORGANIZATION_ONBOARDING`: NOT_AUTHORIZED
- `REAL_CONSENT_ACTIVATION`: NOT_AUTHORIZED
- `REAL_SMS_EMAIL`: NOT_AUTHORIZED
- `REAL_PAYMENT`: NOT_AUTHORIZED
- `PRODUCTION`: LOCKED
- `PRODUCTION_DEPLOY`: NOT_AUTHORIZED
- `PRODUCTION_CREDENTIALS`: 0
- `MERGE_TO_MAIN`: LOCKED_FOR_MANAGER
- `ANTI_RANKING`: 0 (Absolute prohibition of student ranking/leaderboards)
- `RAW_AGENT_RESPONSES_IN_REPO`: 0
- `P7_RUNTIME_DATA_MODE`: SYNTHETIC_ONLY
