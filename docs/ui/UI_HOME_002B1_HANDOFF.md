# UI-HOME-002B1R handoff

## Scope completed

The Typed Homepage Alpha Content Contract is limited to:

- `frontend/src/features/home/home.types.ts`
- `frontend/src/content/fa/homepage.alpha.ts`

The payload reconciles Alpha copy with the strict `main.png` transcription:
the text-only brand is `CodeSho`, all unimplemented destinations are hidden,
and every Homepage section has explicit typed state. Invented feature copy is
removed. The Mentor description is `pending_transcription`; the ambiguous
Footer transcript is not content. It deliberately contains no statistics,
testimonials, prices, ratings, assets, asset URLs, or rendered UI.

## Transcript disposition

The raw external audit completed with
`GEMINI_UI_HOME_002B1_REFERENCE_COPY_AUDIT_01_COMPLETED`. Commander required
the exact Hero description in the typed payload, removal of the prior
invented Mentor description, and omission of uncertain Footer copy. The raw
response remains outside the repository.

## Renderer requirements

A later, separately authorized Homepage task may render a destination only
when its status is `available`. It must keep
`hidden_until_route_available` destinations absent rather than emitting broken
links. Page, component, CSS, asset, shell, and route work remains out of
scope for this handoff.

## Required gates

Run `npm run test:ui-policy`, `npm run check:ui-policy`, `npm run lint`,
`npx next typegen`, `npm run typecheck`, `npm run build`, and
`git diff --check`. No external review is required for this task.
