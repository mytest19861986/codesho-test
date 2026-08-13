# Task81B Claude Evidence Transport

TASK_ID=SPRINT1-UI-LEARNING-DASHBOARD-READ-INTEGRATION-81B  
PR=#42  
CODE_BASE_UNDER_REVIEW=d2b9803972f0c20bc154df471ad941b2f78855fd  
CODE_HEAD_UNDER_REVIEW=e98d1c575903f7b5657a20c004ea2802189e4394  
TRANSPORT_BRANCH=review-evidence-task81b-claude  
PROMPT_ID=CLAUDE_TASK81B_CURRENT_HEAD_IMPLEMENTATION_HARD_GATE_20260813_V4_FOLDER_EVIDENCE  
PROVIDER=Claude  
PURPOSE=Independent current-head implementation hard-gate review from folder evidence

The transport branch HEAD is not the implementation HEAD. Claude MUST review
the exact CODE_HEAD_UNDER_REVIEW above and PR #42. Historical heads
`869532b77d9dc2c9a058401d6052e6e42fb2d961` and
`b5ce0a00f48e598db4ba507f92dfda68d9daadfc` are not current.

## Manifest

- `00-REVIEW-INDEX.md` — provenance, scope, and manifest.
- `01-BASE-TO-CODE-HEAD.diff` — exact base-to-head diff.
- `02-CHANGED-FILES.txt` — exact seven-file allow-list.
- `03-QWEN-CURRENT-HEAD-PASS.md` — current Qwen gate fields and disposition.
- `04-PR-CI-COMPOSE-EVIDENCE.md` — exact-head remote evidence pointers.
- `05-Task81B-DASHBOARD_DATA_BOUNDARY.tsx`
- `06-Task81B-DASHBOARD_SCREEN.tsx`
- `07-Task81B-DASHBOARD_STATE.tsx`
- `08-Task81B-dashboard.data-contract.test.mjs`
- `09-Task81B-dashboard.fixture.ts`
- `10-Task81B-dashboard.types.ts`
- `11-Task81B-learningClient.ts`

The seven source files are copied byte-for-byte from CODE_HEAD_UNDER_REVIEW.
No implementation branch, PR #42, or protected repository is modified here.
