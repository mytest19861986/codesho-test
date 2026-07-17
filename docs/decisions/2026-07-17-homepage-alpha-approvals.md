# Homepage Alpha approvals

Date: 2026-07-17
Status: employer decisions and `UI-HOME-002B1R-FIX` disposition supplied through Commander

## Approved decisions

- The reference transcript is a strict Alpha content source, not a production
  availability claim. Copy not transcribed exactly is removed or represented
  as a typed pending state.
- Non-logo illustrations are `generation_authorized`; this contract creates
  no asset, asset URL, or media placeholder. The official logo remains
  `awaiting_official_asset` and the visible brand text is `CodeSho`.
- Statistics without backend provenance are hidden.
- Testimonials are omitted.
- Footer transcript is intentionally absent because its reported Projects
  subgroup was ambiguous.

## Transcript review evidence

`GEMINI_UI_HOME_002B1_REFERENCE_COPY_AUDIT_01_COMPLETED` was received for
`main.png`. Its raw response is retained outside the repository. The Commander
disposition adopted the exact Hero description in the typed payload and
required the Mentor description to remain `pending_transcription`, rather than
inventing copy.

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
