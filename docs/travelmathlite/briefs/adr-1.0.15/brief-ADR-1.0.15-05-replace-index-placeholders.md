# BRIEF: Replace app index placeholders with real entry points

Goal

- Replace scaffolding copy on app index pages with useful entry points or redirects, so users land on meaningful flows (distance/cost calculators, nearest airports, trips) while retaining accessibility (headings/ARIA) per ADR-1.0.15.

Scope (single PR)

- Files to touch: `apps/base/templates/base/index.html` (+ partial), `apps/calculators/templates/calculators/index.html` (+ partial), `apps/airports/templates/airports/index.html` (+ partial), `apps/trips/templates/trips/index.html` (+ partial).
- Behavior: Add concise summaries and CTAs to primary flows (e.g., Distance/Cost calculators, Nearest airports, Saved trips) or redirect indexes to those flows. Keep headings and focus/ARIA consistent with existing templates.
- Non-goals: Changing business logic, adding new endpoints, or restyling nav.

Standards

- Commits: conventional style (feat/docs/chore as appropriate).
- No secrets; env via settings.
- Django tests: use unittest/Django TestCase (no pytest). For this slice, content changes; manual check acceptable.

Acceptance

- User flow: Visiting each app index shows meaningful content or redirects to the primary task; no placeholder text remains.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Rewrite base/calculators/airports/trips index templates with summaries + CTA buttons linking to primary flows; remove placeholder partials."
- "Optionally redirect calculators index to distance calculator; ensure headings and ARIA remain intact."
