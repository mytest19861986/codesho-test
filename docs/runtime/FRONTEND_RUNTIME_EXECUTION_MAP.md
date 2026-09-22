# Frontend Runtime Execution Map
**Document Version:** 1.0.0  
**Wave Context:** Wave 5.15 — Runtime Integration Qualification (Phase 3)  
**Status:** Certified & Hardlocked  
**Safety Constraints:** `CODE_CHANGE: 0` | `DATABASE_MIGRATION: 0` | `PRODUCTION_TOUCH: 0` | `REAL_USER_TRAFFIC: 0`

---

## 1. Executive Summary & Runtime Topology
This document formally defines the **Frontend Runtime Execution Map** for the Codesho platform, detailing the deterministic execution flow of Next.js 14+ (App Router), server-client component boundaries, state hydration, API client adapter integration, and fail-closed error boundaries.

```
[ User Agent / Browser ]
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Next.js App Router (Server Environment / Node.js Runtime)    │
│  ├─ RootLayout (app/layout.tsx: HTML shell, fonts, meta)    │
│  ├─ Tenant / Session Resolver (Headers & Cookies evaluation)  │
│  └─ Role AppShell Boundary (Server Component)               │
└──────────────────────────────────────────────────────────────┘
       │
       ▼ (RSC Stream / Initial HTML Transfer)
┌──────────────────────────────────────────────────────────────┐
│ Browser Client Environment (Hydration & React Runtime)       │
│  ├─ Client Component Hydration (Theme, UI Contexts)         │
│  ├─ Design Token Enforcement (CSS Variables / Vanilla CSS)  │
│  ├─ API Client Adapter Layer (fetch, CSRF header injection)  │
│  ├─ Global ErrorBoundary & Component Error Fallbacks        │
│  └─ Empty / Skeleton Loading State Governance               │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Next.js App Router Execution Lifecycle

### 2.1 Request Ingestion & Root Layout Boundary
1. **HTTP Ingestion**: Next.js server runtime intercepts HTTP requests at the edge/node layer.
2. **Server-Side Tenant Resolution**: Reads `X-Tenant-ID` or domain context headers to ensure context alignment with Django backend tenant isolation.
3. **AppShell Rendering (`app/layout.tsx`)**:
   - Injects canonical head tags, fonts (IRANSansX/Inter), and global CSS tokens.
   - Enforces `dir="rtl"` and Persian locale tokens deterministically.
   - Emits pure HTML shell before hydration without executing client JavaScript.

### 2.2 Server Component (RSC) vs. Client Component Boundaries
- **Server Components (Default)**:
  - Perform static content generation, layout structuring, and metadata assembly.
  - Zero bundle impact on client runtime JavaScript.
- **Client Components (`'use client'`)**:
  - Bound exclusively to interactive elements (form inputs, navigation drawers, dynamic modal dialogs).
  - Hydrated deterministically without mutating global window or injecting dynamic unsafe inline styles.

---

## 3. API Adapter Layer & DTO Mapping

### 3.1 API Client Runtime Pipeline
```
[ Client Action / Hook ]
       │
       ▼
[ API Client Adapter (src/services/apiClient.ts) ]
       │── Injects CSRF Token (read from document.cookie / meta)
       │── Injects Tenant ID Header (`X-Tenant-ID`)
       │── Enforces Timeout (Bounded 8000ms abort signal)
       │
       ▼
[ Gateway / Backend Proxy -> Django DRF Endpoints ]
       │
       ▼
[ Response Validation & DTO Transformation ]
       │── Sanitizes payload (Strips unapproved fields)
       │── Validates TypeScript contract against OpenAPI schema
       ▼
[ UI State Dispatcher (React State / Store) ]
```

### 3.2 Anti-Evaluation & Zero-PII Enforcement
- Frontend DTO adapters strictly filter any child-level evaluation, scoring, or behavioral grading before UI components receive state.
- Minor currency units (IRR) received from backend are converted to Toman strictly inside presentation formatting hooks (`formatToman(amount)`).
- Timestamps (UTC `TIMESTAMPTZ`) are formatted into Jalali representation exclusively in presentation layers without modifying the underlying state.

---

## 4. Error Boundaries & Fallback States

### 4.1 Tiered Error Handling
1. **Root Error Boundary (`app/error.tsx`)**:
   - Catches uncaught runtime exceptions across the entire route subtree.
   - Renders a localized, user-friendly fail-closed error interface with retry capability.
   - Sanitizes error messages: NEVER leaks stack traces, internal URLs, or database errors to the DOM.
2. **Component Error Boundary**:
   - Localizes widget failures (e.g. telemetry widget or notification bar failure does not crash the main view).

### 4.2 Loading & Skeleton State Governance (`loading.tsx`)
- Server streaming activates `loading.tsx` instantly upon navigation.
- Accessible skeletons display with `aria-busy="true"` and correct ARIA live region annotations.
- Zero cumulative layout shift (CLS < 0.05) guaranteed by fixed-dimension skeleton wrappers.

---

## 5. Viewport & Responsive Runtime Integrity
- **Breakpoints**:
  - Mobile: `320px` to `767px`
  - Tablet: `768px` to `1023px`
  - Desktop: `1024px` to `1440px`+
- Touch targets strictly maintain `>= 44x44px` physical touch bounds across all mobile viewports.
- RTL layout flow remains strictly preserved across all viewport transitions.
