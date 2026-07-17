# UI-HOME-002B1 handoff

## Scope completed

The Typed Homepage Alpha Content Contract is limited to:

- `frontend/src/features/home/home.types.ts`
- `frontend/src/content/fa/homepage.alpha.ts`

The payload contains draft Alpha copy, a text-only `کدشو` brand, the approved
route registry, and hidden destinations for every route that is not yet
implemented. It deliberately contains no statistics, testimonials, prices,
ratings, assets, asset URLs, or rendered UI.

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
