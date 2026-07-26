# Guardian and Recovery Boundary Decision Gate

Status: `EMPLOYER_DECISIONS_RECEIVED / LEGAL_AND_AUTHORITY_DESIGNATIONS_PENDING`
Date: 2026-07-26
Task: `SPRINT1-GUARDIAN-RECOVERY-DECISION-GATE-66D`

## Commander status update

Commander accepted Task66D on 2026-07-26. The gate is now
`EMPLOYER_DECISIONS_RECEIVED / LEGAL_AND_AUTHORITY_DESIGNATIONS_PENDING`.
The following authorities remain intentionally unassigned:

- Security Owner: `PENDING_EMPLOYER_DESIGNATION`
- Data Controller: `PENDING_EMPLOYER_LEGAL_DESIGNATION`
- Legal Approver: `LEGAL_PENDING / فعلاً تعیین نشده`

PR #5 remains draft and unmerged. This update records an authority gap only:
Guardian/Recovery implementation remains `NOT_AUTHORIZED` until an independent
Commander task names the authorities and provides a base SHA, exact allow-list,
acceptance criteria, and explicit implementation authority.

## Problem

Codesho has a `guardian` membership role but no approved definition of a
guardian-to-learner relationship, no consent or evidence policy, and no
approved recovery authority. Implementing Recovery before those boundaries
would risk making a guardian role an undocumented way to take over a learner
account, disclose whether an account exists, bypass forced passcode change, or
circumvent existing abuse controls.

This document is a decision package, not a policy approval or an
implementation contract. It does not authorize a model, migration, endpoint,
public UX, provider, notification, credential reset, or a guardian link.

## Analysis

### Conceptual relationship and lifecycle

A future relationship, if approved, should be a tenant-scoped, explicit
record between one active guardian membership and one active learner
membership. It is not implied by a shared tenant, a username, a staff role,
or a claimed family relationship. A possible lifecycle is `proposed`,
`evidence_pending`, `active`, `suspended`, `disputed`, `revoked`, and
`aged_out`; these names are descriptive only and are **not approved state
values**.

Every relationship operation must establish tenant context inside
`transaction.atomic()` before tenant queries, apply RLS, and fail closed when
membership, tenant, consent, or evidence cannot be established. A request
must disclose neither the existence of a learner nor the status of a guardian
relationship unless a later approved authorization rule permits it.

### Recovery authority boundary

Recovery ownership is unresolved. A guardian relationship must not, by
itself, grant a credential reset, account access, session access, data access,
or the ability to clear `must_change`. A future Recovery flow must remain a
distinct, narrowly authorized operation with independent abuse controls and
an immutable audit trail. It must not be a Login alternative, a way to bypass
the forced-passcode-change boundary, or a substitute for a valid credential.

If Recovery is approved, changing a credential must preserve the existing
security boundary: increment the credential/authentication epoch, invalidate
existing sessions, and require the approved forced-passcode-change behavior.
The exact eligibility, identity proof, rate limits,
challenge lifetime, and support escalation path are all open decisions.

### Consent, evidence, minors, and aging out

The employer and Legal must define who may consent, what proof establishes a
relationship, what happens when guardian and learner claims conflict, and
which jurisdictional rules apply. A minor reaching the relevant age threshold
must not silently retain, expand, or erase a relationship. Its transition,
re-consent, notification policy, and evidence retention are unresolved.

No raw relationship evidence, child data, identity documents, passcodes,
tokens, cookies, or provider payloads must be placed in ordinary audit
metadata. Any future evidence store needs a separately approved access,
encryption, retention, deletion, and legal-hold design.

### Revocation, disputes, replacement, and emergency suspension

Revocation must be one-way and should remove future authority immediately;
whether historical evidence remains immutable and for how long is a Legal
decision. A dispute or emergency suspension must fail closed: it may prevent
relationship or recovery use, but must not silently grant a replacement
guardian authority. Replacement needs its own evidence and consent path.
The employer must select accountable operational owners and a response-time
expectation before these operations are offered.

### Abuse resistance and audit design

Future requests must remain non-enumerating across tenant, learner,
relationship, and recovery states. They must use the established trusted
proxy/device extraction and Redis-backed abuse controls; service degradation
must fail closed rather than silently fall back to a weaker path. External
provider calls must remain outside database transactions.

If future audit events are approved, a minimal proposed taxonomy is
`GUARDIAN_LINK_CREATED`, `GUARDIAN_LINK_REVOKED`,
`GUARDIAN_LINK_ACCESS_DENIED`, `RECOVERY_REQUEST_REJECTED`,
`RECOVERY_CHALLENGE_ISSUED`, `RECOVERY_COMPLETED`, and
`RECOVERY_SUSPENDED`. Event names, reason codes, bounded metadata fields,
retention, and access roles are proposals only. Audit records must be
immutable, contain only approved opaque identifiers and reason codes, and
never contain credentials, challenge secrets, selectors, digests, cookie
values, raw IP addresses, raw device signals, or relationship evidence.

### Explicit exclusions

Notification, delivery providers, Signup, OAuth, Onboarding, public UI, and
public API/OpenAPI are outside this gate. A future notification capability
cannot be inferred from guardian or recovery approval and needs its own
provider, consent, template, retention, cost, and incident-ownership
decisions.

