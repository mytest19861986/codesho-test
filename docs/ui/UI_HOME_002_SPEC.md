# UI-HOME-002A - Homepage implementation specification

Status: `ANALYSIS_ONLY - AWAITING_EMPLOYER_APPROVALS`  
Reference: `H:\codesho\UI\ui new\desktop+mobile+tablet\main.png`  
Scope: This document plans a future Homepage implementation. It authorizes no
source, asset, package, data, API, commit, or push change.

## Non-negotiable implementation rules

1. All user-facing strings, links, CTA labels, icons, brand nodes, statistics,
   card data, testimonials and media are typed content supplied to components;
   no marketing copy or fabricated data is embedded in reusable JSX.
2. Components use semantic tokens only. Raw component colors, screenshot
   extraction/tracing, unlicensed assets, and direct CSS brand literals are
   forbidden.
3. The existing `PublicShell` is consumed unchanged. Homepage code never uses
   an Application Shell sidebar or mobile bottom navigation.

## Responsive shell map

| Viewport | Container and header | Content behavior |
| --- | --- | --- |
| 1440 Desktop | centered max 1280px; 72px public header; hybrid brand-left/nav-middle/actions-right | multi-column content; 24-32px exterior spacing |
| 1024 Tablet | 64px compact header; desktop navigation hidden; drawer trigger visible | 16-24px spacing; two-column cards where content permits |
| 390 Mobile | 56px compact header; drawer trigger; no bottom navigation | 12-16px spacing; one-column sections; touch targets at least 44px |

Normal vertical scrolling is expected. Every breakpoint must prohibit
horizontal overflow, clipped controls, duplicate brand/navigation, and
unreachable focus states.

## Section inventory and executable contracts

| Section | Purpose and desktop geometry | Tablet / mobile behavior | Candidate component and typed content |
| --- | --- | --- | --- |
| Public header | 72px shell header above all content; brand visual left, primary nav centered, utility/action visual right | hide desktop nav below 1280px; menu/drawer remains; retain one brand | existing `PublicShell`; `PublicNavigationItem[]`, `brand: ReactNode`, action and utility slots |
| Hero | primary value proposition with two CTA controls and reserved visual/media column; approximately two balanced desktop columns | stack copy and approved media; CTA controls wrap/stack only below available width | `HomeHero`; `headline`, `supportingText`, `primaryCta`, `secondaryCta`, optional `media` |
| Trust/statistics strip | bordered horizontal strip below hero; semantic proof points only | 2x2 or horizontal-scroll-free stacked grid | `TrustStrip`; `TrustItem[]` with `label`, `value`, optional icon; values require provenance |
| Learning paths | section heading plus three/four route cards | two columns tablet; single column mobile | `LearningPathGrid`; `LearningPathCardContent[]` with image/icon asset, title, description, tags, destination |
| Featured projects | heading/actions and visual project cards | two columns tablet; one-column or accessible carousel only when approved | `FeaturedProjectGrid`; `ProjectCardContent[]` with asset, title, technology labels, destination |
| Featured courses | course cards with category, instructor, rating/progress/price only when real data exists | two columns tablet; one column mobile | `FeaturedCourseGrid`; `CourseCardContent[]`; every numeric field has provenance and state |
| AI mentor CTA | dark/brand accent panel with explanatory copy and optional approved illustration | stack text/media; preserve contrast and 44px CTA | `MentorCta`; text, CTA, optional licensed media and alt text |
| Testimonials | social proof cards; cards may not imply real people without written source approval | three desktop, two tablet, one mobile; no inaccessible carousel | `TestimonialList`; only verified `TestimonialContent[]` with identity/display permission and avatar license |
| Final CTA | final conversion panel with primary/secondary paths | controls stack without truncation | `FinalCta`; title, description, CTAs, optional decorative token-only treatment |
| Footer | `PublicFooter` with brand/summary, reusable link groups and legal/social slots | balanced tablet columns; mobile stacked/compact groups | existing `PublicShell` footer contracts; link destinations must be registered |

## Proposed component tree

```text
Homepage
- PublicShell
  - PublicHeader / PublicNavigationDrawer
  - HomeHero
  - TrustStrip
  - LearningPathGrid
  - FeaturedProjectGrid
  - FeaturedCourseGrid
  - MentorCta
  - TestimonialList
  - FinalCta
  - PublicFooter
```

## Typed content and provenance contract

