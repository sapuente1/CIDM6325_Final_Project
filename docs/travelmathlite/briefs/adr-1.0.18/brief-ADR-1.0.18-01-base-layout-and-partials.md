# BRIEF: Build base layout and shared partials (Bootstrap-only)

Goal

- Implement ADR-1.0.18 by aligning the global base layout and shared partials (navbar/footer/messages) to use only Bootstrap 5 example patterns—no custom CSS/JS beyond existing accessibility/override files.

Scope (single PR)

- Files to touch: `travelmathlite/templates/base.html`, `travelmathlite/templates/includes/navbar.html`, `.../footer.html`, `.../alerts.html` (or app-level partials if needed). Adjust container/grid usage to the chosen Bootstrap example (navbar + sticky footer).
- Non-goals: Theming or new routes; introducing custom CSS/JS; changing HTMX logic.

Standards

- Commits: conventional (feat/chore/docs).
- No secrets; env via settings.
- Django tests: optional template render smoke; focus on manual UI check.

Acceptance

- User flow: Base pages render with navbar, canonical block, and sticky footer using only Bootstrap classes; no new custom CSS/JS introduced.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Refactor base.html to mirror the Bootstrap navbar + sticky footer examples using only Bootstrap utilities; keep canonical block and alert include."
- "Ensure navbar toggler works with the bundle and uses aria-controls/expanded/label from the example."
