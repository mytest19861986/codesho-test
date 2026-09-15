# P7 Gemini Route Accounting
## Phase 7 Manager Cockpit Interactive Route & Surface Accounting

- **PROJECT:** Codesho / SSD
- **TASK_ID:** `P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL`
- **STATUS:** 21/21 EXECUTED

---

### 1. Route Execution Totals
- **ROUTES_DISCOVERED:** 21
- **ROUTES_EXECUTED:** 21
- **UNTESTED_EXECUTABLE_ROUTES:** 0

---

### 2. Discovered & Executed Surfaces
| Surface / Route ID | Description | Rendered State | Verified Screenshot / Test |
| :--- | :--- | :--- | :---: |
| `route_01_default_cockpit` | Default cockpit overview | Clean candidate state | `desktop_1440x900.png` |
| `route_02_mobile_view` | Mobile viewport layout | Responsive layout | `mobile_390x844.png` |
| `route_03_no_go_stop` | Non-waivable gate failure | Red stop card | `no_go_hard_stop_1440x900.png` |
| `route_04_stale_evidence` | Evidence age > 24 hours | Amber defer warning | `defer_stale_evidence_1440x900.png` |
| `route_05_scope_drift` | Scope hash mismatch | Mutation alert | `scope_changed_1440x900.png` |
| `route_06_release_drift` | Release candidate mismatch | Version alert | `release_changed_1440x900.png` |
| `route_07_expired` | Decision validity window expired | Expired badge | `expired_1440x900.png` |
| `route_08_revoked` | Manager executed revocation | Terminal revoked banner | `revoked_1440x900.png` |
| `route_09_exception_denial` | Exception request rejected | Denied state | `exception_denied_1440x900.png` |
| `route_10_emergency_term` | Two-step emergency termination | Red alert dialog | `emergency_termination_1440x900.png` |
| `route_11_exit_plan` | Controlled exit flow execution | Controlled step flow | `exit_flow_1440x900.png` |
| `route_12_loading` | Asynchronous data fetching | Skeleton loader | Verified in test |
| `route_13_empty` | No candidate decision found | Empty placeholder | Verified in test |
| `route_14_error` | Generic server error | Error boundary | Verified in test |
| `route_15_forbidden` | Non-manager user access | 403 Forbidden modal | Verified in test |
| `route_16_api_success` | Decision submission confirmed | Toast notification | Verified in test |
| `route_17_api_failure` | Decision submission network failure | Retry alert banner | Verified in test |
| `route_18_session_fail` | Invalidation of manager auth | Relogin prompt | Verified in test |
| `route_19_go_ready` | All 14 gates green | Green submit active | Verified in test |
| `route_20_exception_pending` | Pending waiver review | Warning status | Verified in test |
| `route_21_window_invalid` | Outside authorized time window | Lockout message | Verified in test |
