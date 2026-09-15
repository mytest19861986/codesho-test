# P7 Real Pilot Admission Architecture
## Phase 7 Real Pilot Manager Decision & Admission Preparation

This document outlines the admission architecture, security boundary definitions, and prerequisite evaluation engine for candidate pilot organizations.

### 1. 14-Prerequisite Admission Engine (Fail-Closed)
Candidate organizations must pass all 14 gates prior to entering `MANAGER_DECISION_REQUIRED`:
1. **Accredited Organizational Identity**: Valid registration number, charter, and physical verification.
2. **Infrastructure Qualification**: Dedicated isolated LAN, supported browser baselines, zero unmanaged endpoints.
3. **Operator Training Certification**: Up to 5 operators certified on Cockpit UI and emergency protocol.
4. **Parental Consent Framework**: 100% verified digital signatures for minor participants (Ages 13–19).
5. **Data Minimization Alignment**: Zero collection of national IDs, biometric, financial, or tracking telemetry.
6. **Multi-Tenant Database Enforcement**: `FORCE ROW LEVEL SECURITY` and `NOBYPASSRLS` active on tenant schema.
7. **Session Context Confinement**: Strict execution of `SET LOCAL "app.current_tenant" = %s` inside `transaction.atomic()`.
8. **Crypto-Shredding Key Generation**: Per-tenant cryptographic envelope key established for instant purge.
9. **DR & PITR Verification**: Successful recovery validation executed within preceding 7 days.
10. **Zero Open SEV1/SEV2 Incidents**: Clean operational health verified by monitoring telemetry.
11. **OpenAPI Schema Conformance**: Zero contract drift (`OPENAPI_SCHEMA_DRIFT: 0`).
12. **WCAG 2.2 AA Compliance**: Manager Decision Cockpit accessible, responsive, and Persian RTL/BiDi compliant.
13. **Mock Egress Boundary**: Telecom (SMS) and payment gateways hard-locked to synthetic sandbox adapters.
14. **Dual-Custody Separation of Duties**: Independent verification by security and operational leads.

### 2. Failure Handling
Any failed prerequisite halts the admission pipeline immediately and transitions the candidate to `DEFER` or `NO_GO`. No automated override is permitted.
