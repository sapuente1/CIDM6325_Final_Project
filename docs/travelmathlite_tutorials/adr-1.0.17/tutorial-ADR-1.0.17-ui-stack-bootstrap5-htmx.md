# Tutorial: ADR-1.0.17 UI Stack (Bootstrap 5 + HTMX)

**Date:** November 26, 2025  
**ADR Reference:** [ADR-1.0.17 UI stack: Bootstrap 5 + HTMX](../../travelmathlite/adr/adr-1.0.17-ui-stack-bootstrap5-htmx.md)  
**Briefs:** [adr-1.0.17 briefs](../../travelmathlite/briefs/adr-1.0.17/)

---

## Overview

This tutorial shows how the TravelMathLite UI stack is assembled with Bootstrap 5 and HTMX: base template assets, shared includes (navbar/footer/alerts/pagination), form/component styling with HTMX partials, static overrides/versioning, and documentation/screenshots for attestation.

**Learning Objectives**

- Load pinned Bootstrap/HTMX assets with SRI and deferred scripts.
- Use shared includes for navbar/footer/alerts/pagination across pages.
- Apply consistent Bootstrap styling to forms, results, and HTMX partials.
- Understand where overrides live and how cache-busting works.
- Know where UI docs and screenshots are stored for reviewers.

**Prerequisites**

- TravelMathLite project set up; `uv` available for commands.
- Basic familiarity with Django templates and static files.
- No migrations required; docs-only steps can be previewed by running the dev server.

---

## Section 1 — Base template and assets

**Brief Context:** [brief-ADR-1.0.17-01-base-template-and-assets.md](../../travelmathlite/briefs/adr-1.0.17/brief-ADR-1.0.17-01-base-template-and-assets.md)  
**Goal:** Load Bootstrap 5 + HTMX globally with integrity attributes, progressive enhancement, and navbar collapse.

### Documentation context

- Django template docs: `{% static %}` resolves hashed filenames when using `ManifestStaticFilesStorage`.
- Bootstrap docs: include CSS in `<head>` and bundle JS before `</body>`; navbar toggler requires the bundle.
- HTMX docs: load script once, defer to avoid blocking render; progressive enhancement keeps forms working without JS.

### Implementation highlights

- `templates/includes/head.html`:

```html
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
      integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH"
      crossorigin="anonymous">
<link href="{% static 'css/accessibility.css' %}" rel="stylesheet">
<link href="{% static 'css/overrides.css' %}" rel="stylesheet">
```

- `templates/base.html` defers scripts before `</body>`:

```html
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz"
        crossorigin="anonymous" defer></script>
<script src="https://unpkg.com/htmx.org@2.0.3/dist/htmx.min.js"
        integrity="sha384-0895/pl2MU10Hqc6jd4RvrthNlDiE9U1tWmX7WRESftEDRosgxNsQG/Ze9YMRzHq"
        crossorigin="anonymous" defer></script>
```

- HTMX focus management lives in the base template (`htmx:afterSwap` listener).

### How to verify

- Load any page; check devtools Network for Bootstrap/HTMX loads with SRI and no console errors.
- Toggle navbar on mobile width; collapse/expand should work (Bootstrap bundle loaded).
- HTMX available: run `typeof htmx !== 'undefined'` in console.

---

## Section 2 — Layout includes (navbar, footer, alerts, pagination)

**Brief Context:** [brief-ADR-1.0.17-02-layout-includes-navbar-footer-alerts.md](../../travelmathlite/briefs/adr-1.0.17/brief-ADR-1.0.17-02-layout-includes-navbar-footer-alerts.md)  
**Goal:** Centralize shared UI fragments with Bootstrap patterns and accessibility defaults.

### Documentation context

- Bootstrap navbar: requires `.navbar-toggler` + collapse target; use `aria-controls/expanded/label`.
- Alerts: `.alert` with dismiss button; `role="alert"` for screen readers.
- Pagination: wrap in `<nav aria-label="Pagination">` with `.pagination`.

### Implementation highlights

- Includes under `templates/includes/`:
  - `navbar.html` — responsive navbar, active states via `request.resolver_match`, search form, auth links.
  - `alerts.html` — loops over Django messages as dismissible alerts.
  - `pagination.html` — Bootstrap pagination preserving querystring.
  - `footer.html` — small-text links to PRD/ADR/briefs.
- `base.html` pulls in navbar, alerts slot, and footer around the page content.

### How to verify

- Navigate pages: navbar links highlight the active namespace; collapse works on narrow viewports.
- Trigger a Django message (e.g., login failure) to see alert styling.
- Check any paginated view using `includes/pagination.html` (search results).

---

## Section 3 — Forms, components, and HTMX patterns

**Brief Context:** [brief-ADR-1.0.17-03-forms-components-and-htmx-patterns.md](../../travelmathlite/briefs/adr-1.0.17/brief-ADR-1.0.17-03-forms-components-and-htmx-patterns.md)  
**Goal:** Keep forms/buttons/results styled consistently and ensure HTMX partials mirror full-page markup.

