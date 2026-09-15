# P7 Real Pilot Write Manifest
## Phase 7 Real Pilot Manager Decision & Admission Preparation

This document specifies the locked write manifest for Phase 7 Discovery and specifies the strict path boundaries.

### 1. Classification & Path Manifest

| Path | Classification | In-Scope Reviewer | Mutation Allowed |
| :--- | :--- | :--- | :--- |
| `docs/coordination/P7_REAL_PILOT_DISCOVERY_SPECIFICATION.md` | CREATE | Qwen, GLM, Gemini | YES (Discovery Document) |
| `docs/coordination/P7_REAL_PILOT_MANAGER_DECISION_DISCOVERY_DOSSIER.md` | CREATE | Qwen, GLM, Gemini | YES (Discovery Document) |
| `docs/coordination/P7_REAL_PILOT_ADMISSION_ARCHITECTURE.md` | CREATE | Qwen, GLM | YES (Discovery Document) |
| `docs/coordination/P7_MANAGER_GO_NO_GO_MATRIX.md` | CREATE | Qwen, Gemini | YES (Discovery Document) |
| `docs/coordination/P7_REAL_PILOT_SCOPE_PROPOSAL.md` | CREATE | Qwen, GLM, Gemini | YES (Discovery Document) |
| `docs/coordination/P7_REAL_DATA_ADMISSION_DECISION_PACKAGE.md` | CREATE | GLM, Qwen | YES (Discovery Document) |
| `docs/coordination/P7_PRODUCTION_ADMISSION_READINESS.md` | CREATE | Gemini, GLM | YES (Discovery Document) |
| `docs/coordination/P7_MANAGER_DECISION_PACKAGE.md` | CREATE | Qwen, Gemini | YES (Discovery Document) |
| `docs/coordination/P7_SYNTHETIC_MANAGER_DECISION_REHEARSAL.md` | CREATE | Qwen, Gemini | YES (Discovery Document) |
| `docs/coordination/P7_REAL_PILOT_EXIT_PLAN.md` | CREATE | GLM, Gemini, Qwen | YES (Discovery Document) |
| `docs/coordination/P7_NEGATIVE_TEST_MATRIX.md` | CREATE | Qwen, GLM | YES (Discovery Document) |
| `docs/coordination/P7_REAL_PILOT_WRITE_MANIFEST.md` | CREATE | Qwen, GLM, Gemini | YES (Discovery Document) |
| `backend/core/` | READ_ONLY_REFERENCE | All | **NO (LOCKED DURING DISCOVERY)** |
| `backend/apps/` | READ_ONLY_REFERENCE | All | **NO (LOCKED DURING DISCOVERY)** |
| `frontend/src/` | READ_ONLY_REFERENCE | All | **NO (LOCKED DURING DISCOVERY)** |
| `deploy/` | READ_ONLY_REFERENCE | All | **NO (LOCKED DURING DISCOVERY)** |

### 2. Strict Manifest Rules
- **`EXACT_PATHS_ONLY`**: Every path is enumerated explicitly.
- **`ZERO_WILDCARDS`**: No `*`, `**`, or directory globs permitted.
- **`UNREVIEWED_PATHS`**: `0`.
- **`RUNTIME_MUTATION`**: `0` (Zero source code, database migration, or production deployment modifications permitted during Discovery).
