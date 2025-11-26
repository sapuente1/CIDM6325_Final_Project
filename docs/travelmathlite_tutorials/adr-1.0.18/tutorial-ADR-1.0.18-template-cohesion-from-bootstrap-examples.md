# Tutorial: ADR-1.0.18 Template Cohesion from Bootstrap 5 Examples

**Date:** November 26, 2025  
**ADR Reference:** [ADR-1.0.18 Template cohesion from Bootstrap 5 examples](../../travelmathlite/adr/adr-1.0.18-template-cohesion-from-bootstrap-examples.md)  
**Briefs:** [adr-1.0.18 briefs](../../travelmathlite/briefs/adr-1.0.18/)

---

## Overview

This tutorial explains how TravelMathLite standardizes templates using official Bootstrap 5 examples. It covers the base layout, navbar/footer, search/pagination patterns, app template alignment, documentation catalogue, and visual attestation. The goal is consistent, Bootstrap-only markup with zero new custom CSS/JS.

**Learning Objectives**

- Align base layout and partials to Bootstrap navbar + sticky footer patterns.
- Ensure navbar search, canonical, and pagination follow Bootstrap and ADR-1.0.4.
- Refactor app templates (search, accounts, calculators, airports) to shared patterns (cards/list groups/forms).
- Document the chosen Bootstrap components and capture screenshots for attestation.

**Prerequisites**

- TravelMathLite set up; `uv` available.
- No migrations required.
- For screenshots: Playwright installed (`uvx playwright install chromium`) and dev server runnable locally.

---

## Section 1 — Base layout and shared partials

**Brief Context:** [brief-ADR-1.0.18-01-base-layout-and-partials.md](../../travelmathlite/briefs/adr-1.0.18/brief-ADR-1.0.18-01-base-layout-and-partials.md)  
**Goal:** Use only Bootstrap navbar + sticky footer patterns in base layout/partials; no new custom CSS/JS.

### Documentation context

- Bootstrap Navbar + Sticky footer examples demonstrate collapse behavior and minimal footer markup.
- Django templates: keep `{% block canonical %}` and `{% include "includes/alerts.html" %}`; no extra JS beyond Bootstrap bundle and HTMX.

### Implementation highlights

- `templates/base.html`: `<main class="container flex-grow-1 py-4" role="main">` with navbar/footer includes; scripts deferred; alerts include just inside main.
- Includes used:
  - `templates/includes/navbar.html` — brand-left, collapse toggler with aria-controls/expanded/label, search form.
  - `templates/includes/footer.html` — muted links, sticky footer style via Bootstrap classes.
  - `templates/includes/alerts.html` — dismissible alerts from Django messages.

### Verify

- Manual: Load any page, check navbar collapse on mobile width, alerts render correctly, footer sticks after content.
- No new CSS/JS files added for this ADR.

---

## Section 2 — Navbar search, canonical, and pagination

**Brief Context:** [brief-ADR-1.0.18-02-navbar-search-and-canonical.md](../../travelmathlite/briefs/adr-1.0.18/brief-ADR-1.0.18-02-navbar-search-and-canonical.md)  
**Goal:** Navbar search GETs to `search:index`, preserves `q`; canonical links present on results; pagination uses Bootstrap and keeps querystring.

### Documentation context

- ADR-1.0.4: search URLs/canonical; Bootstrap pagination markup.
- Django: `{% block canonical %}` on result pages; `request.GET.urlencode` to keep query params.

### Implementation highlights

- `templates/includes/navbar.html`: search form method GET → `search:index`, retains `q` value.
- `templates/includes/pagination.html`: accepts `querystring` (defaults to `request.GET.urlencode`) to avoid duplicating page params; Bootstrap `.pagination` inside `<nav aria-label="Pagination">`.
- `apps/search/templates/search/results.html`: passes `q=` to pagination include; canonical block already present.

### Verify

