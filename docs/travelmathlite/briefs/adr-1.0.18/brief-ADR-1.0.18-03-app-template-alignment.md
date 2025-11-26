# BRIEF: Align app templates to Bootstrap catalogue patterns

Goal

- Update app index/detail templates to reuse the Bootstrap example catalogue (cards/list groups/tables/forms) with consistent container/grid spacing and optional breadcrumbs, per ADR-1.0.18. Avoid custom CSS.

Scope (single PR)

- Files to touch: key app templates (calculators, airports, search, accounts/trips landing pages) to ensure they extend the base layout and use the chosen components (cards/list groups/tables) plus optional breadcrumbs via Bootstrap `.breadcrumb`.
- Non-goals: Backend logic; new routes; heavy redesign outside Bootstrap utilities.

Standards

- Commits: conventional (feat/chore/docs).
- No secrets; env via settings.
- Django tests: optional template render smoke; main verification is manual UI pass.

Acceptance

- User flow: App pages share consistent container spacing, component choices (cards or list groups per catalogue), and breadcrumbs where nested. No new custom CSS/JS is added.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Refactor app templates to use Bootstrap list-group or card patterns from the examples; ensure breadcrumbs are present on nested pages."
- "Verify templates extend base.html and avoid custom CSS; keep aria/label behavior intact."
