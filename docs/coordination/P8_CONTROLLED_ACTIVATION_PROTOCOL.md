# P8 Controlled Activation Protocol

## Sequential Verification & Execution Flow
Every activation request must strictly traverse these 12 sequential gates in fail-closed order:

```text
Step 01: [Manager GO Verification] -> Verify active ManagerDecision with status=GO and is_human_manager=True
Step 02: [Self-Approval Check]    -> Assert creator_id != manager_user_id
Step 03: [Decision Freshness]     -> Assert decision_timestamp is within 24 hours (not STALE)
Step 04: [Hard-Stops Check]       -> Assert zero open blockers or failing hard-stop checks
Step 05: [Scope Hash Matching]    -> compute_canonical_scope_hash() == approved_scope_hash
Step 06: [Release Matching]       -> submitted_release_candidate_sha == approved_rc_sha
Step 07: [Evidence Freshness]     -> Verify all DecisionEvidenceSnapshots are ACTIVE (<24h)
Step 08: [Activation Window]      -> current_time between activation_window_start and activation_window_end
Step 09: [Operator Authorization] -> current_operator_id == authorized_operator_id
Step 10: [Single-Use Nonce]       -> Nonce is unique and unconsumed in token store
Step 11: [Token Consumption]      -> Atomically mark token is_consumed=True, record consumed_at
Step 12: [Audit Event Emission]   -> Write immutable REAL_PILOT_ACTIVATED audit row
```
Any failure along Steps 01–12 aborts execution immediately with zero state modification.
