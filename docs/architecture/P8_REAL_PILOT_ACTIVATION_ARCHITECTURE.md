# P8 Real Pilot Activation Architecture

## 1. Architectural Principles
1. **Separation of Concerns**: Complete decoupling of Decision-Making (Human Manager) from Technical Verification (Commander & Fleet) and Execution (Controlled Operators).
2. **Deterministic Cryptographic Binding**: Every activation request is bound to:
   - Specific Tenant UUID
   - Exact Candidate Organization UUID
   - Canonical Release Candidate SHA-256
   - Deterministic Scope Hash
   - Authorized Operator User ID
   - Single-use Nonce & Activation Window
3. **Fail-Closed Gateways**: Any missing attribute, timestamp skew (>300s), signature mismatch, or unhandled exception immediately halts activation.
4. **Append-Only Immutable Ledger**: Decisions, evidence snapshots, and revocation receipts are written to append-only PostgreSQL tables with RLS and restrictive triggers.

## 2. Component Diagram & Authority Flow
```
[Human Manager Cockpit]
         │ (GO / NO_GO / DEFER Decision)
         ▼
[Manager Decision Ledger] ───(Snapshots)───► [DecisionEvidenceSnapshot]
         │
         │ (Issues Cryptographically Signed Token)
         ▼
[Synthetic / Controlled Activation Token]
         │
         ▼
[Activation Gateway Verification Engine]
   ├─ Verify Human Authority (is_human_manager=True)
   ├─ Verify Self-Approval Prohibition (creator_id != manager_user_id)
   ├─ Verify Scope Hash & Release Candidate Match
   ├─ Verify Evidence Freshness (<24h, zero STALE/EXPIRED)
   ├─ Verify Activation Window & Single-Use Nonce
   └─ Verify Zero Open Hard Stops
         │
   [PASS]│
         ▼
[Bounded Tenant Admission Execution] ───► [Immutable Security Audit Log]
```

## 3. Threat Mitigation
- **Token Replay / Duplication**: Nonce uniqueness constraints and immediate consumption flag.
- **Cross-Tenant Leakage**: PostgreSQL Row-Level Security (RLS) enforced across all admission and decision models.
- **Authority Resurrection**: Revocation updates cascade to all child tokens, marking them terminal.
