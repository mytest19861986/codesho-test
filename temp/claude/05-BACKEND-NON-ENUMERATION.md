TASK_ID=SPRINT1-UI-LEARNING-DASHBOARD-READ-INTEGRATION-81B
BACKEND_EVIDENCE_SOURCE=Commander-authoritative prior Task80B review and tests

The backend boundary is non-enumerating: malformed, unknown, draft, archived, and cross-tenant parent identifiers resolve to the same not-found response shape rather than revealing whether a resource exists or its publication state.

Expected response shape: 404 {"code":"not_found"}.

The prior backend review reported explicit tests covering malformed, unknown, draft/archived, and cross-tenant parent cases. Claude must independently assess whether this evidence is sufficient for AC-15 and the related boundary criteria.
