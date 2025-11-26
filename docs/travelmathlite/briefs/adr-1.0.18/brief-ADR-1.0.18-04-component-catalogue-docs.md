# BRIEF: Document Bootstrap component catalogue for templates

Goal

- Create documentation that maps the chosen Bootstrap examples (Album, Navbar, Sticky footer, List group, Pagination, Forms, Tables) to our templates, per ADR-1.0.18. Include snippets and links to source examples.

Scope (single PR)

- Files to touch: `docs/ux/templates-bootstrap-catalogue.md` (new or updated), optionally link from `docs/ux/ui-stack.md` or README.
- Non-goals: Code changes in templates; adding new CSS/JS.

Standards

- Commits: conventional (docs).
- No secrets; env via settings.
- Tests: N/A (docs).

Acceptance

- User flow: Contributors can read the catalogue to know which Bootstrap components to use for pages (navbar/footer/cards/list groups/tables/pagination/forms) and find links to official examples. Snippets reflect current templates.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Draft a component catalogue doc mapping Bootstrap examples to our templates; include snippets and links."
- "Add a short link from the UI stack guide or README to the catalogue."
