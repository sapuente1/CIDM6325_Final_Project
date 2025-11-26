# BRIEF: Build form labeling and ARIA slice

Goal

- Add explicit labels, descriptions, and ARIA hooks for forms and result sections to satisfy PRD §7 (F-007/F-008) and ADR-1.0.15.

Scope (single PR)

- Files to touch: form templates and partials (search, accounts, calculators), shared form macros/components, result templates where instructions/descriptions are rendered.
- Behavior: Ensure every input/select/textarea has a visible label (`for`/`id` pairs); add `aria-describedby` for helper/error text; provide programmatic names for buttons/links; ensure form errors announce via `aria-live` or are referenced in `aria-describedby`.
- Non-goals: Changing business logic or form validation rules; adding new endpoints.

Standards

- Commits: conventional style (feat/fix/docs depending on edits).
- No secrets; env via settings.
- Django tests: use unittest/Django TestCase (no pytest). Prefer template coverage via manual/axe verification for this slice.

Acceptance

- User flow: Screen-reader users hear clear labels and descriptions for all form fields; errors/alerts are reachable via `aria-describedby` or `aria-live` regions.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Add `label`/`for` pairs and `aria-describedby` for this form template; ensure errors hook into the describedby ids."
- "Propose ARIA attributes for result summaries and alerts so screen readers announce state changes."
