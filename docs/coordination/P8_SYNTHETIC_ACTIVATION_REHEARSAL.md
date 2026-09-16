# P8 Synthetic Activation Rehearsal Protocol

## 1. Objective
To execute a 100% synthetic end-to-end dry run of the P8 Controlled Activation Protocol and Admission Cockpit using mock tenant UUIDs, synthetic student records, and isolated test fixtures prior to presenting any package to the Human Manager.

## 2. Rehearsal Environment Boundaries
- **DATABASE**: Isolated test schema / staging database container.
- **DATA**: 100% synthetic UUIDs, mock organizations, and fake child profiles (`synthetic_student_01` .. `synthetic_student_50`).
- **SECRETS**: Mock signatures and ephemeral test keys.
- **EXTERNAL SERVICES**: SMS, Email, and Payment drivers routed strictly to Null/Mock handlers.

## 3. Execution Checklist
1. Pre-seed synthetic candidate organization and 50 mock student accounts.
2. Generate synthetic `DecisionEvidenceSnapshot` set with valid hashes.
3. Simulate Human Manager `GO` determination in `ManagerDecisionLedger`.
4. Issue `SyntheticActivationToken` tied to test scope hash.
5. Invoke `ActivationGateway.verify_and_consume()` and assert:
   - Token state transitions to consumed.
   - Admission audit row is immutably written.
   - Zero errors across console and network logs.
6. Trigger simulated emergency kill-switch and assert immediate revocation.
7. Execute crypto-shredding rehearsal and assert receipt emission and student record deletion.
