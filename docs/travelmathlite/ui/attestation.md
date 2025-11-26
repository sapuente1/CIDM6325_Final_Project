# UI Attestation (ADR-1.0.18)

This note tracks the visual evidence for the Bootstrap-only template catalogue and confirms no new custom CSS/JS was added for ADR-1.0.18.

## Required screenshots (replace placeholders)

Capture real screenshots from the running app and overwrite the existing files in `docs/travelmathlite/ui/`:

- `home.png` — Navbar + home cards (base page)
- `distance.png` — Distance calculator form and HTMX results
- `search.png` — Search results with list-group + pagination
- `nearest.png` — Nearest airports form + results list with distance badges

Keep filenames the same. Ensure navbar collapse works (try narrow width) and pagination retains query params.

## Checks to perform

- Templates use only Bootstrap classes/utilities; no new custom CSS/JS added for ADR-1.0.18.
- Navbar search submits via GET to `search:index` and retains `q`.
- Pagination uses Bootstrap `.pagination` and preserves querystring.
- HTMX partials mirror full-page styling (cards/list groups).

## Where to reference

- UI stack guide: `docs/ux/ui-stack.md`
- Component catalogue: `docs/ux/templates-bootstrap-catalogue.md`

Record the commit hash when screenshots are updated for future audits.
