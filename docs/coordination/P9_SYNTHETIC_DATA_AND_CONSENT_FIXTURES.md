# P9 Synthetic Data and Consent Fixtures

## 1. Zero Real World Effect Mandate
Under no circumstances are real organizations, real students, real guardians, real contact details, or live SMS/payment gateways used in Phase 9. All entities are explicitly classified synthetic test fixtures.

## 2. Synthetic Dataset Definitions
### Tenant Fixture:
- `tenant_id`: `a0000000-0000-0000-0000-000000000001` (Synthetic Org Alpha)
- `name`: `مدرسه نمونه آزمایشی کانونیکال (صرفاً تستی)`
- `domain`: `alpha.test.codesho.local`
- `classification`: `SYNTHETIC_TEST_FIXTURE`

### Cross-Tenant Boundary Fixture:
- `tenant_id`: `b0000000-0000-0000-0000-000000000002` (Synthetic Org Beta)
- `name`: `مدرسه آزمایشی بتا (ایزولاسیون منفی)`
- `domain`: `beta.test.codesho.local`
- `classification`: `SYNTHETIC_TEST_FIXTURE`

### User Fixtures (Zero PII):
- `student_1`: UUID `11111111-1111-1111-1111-111111111111`, username `synth_student_01`, national_id `SYNTH_NAT_001`, mobile `+989000000001` (mock)
- `guardian_1`: UUID `22222222-2222-2222-2222-222222222222`, username `synth_guardian_01`, mobile `+989000000002` (mock)
- `mentor_1`: UUID `33333333-3333-3333-3333-333333333333`, username `synth_mentor_01`, mobile `+989000000003` (mock)

## 3. Synthetic Consent Fixtures
Consent records in P9 are strictly simulated to test gate logic without legal validity.
- `consent_id`: `c0000000-0000-0000-0000-000000000001`
- `tenant_id`: `a0000000-0000-0000-0000-000000000001`
- `student_id`: `11111111-1111-1111-1111-111111111111`
- `guardian_id`: `22222222-2222-2222-2222-222222222222`
- `purpose`: `SYNTHETIC_TRIAL_PARTICIPATION`
- `is_revoked`: `false`
- `classification`: `TEST_FIXTURE`

### Negative Consent Cases:
- Missing consent -> Rejects synthetic course enrollment.
- Revoked consent (`is_revoked = true`) -> Immediate suspension of synthetic access.
- Cross-tenant consent -> Ineffective in Tenant B (`404` / anti-enumeration).
- Unknown data class -> `FAIL_CLOSED`.
