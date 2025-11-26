# Tutorial: ADR-1.0.15 Accessibility Standards

**Date:** November 27, 2025  
**ADR Reference:** [ADR-1.0.15 Accessibility standards](../../travelmathlite/adr/adr-1.0.15-accessibility-standards.md)  
**Briefs:** [adr-1.0.15 briefs](../../travelmathlite/briefs/adr-1.0.15/)  
**PRD trace:** §7 Accessibility (F-007/F-008, NF-002)  
**Acceptance hooks:** FR-F-007-1 (contrast/focus/ARIA), FR-F-008-1 (search templates accessible), NF-002 (axe/manual checks)

---

## Overview

ADR-1.0.15 raises the bar for accessibility: WCAG AA contrast, visible focus, labeled forms with ARIA, keyboard/HTMX focus management, documented checks, and removal of placeholder pages. This tutorial follows each brief to show what changed, why it matters, and how to verify.

**Learning Objectives**
- Apply WCAG AA contrast and visible focus rings on interactive elements.
- Ensure form fields use label/for, describedby/error hints, and aria-live regions for updates.
- Manage keyboard and HTMX focus so content swaps stay reachable.
- Run axe + manual checks and document the runbook.
- Replace scaffolded index pages with meaningful, accessible CTAs.
- Surface the “Fly or Drive” comparison with accessible forms and results.

**Prerequisites**
- TravelMathLite running locally (`uv run python travelmathlite/manage.py runserver` with `core.settings.local`).
- Ability to inspect templates/CSS and run axe/keyboard checks.

**How to use this tutorial**
- Work section by section (Brief 01 → 06). Each includes context, concepts, steps, code refs, and verification.
- Keep `docs/travelmathlite/ops/deploy.md` and `docs/ux/accessibility.md` handy for runbooks/checklists.

---

## Section 1 — Contrast and focus styling (Brief 01)

**Context:** [brief-ADR-1.0.15-01-contrast-and-focus.md](../../travelmathlite/briefs/adr-1.0.15/brief-ADR-1.0.15-01-contrast-and-focus.md)  
**Why it matters:** WCAG AA requires sufficient contrast and clearly visible focus states. Bootstrap defaults can be borderline depending on brand colors.

### Concepts (Django/Bootstrap)
- Bootstrap exposes CSS custom properties (`--bs-success`, `--bs-focus-ring-color`) to tune palette and focus globally.
- WCAG AA contrast: 4.5:1 for normal text; visible focus indicator for all interactive elements.

### Implementation
- Added an accessibility override stylesheet and load it after Bootstrap:
  - `travelmathlite/templates/base.html` now includes `{% static 'css/accessibility.css' %}`.
- Contrast and focus tokens:
  - `travelmathlite/static/css/accessibility.css` sets a darker success palette (`--bs-success`) and a high-visibility focus ring (`--bs-focus-ring-color` + explicit outline).
  - Applies focus outlines to links, buttons, form controls, nav items, and skip links.

### Verification
- Tab through nav/search/buttons: focus ring is obvious on light backgrounds.
- Check success/outline-success buttons: text contrasts on hover/active states.
- Axe should report no “focus visible” or “low contrast” issues on primary UI elements.

---

## Section 2 — Form labels and ARIA (Brief 02)

**Context:** [brief-ADR-1.0.15-02-form-labels-and-aria.md](../../travelmathlite/briefs/adr-1.0.15/brief-ADR-1.0.15-02-form-labels-and-aria.md)  
**Why it matters:** Screen readers need label/for pairs and describedby links to helper/error text; aria-live regions announce updates.

### Concepts (Django templates)
- Use `label` + `for` tied to field `id_for_label`.
- `aria-describedby` can reference help + error ids; alerts with `aria-live="assertive"` for non-field errors.
- HTMX/partials should keep regions keyboard-reachable.

### Implementation highlights
- Navbar search: hidden label + hint, describedby, visible focus (`travelmathlite/templates/base.html`).
- Search page: labeled form with help/status, results region `aria-live="polite"` (`apps/search/templates/search/results.html`).
- Auth forms (login/signup): help/error ids wired via describedby; alerts marked assertive (`apps/accounts/templates/registration/*.html`).
- Calculators (distance/cost): labeled fields with help, describedby, aria-live results (`apps/calculators/templates/calculators/*calculator.html`).
- Airports nearest: full labels/help/errors with describedby, results region aria-live (`apps/airports/templates/airports/nearest.html`).
- Form widgets set classes/describedby defaults in `apps/calculators/forms.py` and `apps/airports/forms.py`.

### Verification
- Screen reader reads labels and help; errors announce via describedby/alerts.
- Axe should not flag missing labels/aria-describedby on forms.
- HTMX swaps keep focusable regions (results containers have tabindex/focus via existing base script).

---

## Section 3 — Keyboard navigation and HTMX focus (Brief 03)

