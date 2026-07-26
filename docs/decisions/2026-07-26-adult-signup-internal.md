# Adult signup internal-only implementation decision

```text
DECISION_ID: SPRINT1-ADULT-SIGNUP-IMPLEMENT-67A
DATE: 2026-07-26
STATUS: EMPLOYER_APPROVED_FOR_DEVELOPMENT_AND_INTERNAL_TEST
DATA_CONTROLLER: EMPLOYER_NATURAL_PERSON_TEMPORARY
LEGAL_APPROVAL: PENDING_BEFORE_ANY_REAL_USER
REAL_USERS: PROHIBITED
MERGE: NOT_AUTHORIZED
DEPLOYMENT: NOT_AUTHORIZED
```

## Decision

Codesho may implement an internal-only adult age-attestation foundation using
synthetic test subjects. The only age claim is an explicit self-attestation
that the subject is at least 18. Date of birth, birth year, numeric age,
identity evidence, national identifier, Guardian data, and free-text age data
must not be accepted, logged, or persisted.

This implementation supersedes the earlier proposal to collect a complete
Jalali birth date. It does not create accounts or enable the public `/signup`
route. A future user-creation workflow must be authorized independently and
must consume a valid attestation without weakening this boundary.

## Environment boundary

The mode is `disabled` by default. `internal_test` is available only through
development settings, and production settings fail closed if any non-disabled
mode is configured. The request is tenant-routed, but the subject identifier is
an opaque synthetic UUID with no relation to a real person.

## Evidence and retention boundary

The domain record stores only tenant UUID, synthetic subject UUID, the constant
adult-attested status, server-approved policy version, allow-listed source,
UTC timestamp, and opaque audit event UUID. The accepted event and the
supported explicit rejection are appended to the immutable security audit
ledger. Raw payloads and raw IP addresses are never evidence fields.

Valid request attempts are rate-limited by HMAC-anonymous synthetic-subject
and client-IP dimensions in Redis. Raw identifiers and raw IP addresses are
not Redis keys, and Redis failure blocks the endpoint.

## Non-authority

This decision does not authorize real users, Alpha, public release, Guardian or
Recovery work, frontend activation, Merge, Deployment, or promotion to the
protected `codesho` repository.