- Manual: Use navbar search; input retains value; results show canonical link (view source); pagination links preserve `q`.

---

## Section 3 — App template alignment (Bootstrap catalogue)

**Brief Context:** [brief-ADR-1.0.18-03-app-template-alignment.md](../../travelmathlite/briefs/adr-1.0.18/brief-ADR-1.0.18-03-app-template-alignment.md)  
**Goal:** Refactor app templates to use cards/list groups/forms per Bootstrap examples; no custom CSS.

### Documentation context

- Bootstrap Album/Blog examples (cards), list-group components for dense lists, forms/validation examples.
- Accessibility: labels, `aria-describedby`, `aria-live` regions retained.

### Implementation highlights

- Search index: card-based search form + CTAs; supporting cards for browse/nearest.
- Accounts index: cards/list-groups for CTAs and quick links; login/signup buttons.
- Calculators and nearest airports already use cards and list groups; search results use list groups + pagination include.
- No new CSS/JS introduced; relies solely on Bootstrap classes/utilities.

### Verify

- Manual: Open search, accounts, calculators, nearest pages; confirm consistent card/list-group usage and spacing. Breadcrumbs optional; ensure no stray custom styles.

---

## Section 4 — Component catalogue docs

**Brief Context:** [brief-ADR-1.0.18-04-component-catalogue-docs.md](../../travelmathlite/briefs/adr-1.0.18/brief-ADR-1.0.18-04-component-catalogue-docs.md)  
**Goal:** Document which Bootstrap examples map to our templates and where to start for new pages.

### Documentation context

- Bootstrap 5 examples: Navbars, Sticky footer, Album, Blog, List group, Forms/Validation, Pagination.

### Implementation highlights

- `docs/ux/templates-bootstrap-catalogue.md`: lists component choices, template references, and source example folders; usage notes emphasize “no custom CSS/JS.”
- Linked from `docs/ux/ui-stack.md`.

### Verify

- Open the catalogue and confirm links/sections exist; README/UI stack points to it.

---

## Section 5 — Visual checks and attestation

**Brief Context:** [brief-ADR-1.0.18-05-visual-checks-and-attestation.md](../../travelmathlite/briefs/adr-1.0.18/brief-ADR-1.0.18-05-visual-checks-and-attestation.md)  
**Goal:** Capture screenshots proving Bootstrap-only templates and document the checklist.

### Documentation context

- Playwright scripts used for visual checks; attestation note tracks required views and confirms no new custom CSS/JS.

### Implementation highlights

- Real screenshots captured via Playwright stored at `docs/travelmathlite/ui/`:
  - `home.png`, `distance.png`, `search.png`, `nearest.png`
- Attestation checklist: `docs/travelmathlite/ui/attestation.md` with steps and references to UI stack and catalogue.

### Verify

- Review screenshots; confirm navbar, forms, list groups, pagination match catalogue.
- Attestation note references the images; filenames stable for audits.

---

## Summary and next steps

- Templates are cohesive and Bootstrap-only, with documented patterns and evidence.
- Next steps:
  1) Keep screenshots up to date after significant UI changes (reuse Playwright script).
  2) When adding new pages, start from the catalogue templates and avoid new CSS/JS.
  3) If a theme is needed later, introduce via variables in a future ADR without breaking markup.

---

## References

- ADR: [ADR-1.0.18 Template cohesion from Bootstrap 5 examples](../../travelmathlite/adr/adr-1.0.18-template-cohesion-from-bootstrap-examples.md)
- Briefs: [adr-1.0.18](../../travelmathlite/briefs/adr-1.0.18/)
- UI docs: [UI stack guide](../../ux/ui-stack.md), [Bootstrap component catalogue](../../ux/templates-bootstrap-catalogue.md)
- Attestation: [docs/travelmathlite/ui/attestation.md](../../travelmathlite/ui/attestation.md)
- Key templates: `templates/base.html`, `templates/includes/*`, app templates (search, accounts, calculators, airports)