**Context:** [brief-ADR-1.0.15-03-keyboard-and-htmx-focus.md](../../travelmathlite/briefs/adr-1.0.15/brief-ADR-1.0.15-03-keyboard-and-htmx-focus.md)  
**Why it matters:** Keyboard users must reach nav, forms, and dynamically updated regions.

### Concepts
- HTMX updates should move focus to the updated region or announce via `aria-live`.
- Skip links (if added) need visible focus styles; we prepped `.skip-link` styling in `accessibility.css`.

### Implementation
- Base template retains HTMX afterSwap focus script for targets with `tabindex`.
- Result containers (search/calculators/airports) marked with `aria-live="polite"` so changes are announced.
- Focus outline styles ensure visibility across nav/forms/buttons.

### Verification
- Tab order is logical through nav → search → content; after submitting HTMX forms, focus can be moved to results if `tabindex` is present.
- Axe/keyboard pass: no keyboard traps; focus remains visible.

---

## Section 4 — Axe/manual checks and docs (Brief 04)

**Context:** [brief-ADR-1.0.15-04-axe-checks-and-docs.md](../../travelmathlite/briefs/adr-1.0.15/brief-ADR-1.0.15-04-axe-checks-and-docs.md)  
**Why it matters:** NF-002 requires tool-assisted checks and a runbook.

### Implementation
- Use `docs/ux/accessibility.md` (update/run) to capture:
  - Pages to check: home, calculators (distance/cost/fly-or-drive), airports nearest, search, login/signup.
  - Steps: run axe DevTools on each page; keyboard walkthrough (nav → form → submit → results); note focus and describedby coverage.
  - Evidence: screenshots of axe reports and notes.

### Verification
- Axe reports no critical issues on key pages; manual keyboard walkthrough succeeds.
- Update the docs checklists with findings and any known issues.

---

## Section 5 — Replace index placeholders (Brief 05)

**Context:** [brief-ADR-1.0.15-05-replace-index-placeholders.md](../../travelmathlite/briefs/adr-1.0.15/brief-ADR-1.0.15-05-replace-index-placeholders.md)  
**Why it matters:** Landing pages should guide users, not show scaffolding.

### Implementation
- `apps/base/templates/base/index.html`: cards for trip calculators, drive vs fly, nearest airports, search, saved trips.
- `apps/calculators/templates/calculators/index.html`: cards for distance, cost, and drive vs fly.
- `apps/airports/templates/airports/index.html`: nearest-airports CTA + search link; partial with usage tips.
- `apps/trips/templates/trips/index.html`: CTA for saved calculations; partial updated.
- Removed placeholder copy in `_welcome.html` partials.

### Verification
- No placeholder text remains; CTAs link to primary flows.
- Headings and buttons are reachable and have visible focus.

---

## Section 6 — Fly or Drive experience (Brief 06)

**Context:** [brief-ADR-1.0.15-06-fly-or-drive.md](../../travelmathlite/briefs/adr-1.0.15/brief-ADR-1.0.15-06-fly-or-drive.md)  
**Why it matters:** Mirrors TravelMath’s fly-or-drive comparison with accessible forms/results.

### Implementation
- New route/page: `/calculators/fly-or-drive/` with `FlyOrDriveForm` + `FlyOrDriveView`.
- Inputs: origin/destination, trip type, passengers, route factor, avg speed, fuel economy, fuel price, fare per km.
- Driving outputs: distance, time, fuel cost (trip-multiplied), assumptions shown.
- Flying outputs: nearest origin/destination airports, flight distance, buffered time (cruise + 1.5h), fare heuristic × passengers × trip type.
- Recommendation: “Fly” or “Drive” with cost/time rationale; results in `partials/fly_or_drive_result.html`.
- CTAs: home/calculators cards link to the new page.

### Verification
- Submit sample (e.g., “AMA” to “DAL”): see both driving and flying cards plus recommendation; focus remains visible; aria-live results present.
- Basic view test: `uv run python travelmathlite/manage.py test apps.calculators.tests.test_fly_or_drive`.

---

## Summary and next steps

- Accessibility standards implemented: contrast/focus, ARIA labels/announcements, keyboard/HTMX focus, runbook for axe/manual checks, meaningful landing pages, and a surfaced fly-or-drive flow.
- Next steps:
  1) Run axe + keyboard checks per docs and capture evidence.
  2) Tune heuristics (fare per km, buffers) if needed; document assumptions in `docs/ux/accessibility.md` or feature notes.
  3) Add a skip link if desired; styling already prepared in `accessibility.css`.

---

## References

- ADR-1.0.15 Accessibility standards  
- Django forms and template ARIA guidance: https://docs.djangoproject.com/en/stable/ref/forms/renderers/  
- Bootstrap accessibility and focus: https://getbootstrap.com/docs/5.3/getting-started/accessibility/  
- Axe DevTools: https://www.deque.com/axe/devtools/  
- HTMX docs (events/focus): https://htmx.org/docs/  
- TravelMath fly-or-drive example: https://www.travelmath.com/fly-or-drive/
