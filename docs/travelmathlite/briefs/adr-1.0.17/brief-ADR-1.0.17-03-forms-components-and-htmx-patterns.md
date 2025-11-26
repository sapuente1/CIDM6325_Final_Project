# BRIEF: Bootstrap-styled forms/components and HTMX patterns

Goal

- Standardize form styling, buttons, highlights, and HTMX partial patterns with Bootstrap 5 classes and accessible markup per ADR-1.0.17.

Scope (single PR)

- Files to touch: shared form partials (if any), key templates with forms (search, calculators, airports), HTMX partials; optional helpers for buttons/alerts/highlights.
- Behavior: Apply Bootstrap form controls (`form-control`, `form-select`, spacing classes), button variants, and alert styles; ensure highlights/pagination use Bootstrap classes; HTMX partials return valid fragments with the same styling. Preserve aria-label/ describedby per ADR-1.0.15. Add any small utility classes or snippets for consistent HTMX responses.
- Non-goals: New features; design overhaul beyond Bootstrap conventions.

Standards

- Commits: conventional (feat/chore/docs).
- No secrets; env via settings.
- Django tests: optional template render checks; primary verification via manual UI review.

Acceptance

- User flow: Forms/buttons/pagination look consistent across pages; HTMX responses mirror full-page styling; highlights use Bootstrap utilities.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Apply Bootstrap 5 classes to forms/buttons/pagination/highlights; ensure HTMX partials return the same styling as full pages."
- "Keep aria-label/ describedby intact while adding Bootstrap classes."
