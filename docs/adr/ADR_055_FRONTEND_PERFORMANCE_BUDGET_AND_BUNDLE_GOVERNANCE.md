# ADR-055: Frontend Performance Budget & Bundle Governance Architecture Gate

## Context & Problem Statement
As CodeSho expands across role-based experiences (Student, Parent, Mentor, Admin), frontend assets, hydration costs, and client rendering times risk degrading, particularly on low-bandwidth connections and lower-end mobile devices common among Iranian learners. Without an automated architectural gate, bundle bloat and unmonitored script execution will harm First Contentful Paint (FCP) and Largest Contentful Paint (LCP).

## Decision
We enforce a mandatory **Frontend Performance Budget & Bundle Governance Gate** within Next.js App Router and the design token system:

1. **Strict Bundle Weight Budgets**:
   - Gzipped shared runtime bundle must not exceed **85 KB**.
   - Vendor chunks must not exceed **160 KB**.
   - Dynamic route chunks must not exceed **45 KB**.
2. **Mandatory Dynamic Import (Code Splitting) Boundaries**:
   - Heavy modal components, drawers, charts, and interactive canvas components must be dynamically imported with `next/dynamic` (`ssr: false` where server pre-rendering is non-beneficial).
3. **Persian Typography & Font Asset Strategy**:
   - Fonts (Vazirmatn) must use `font-display: swap` with subsetted WOFF2 formats to eliminate layout shifts (CLS < 0.01) and prevent invisible text during font download.
4. **Rendering Cost & Hydration Ceiling**:
   - Client component hydration must complete within **250ms** on 4x CPU throttling.

## Consequences
- **Positive**:
  - Predictable load times across all mobile and desktop devices.
  - Zero regression in Core Web Vitals.
  - Consistent Persian typography rendering without layout shifts.
- **Negative**:
  - Developers must deliberately split heavy components and respect chunk budgets.

## Compliance & Verification
- Validated via CI bundle analysis (`@next/bundle-analyzer`) and Lighthouse CI performance gate (Minimum Score: 92/100).
