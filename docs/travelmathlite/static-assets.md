# Static Assets: Bootstrap/HTMX Pins, Overrides, and Versioning (ADR-1.0.17)

This note documents how TravelMathLite sources UI assets, pins versions, and layers overrides for Bootstrap 5 + HTMX per ADR-1.0.17.

## Sources and pins

- **Bootstrap CSS/JS (CDN by default)**  
  - CSS: `https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css`  
    - SRI: `sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH`
  - JS: `https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js`  
    - SRI: `sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz`
- **HTMX (CDN by default)**  
  - JS: `https://unpkg.com/htmx.org@2.0.3/dist/htmx.min.js`  
    - SRI: `sha384-0895/pl2MU10Hqc6jd4RvrthNlDiE9U1tWmX7WRESftEDRosgxNsQG/Ze9YMRzHq`

## Loading order (base template)

- `templates/includes/head.html` loads:
  1. Bootstrap CSS (CDN, pinned + SRI)
  2. `static/css/accessibility.css` (WCAG/focus overrides)
  3. `static/css/overrides.css` (project-specific tweaks, minimal)
- `templates/base.html` loads scripts **deferred** before `</body>`:
  - Bootstrap bundle JS (CDN, pinned + SRI)
  - HTMX (CDN, pinned + SRI)

## Overrides and custom assets

- **Accessibility overrides**: `travelmathlite/static/css/accessibility.css` — focus rings, contrast tweaks using Bootstrap variables.
- **Project overrides**: `travelmathlite/static/css/overrides.css` — minimal UI touches layered after Bootstrap. Keep it small; prefer Bootstrap utilities/variables first.
- Add new overrides to `overrides.css` (or a nearby file) and ensure they load **after** Bootstrap in `includes/head.html`.

## CDN vs. vendored switch

- CDN is default for simplicity. If you need local vendored assets:
  1. Place files under `travelmathlite/static/vendor/bootstrap/` or equivalent.
  2. Update `templates/includes/head.html` and `templates/base.html` to point to `{% static 'vendor/bootstrap/css/bootstrap.min.css' %}` and `{% static 'vendor/bootstrap/js/bootstrap.bundle.min.js' %}`.
  3. Preserve SRI hashes when using CDN; not needed for local static.

## Cache busting

- `ManifestStaticFilesStorage` (Django) handles cache-busting by hashing filenames (e.g., `bootstrap.min.abcd1234.css`) on `collectstatic`.
- Always load assets via `{% static %}` for local/vendored files so hashed names are used in production. CDN assets rely on versioned URLs above.

## HTMX notes

- HTMX is global and deferred; HTMX partials mirror full-page Bootstrap styling.
- Keep HTMX enhancements progressive; forms still work with full-page POST/GET if JS is disabled.

## What to do when upgrading versions

1. Choose the new version and record it here (CSS/JS URLs + SRI).
2. Update `templates/includes/head.html` (CSS) and `templates/base.html` (JS) if still using CDN.
3. If vendored, replace files under `static/vendor/...` and re-run `collectstatic`.
4. Sanity check UI and HTMX flows in the browser; clear caches/CDN if applicable.
