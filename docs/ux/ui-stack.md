# UI Stack Guide (ADR-1.0.17)

This guide describes how TravelMathLite uses Bootstrap 5 + HTMX, where shared includes live, and how to keep forms/components consistent. Screenshots live under `docs/travelmathlite/ui/` for attestation.

## Assets and loading order

- Bootstrap 5.3.3 (CSS/JS) via CDN with SRI in `templates/includes/head.html` and `templates/base.html`.
- HTMX 2.0.3 via CDN, deferred before `</body>`.
- Overrides:
  - `static/css/accessibility.css` — WCAG/focus tweaks via Bootstrap variables.
  - `static/css/overrides.css` — minimal project UI tweaks layered last.
- Cache busting: Django `ManifestStaticFilesStorage` handles hashed filenames for local assets; CDN pins use versioned URLs.

## Shared includes

- Navbar: `templates/includes/navbar.html` (mobile collapse, active states via `resolver_match`, search form).
- Alerts: `templates/includes/alerts.html` (Bootstrap dismissible alerts bound to Django messages).
- Footer: `templates/includes/footer.html` (links to PRD/ADR/briefs).
- Pagination: `templates/includes/pagination.html` (Bootstrap `.pagination` with `aria-label`).
- Base template: `templates/base.html` loads head, navbar, alerts slot, content, footer.

## Forms and components

- Forms use Bootstrap classes (`form-control`, `form-select`) applied in form widgets (see `apps/calculators/forms.py` initialization).
- Layout pattern: wrap forms in `.card` with `.card-body`; use `.row.g-3` grids for multi-column inputs; buttons with `btn btn-primary`.
- Validation: display field errors with `invalid-feedback d-block`; keep `aria-describedby` linking help/error IDs.
- HTMX partials mirror full-page styling: calculator results and nearest-airport results use cards/list groups.

## HTMX patterns

- Global HTMX script deferred; forms keep standard `action`/`method` for progressive enhancement.
- Targets: calculators use `hx-target` to swap result containers (`outerHTML show:top`); nearest airports swaps results container `innerHTML`.
- Accessibility: result containers include `role="region"` and `aria-live` with focus management in base template script (`htmx:afterSwap` focus).

## Overrides and customization

- Add small tweaks to `static/css/overrides.css` (loaded after Bootstrap). Prefer Bootstrap utilities and CSS variables first.
- If switching to vendored assets, point includes to `{% static 'vendor/bootstrap/...` %}` and keep the same order.

## Screenshots (attestation)

- Placeholder captures at `docs/travelmathlite/ui/`:
  - `home.png` — Navbar + home cards
  - `distance.png` — Distance calculator form + HTMX results
  - `search.png` — Search results list + pagination
  - `nearest.png` — Nearest airports form + results
- Replace placeholders with real captures during manual verification.
- Attestation notes and checklist live in `docs/travelmathlite/ui/attestation.md` (what to capture and what to check).

## Component catalogue

- See `docs/ux/templates-bootstrap-catalogue.md` for the Bootstrap examples and patterns to reuse (navbars, sticky footer, cards, list groups, forms, pagination).
