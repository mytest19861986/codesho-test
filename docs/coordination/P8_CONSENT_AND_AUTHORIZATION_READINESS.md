# P8 Consent and Authorization Readiness

## 1. Consent Lifecycle Model
1. **Notice & Disclosure**: Prior to any student entry, guardian is presented with explicit, unbundled disclosures regarding the learning scope, duration, data classes processed, and voluntary participation nature.
2. **Affirmative Opt-In**: Requires verified adult guardian signature/confirmation. Implicit, pre-ticked, or inferred consent fails closed.
3. **Immutable Audit Receipt**: Each consent grant generates an append-only cryptographic receipt (`CONSENT-RECEIPT-<UUID>`) containing:
   - `guardian_user_id`
   - `student_user_id`
   - `tenant_id`
   - `consent_text_version`
   - `granted_at` (UTC TIMESTAMPTZ)
   - `expiry_at` (Maximum 365 days or pilot end)
4. **Immediate Withdrawal Flow**:
   - Guardian may revoke consent at any moment via single-click withdrawal.
   - Revocation triggers instant student de-provisioning, session invalidation, and data lock.
   - Generates immutable `CONSENT-REVOCATION-RECEIPT-<UUID>`.
