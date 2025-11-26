# BRIEF: Layout includes (navbar, footer, alerts/pagination) with Bootstrap patterns

Goal

- Create shared includes for navbar, footer, and common UI fragments (alerts, pagination) using Bootstrap 5 patterns and accessible markup per ADR-1.0.17.

Scope (single PR)

- Files to touch: `travelmathlite/templates/includes/navbar.html`, `.../footer.html`, `.../alerts.html`, `.../pagination.html`; update `base.html` to include them; optional CSS tweaks for footer spacing/sticky footer.
- Behavior: Navbar supports collapse toggle on mobile, highlights current section, and uses accessible labels; footer contains links (PRD references, ADR docs) with small text; alerts include dismiss buttons and roles; pagination uses `<nav aria-label>` and Bootstrap `.pagination`. Ensure includes are reusable across apps.
- Non-goals: New routes or content; full redesign beyond Bootstrap patterns.

Standards

- Commits: conventional (feat/chore/docs).
- No secrets; env via settings.
- Django tests: template include smoke tests optional; focus on manual verification.

Acceptance

- User flow: Navbar, footer, alerts, and pagination render consistently on all pages; mobile collapse works; aria labels present.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Create navbar/footer/alerts/pagination includes using Bootstrap 5; wire them into base.html."
- "Ensure navbar collapse button has aria-controls/expanded/label; pagination wrapped in nav with aria-label."