## Options

### Option A — defer all Guardian and Recovery work

Keep the current absence of guardian relationships and recovery flows until
all decisions are approved. This has the lowest immediate risk and cost, but
does not create a recovery route for users who cannot authenticate.

### Option B — approve a relationship-only foundation after decisions

Authorize a tenant-safe, consent-bound relationship lifecycle without
recovery, data access, notification, or public UI. This separates the
relationship boundary from credential control, but still requires Legal and
employer decisions before implementation.

### Option C — approve a complete Guardian-assisted Recovery flow

Authorize relationship and Recovery together. This could address recovery
needs sooner, but combines identity proof, child privacy, abuse protection,
credential/session security, support operations, and possible notification
dependencies. It has the highest decision and implementation risk.

## Recommendation

No option is approved by this document. The recommended decision sequence for
Employer and Legal to consider is: first decide the relationship, consent,
evidence, retention, revocation, dispute, replacement, and aging-out policy;
then consider **Option B** as the smallest separately authorized foundation;
only after its evidence and review should a distinct Recovery proposal be
considered. This ordering is a recommendation, not an authorization.

## Reason

Separating the relationship boundary from Recovery prevents a role label or
operational convenience from becoming a credential-control bypass. It keeps
tenant isolation, non-disclosure, immutable audit, existing credential epoch
handling, forced passcode change, and abuse controls as independent,
fail-closed gates.

## Decisions required from Employer and Legal

| ID | Decision and selectable response | Required owner |
| --- | --- | --- |
| GL-01 | Guardian relationship purpose: `A relationship-only`, `B recovery-eligible after separate approval`, or `C no guardian relationship`. | Employer + Legal |
| GL-02 | Eligible parties and role proof: `A named guardian and learner roles only`, `B approved alternative roles`, or `C defer`. | Employer + Legal |
| GL-03 | Consent model: `A dual consent`, `B guardian consent plus learner notice`, `C Legal-defined exception`, or `D defer`. | Legal (Employer accepts product impact) |
| GL-04 | Relationship evidence: `A no retained evidence beyond attestation`, `B approved document/evidence class`, or `C defer`; name the evidence controller. | Legal + Employer |
| GL-05 | Minor threshold and aging-out: select jurisdiction, age rule, re-consent action, and whether active links suspend pending re-consent. | Legal |
| GL-06 | Revocation/dispute/emergency suspension: select `A immediate fail-closed suspension`, `B operational review before suspension`, or `C defined emergency exception`; name the operator owner and SLA. | Employer + Legal |
| GL-07 | Guardian replacement: `A require a new independent relationship`, `B allow approved transfer evidence`, or `C prohibit`; specify dispute handling. | Legal + Employer |
| GL-08 | Retention/deletion/legal hold: select retention duration, deletion trigger, immutable-audit minimum, evidence deletion rules, and data controller. | Legal |
| GL-09 | Recovery authority: `A no guardian-assisted recovery`, `B guardian may initiate only`, `C guardian may approve after independent proof`, or `D other approved contract`. | Employer + Legal |
| GL-10 | Credential/session result after approved recovery: select epoch/session invalidation, forced-change rule, support override policy, and challenge proof/rate-limit owner. | Employer + Security owner |
| GL-11 | Non-disclosure and abuse behavior: approve neutral outcomes, tenant/RLS fail-closed behavior, Redis outage failure, and escalation path. | Security owner + Employer |
| GL-12 | Audit taxonomy and access: approve event names, reason codes, bounded metadata, retention, and audit-reader roles; or defer. | Security owner + Legal |
| GL-13 | Notification boundary: `A remain absent`, `B separate future decision package`, or `C other`; no provider selection occurs here. | Employer + Legal |

An answer is not complete unless each selected option names the decision owner
and, where required, jurisdiction, operational owner, and effective date.
Any approval of GL-09 is void until GL-05 is resolved: Recovery authority
cannot be exercised over a relationship whose minor and aging-out status is
undefined.

## Proposed smallest implementation slice after approval

`PROPOSED_NOT_AUTHORIZED`: a Guardian Relationship Foundation only. It would
create no recovery, credential reset, notification, provider integration,
public route, UI, or data-access grant. Subject to a new Commander task and
review, its possible allow-list is:

1. `backend/modules/platform_tenant/models.py`
2. `backend/modules/platform_tenant/guardian_links.py` (new)
3. `backend/modules/platform_tenant/migrations/0003_guardian_link.py` (new)
4. `backend/modules/platform_event/models.py`
5. `backend/modules/platform_event/security_audit.py`
6. `backend/modules/platform_event/migrations/0010_guardian_link_events.py` (new, only if required)
7. `backend/tests/test_guardian_links.py` (new)
8. `backend/tests/test_guardian_links_postgres.py` (new)
9. `backend/tests/test_security_audit.py`
10. `docs/data-dictionary.md`
11. `docs/sprint-zero/threat-model.md`

The two proposed documentation files would be updated only after GL-01
through GL-13 are resolved, to reflect approved definitions; they cannot
pre-justify implementation.

This proposed list is not an authorization to edit any file. A future task
must supply an independent base SHA, exact contract, approved policy answers,
review gate, and explicit implementation authority.