### Documentation context

- Bootstrap forms: apply `form-control` / `form-select`, group inputs with `.row.g-3`, show errors via `invalid-feedback d-block`.
- HTMX: partial responses should include the same Bootstrap structure as full pages.
- Accessibility: preserve `aria-describedby` and error/help IDs.

### Implementation highlights

- Calculators (`apps/calculators/templates`):
  - Forms wrapped in `.card .card-body`; multi-column grids with `.row.g-3`.
  - Submit buttons use `btn btn-primary`; errors displayed with `invalid-feedback d-block`.
  - HTMX partials (`distance_result.html`, `cost_result.html`) use cards + list groups matching full-page styling.
- Nearest airports (`apps/airports/templates/airports/nearest.html` + partials) use the same card/grid pattern; results rendered as numbered list-group with distance badges.
- Search results (`apps/search/templates/search/results.html`) use card form header and list-group results with shared pagination include.
- Form widgets set classes in `apps/calculators/forms.py` initializer for consistent styling.

### How to verify

- Manual: Load calculators, nearest airports, and search pages; confirm form layout and results cards match between full render and HTMX swaps (e.g., submit distance form twice—HTMX partial should look identical).
- Accessibility spot-check: error messages tie to `aria-describedby` IDs; `role="region"` + `aria-live` on results containers.

---

## Section 4 — Static overrides and versioning

**Brief Context:** [brief-ADR-1.0.17-04-static-overrides-and-versioning.md](../../travelmathlite/briefs/adr-1.0.17/brief-ADR-1.0.17-04-static-overrides-and-versioning.md)  
**Goal:** Document asset pins, overrides location, CDN vs. vendored switch, and cache-busting approach.

### Documentation context

- Django `ManifestStaticFilesStorage` adds hashed filenames for cache-busting when using `{% static %}`.
- Bootstrap/HTMX pins recorded with SRI hashes; CDN URLs are versioned.

### Implementation highlights

- Overrides:
  - `static/css/accessibility.css` — WCAG-focused tweaks.
  - `static/css/overrides.css` — minimal project tweaks loaded after Bootstrap.
- Guidance file: `docs/travelmathlite/static-assets.md` covers pins, SRI, load order, switching to vendored assets, and upgrade steps.
- Base/head templates already point to CDN; switch to vendored by editing those includes to use `{% static 'vendor/bootstrap/...'%}`.

### How to verify

- Run `uv run python manage.py collectstatic` (in a throwaway env) to confirm hashed names and no missing files.
- Spot-check that overrides CSS loads after Bootstrap in devtools Network/Styles.

---

## Section 5 — UI docs and screenshots

**Brief Context:** [brief-ADR-1.0.17-05-ui-docs-and-screens.md](../../travelmathlite/briefs/adr-1.0.17/brief-ADR-1.0.17-05-ui-docs-and-screens.md)  
**Goal:** Provide UI stack docs and screenshots for attestation.

### Documentation context

- Consolidated guide: `docs/ux/ui-stack.md` (assets, includes, patterns, overrides, screenshot pointers).
- README links to the UI stack guide.

### Implementation highlights

- Placeholder screenshots stored in `docs/travelmathlite/ui/`:
  - `home.png`, `distance.png`, `search.png`, `nearest.png` (replace with real captures during manual verification).
- UI stack guide ties together assets, includes, patterns, HTMX notes, and override guidance.

### How to verify

- Open `docs/ux/ui-stack.md` to review pins/patterns; ensure README link works.
- Replace placeholders with real screenshots after running the app; keep filenames stable for attestation.

---

## Summary and next steps

- The UI stack is standardized: pinned Bootstrap/HTMX, shared includes, consistent forms/partials, and documented overrides/versioning.
- Next steps:
  1) Capture real screenshots to replace placeholders in `docs/travelmathlite/ui/`.
  2) If CSP is added, include CDN hosts (`cdn.jsdelivr.net`, `unpkg.com`) in `script-src`/`style-src`.
  3) When upgrading asset versions, update pins in `includes/head.html`, `base.html`, and `docs/travelmathlite/static-assets.md`, then sanity-check navbar/HTMX flows.

---

## References

- ADR: [ADR-1.0.17 UI stack: Bootstrap 5 + HTMX](../../travelmathlite/adr/adr-1.0.17-ui-stack-bootstrap5-htmx.md)
- Briefs: [adr-1.0.17](../../travelmathlite/briefs/adr-1.0.17/)
- UI guide: [docs/ux/ui-stack.md](../../ux/ui-stack.md)
- Asset pins/overrides: [docs/travelmathlite/static-assets.md](../../travelmathlite/static-assets.md)
- Templates: `templates/includes/`, `templates/base.html`
- Key pages: calculators (distance/cost/fly_or_drive), airports nearest, search results
