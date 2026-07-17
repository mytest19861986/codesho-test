# Homepage Alpha approvals

Date: 2026-07-17
Status: employer decisions supplied through Commander for `UI-HOME-002B1`

## Approved decisions

- Reference copy is approved only as an `alpha_approved` draft. It is stored as
  typed Persian content and is not a claim of production availability.
- Non-logo AI assets may be generated in a separately authorized asset task.
  This contract creates no asset, asset URL, or media placeholder.
- Statistics without backend provenance are hidden.
- Testimonials are omitted.
- The logo remains a text placeholder: `کدشو`.

## Route policy

The approved route registry is `/login`, `/signup`, `/paths`, `/courses`,
`/projects`, and `/mentor`. At this checkpoint none is implemented. Every
destination in the Alpha contract is therefore
`hidden_until_route_available`; a future renderer must not render it as a
link until its route is available.

## Scope boundary

This decision authorizes the typed content contract only. It does not
authorize Homepage/page, component, CSS, asset, shell, package, or lockfile
changes.