Every future `HomepageContent` payload is passed from a content module or
approved server/data boundary and includes stable ids. CTA shape is
`{ id, label, href, destinationStatus }`; `destinationStatus` is one of
`approved`, `pending_product_decision`, or `unavailable`. Numeric data shape
is `{ value, label, provenance, asOf, displayState }`; `displayState` is
`verified`, `hidden`, or `placeholder_not_for_production`. Testimonials require
`source`, `permissionStatus`, `displayName`, and avatar `assetId`.

No value may be presented as a production statistic, price, rating, learner
count, project count, testimonial, instructor identity, or course availability
until its provenance is approved. Pending data is hidden rather than replaced
with mock numbers.

## Asset dependency register

| Need | Required source/license metadata | Fallback before approval |
| --- | --- | --- |
| CodeSho logo/mark | owner, license, variants, dimensions, alt text | caller-provided text brand only |
| Hero/mentor illustration | original file, license, dimensions, alt text, responsive crop rules | omit media; do not recreate from screenshot |
| Learning/project/course imagery | original licensed asset, source, alt text, light/dark variants | content card without image only if product approves |
| Testimonial avatars | display permission, license/consent, alt text | omit testimonials |
| Footer/social icons | approved icon source/license and accessible label | textual links only |

## CTA destination register

All reference CTA destinations are unresolved product decisions. Future
implementation must register each primary hero CTA, secondary hero CTA,
path/project/course card CTA, mentor CTA, final CTA, auth CTA and footer link
with an approved route/URL before it becomes interactive. A pending
destination is not guessed; it is hidden or rendered disabled only when the
product decision explicitly permits that state.

## SEO and accessibility contract

- one `h1`, logical section headings, landmark labels, descriptive links and
  semantic lists/cards;
- metadata/title/description, canonical URL, OpenGraph and structured data
  are defined only from approved production content;
- images have approved meaningful alt text; decorative media is hidden from
  assistive technology;
- keyboard order follows RTL reading order; visible token focus ring is at
  least 2px; menu/drawer behavior remains covered by the closed shell gate;
- meet essential 4.5:1 contrast, respect reduced motion, and do not use color
  alone for status.

## Legacy homepage baseline removal plan

1. Freeze and hash the current legacy Homepage files before any source task.
2. Implement the new Homepage behind a bounded approved slice; do not blend
   reference mock content into the legacy page.
3. Run visual captures at 1440/1024/390, policy/lint/type/build, accessibility
   checks and independent review per slice.
4. Switch only after all sections and approved content/assets are present.
5. Remove the legacy baseline in a separately approved cleanup change after
   regression, routing and SEO verification.

## Suggested delivery slices

1. Content contracts, page frame and hero with no unapproved assets/data.
2. Trust strip and learning paths after provenance/CTA decisions.
3. Project and course cards after data/API ownership is approved.
4. Mentor CTA and final CTA after media/destinations are approved.
5. Testimonials/footer/social/SEO after permissions and legal content are
   supplied; then legacy removal in its own approval.

## Employer approval matrix

| Decision required | Commander recommendation | Effect if unresolved |
| --- | --- | --- |
| Are reference texts production-approved? | Treat as draft only; obtain editorial/product approval | use no reference marketing copy |
| Asset supply or AI generation? | employer supplies licensed originals; AI needs separate rights approval | omit visual assets |
| Statistics before backend connection? | hide until verified provenance exists | no mock figures |
| Testimonials before real samples? | omit until permissioned examples exist | no testimonial section/content |
| Primary CTA destinations? | approve exact routes and auth behavior | CTAs remain unimplemented/hidden |
| Text logo or asset? | text placeholder until UI-ASSET-001 supplies approved mark | no logo extraction/generation |
| Resolve drawer inertness/scroll lock and Mobile Legal alignment here? | Commander decision finalized: resolve all three in the first Homepage implementation task | Homepage final gate cannot pass while any remains unresolved |

## Evidence and stop condition

This analysis did not alter source, legacy baseline, coordination files,
dependencies, commits, or remotes. `git diff --check` must pass before
handoff.

Employer approval required: Approval Matrix decisions 1-6. Safe defaults are:
unapproved statistics hidden; unapproved testimonials omitted; unapproved
assets omitted; unapproved CTA destinations hidden and not guessed; and brand
rendered as a text placeholder.

Commander decision finalized: decision 7 requires drawer background inertness,
body-scroll locking, and Mobile Legal alignment to be resolved in the first
Homepage implementation task. That task cannot pass its final gate while any
of those three items remains unresolved. Homepage source implementation remains
blocked until the employer approvals are provided.
