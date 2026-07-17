# UI-GOV-001 handoff

Status: complete
Repository: `codesho-test`
Implementation commit: `a02d2a9`
Final documentation checkpoint: `e37b5f0`
Promotion: forbidden for protected `codesho`

## Delivered

- `frontend/scripts/check-ui-policy.mjs` uses the installed TypeScript compiler
  API to scan production TS/TSX source for user-facing JSX literals and
  forbidden fixture/mock/demo/preview imports, and scans CSS/JS/TS source for
  raw colors and direct-color gradients.
- `frontend/ui-policy-baseline.json` pins the three approved legacy files by
  SHA-256. Any missing, changed, or extra exemption fails the gate.
- `frontend/scripts/check-ui-policy.test.mjs` covers raw HEX, rgb/gradient,
  named CSS colors, JSX marketing literals, fixture imports, baseline drift,
  token-layer colors, props, and the current repository pass.
- `frontend/package.json` exposes `test:ui-policy` and `check:ui-policy`.
  `.github/workflows/ci.yml` runs both before frontend lint.
- The decision protocol is recorded in
  `docs/decisions/2026-07-17-employer-execution-and-ui-policy.md`: T+0
  decision, one T+10 reminder, park unanswered blockers, and never infer or
  self-approve employer decisions.

## Approved legacy baseline

| Path | SHA-256 |
|---|---|
| `src/app/page.tsx` | `380F4F5C7E5FF105ABAF6C421991160E122BB9E92138141C5E5F0E454D781AB8` |
| `src/app/styles.css` | `955AFDE37693F2521310D1B677E1CB8C50CB77BF505C8F968E6079270A50EF73` |
| `src/app/ui-001.css` | `E66ADDC2479820FC4A7C314CAC4F79BDC9317270D86BE45B8E8B5021C582910B` |

## Verification

- Policy tests: `8 passed`.
- `npm run check:ui-policy`: passed on the live repository.
- `npm run lint`, `npm run typecheck`, `npm run build`, and `git diff --check`:
  passed.
- No dependency was added; `frontend/package-lock.json` was not changed.
- CI: [29564264678](https://github.com/mytest19861986/codesho-test/actions/runs/29564264678)
- Compose smoke/restore: [29564264683](https://github.com/mytest19861986/codesho-test/actions/runs/29564264683)
- Both real gates completed successfully for `e37b5f0`.

UI-GOV-001 is closed. Shell/page implementation remains blocked until a new
approved task. The next task must preserve the three employer blocking gates.
