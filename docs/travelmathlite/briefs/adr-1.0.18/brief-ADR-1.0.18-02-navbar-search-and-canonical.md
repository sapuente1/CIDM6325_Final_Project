# BRIEF: Navbar search + canonical/pagination patterns

Goal

- Implement ADR-1.0.18 navbar/search patterns: brand-left navbar with search form GET to `search:index`, preserving `q`, and canonical block per ADR-1.0.4. Ensure pagination uses Bootstrap `.pagination` and keeps the query string.

Scope (single PR)

- Files to touch: `templates/includes/navbar.html`, `templates/includes/pagination.html`, search templates (`apps/search/templates/search/results.html`), any page using pagination. Canonical block in templates where needed.
- Non-goals: Search view logic; API changes; new styling beyond Bootstrap utilities.

Standards

- Commits: conventional (feat/chore/docs).
- No secrets; env via settings.
- Django tests: optional template asserts for canonical link, navbar form action, pagination markup.

Acceptance

- User flow: Navbar search submits via GET to `search:index` and retains `q` in the input; canonical link renders on results; pagination uses Bootstrap markup and preserves `q/page`.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Update navbar include so search form GETs to search:index, keeps q value, and matches Bootstrap navbar example."
- "Ensure pagination include uses Bootstrap .pagination and appends existing query parameters."
