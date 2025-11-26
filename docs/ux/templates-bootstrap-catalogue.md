# Templates Bootstrap Catalogue (ADR-1.0.18)

This catalogue maps selected Bootstrap 5 examples to the patterns used in TravelMathLite templates. Use these as your defaults—avoid custom CSS/JS; prefer Bootstrap utilities and components.

## Core layout

- **Navbar + sticky footer**: Based on Bootstrap Navbar + Sticky footer examples. Use brand-left, collapse on md, and footer with muted links.
- **Containers and grid**: Default `.container` with `.row.g-*` spacing; use `.container-fluid` only for dense layouts (dashboards/maps).

## Components to reuse

- **Cards**: Album/Blog examples. Wrap content in `.card` + `.card-body` for feature listings (e.g., calculators, trips, accounts, search CTAs).
- **List groups**: For search results and nearest-airport lists; add `.list-group-numbered` when ordering matters. Use badges for distances.
- **Forms**: Input groups and validation states from Bootstrap forms. Apply `form-control` / `form-select`, group fields with `.row.g-3`, show errors via `.invalid-feedback.d-block`.
- **Pagination**: Bootstrap `.pagination` inside `<nav aria-label="Pagination">`; preserve querystring (see `templates/includes/pagination.html`).
- **Alerts/messages**: `.alert` with dismiss button (`btn-close`) for flash messages or inline errors.
- **Breadcrumbs**: Use `.breadcrumb` when pages are nested (optional).
- **Tables**: `.table.table-striped` wrapped in `.table-responsive` for tabular data (if needed).

## Template references (current usage)

- Base layout and includes: `templates/base.html`, `templates/includes/navbar.html`, `templates/includes/footer.html`, `templates/includes/alerts.html`, `templates/includes/pagination.html`.
- Search: `apps/search/templates/search/index.html` (card form + CTAs), `apps/search/templates/search/results.html` (list-group results + pagination).
- Calculators: `apps/calculators/templates/calculators/*.html` (cards for forms/results).
- Airports: `apps/airports/templates/airports/nearest.html` + partials (list-group with distance badges).
- Accounts/Trips: `apps/accounts/templates/accounts/index.html`, `apps/trips/templates/trips/index.html` (cards/list groups).

## Source examples (Bootstrap 5.3.8)

- Navbars: `examples/navbars/`  
- Sticky footer: `examples/sticky-footer/`  
- Album / Blog: `examples/album/`, `examples/blog/`  
- List group + badges: `components/list-group/`  
- Forms: `forms/overview/`, `forms/validation/`  
- Pagination: `components/pagination/`

## Usage notes

- Keep markup strictly to Bootstrap classes/utilities; avoid adding new CSS/JS.  
- Prefer list groups for dense results; cards for feature summaries; tables only when tabular data is essential.  
- Ensure accessibility: labels, `aria-describedby`, `aria-live` on result regions, and navbar collapse attributes.  
- When adding a new page, start from one of the reference templates above and stay within this catalogue.
