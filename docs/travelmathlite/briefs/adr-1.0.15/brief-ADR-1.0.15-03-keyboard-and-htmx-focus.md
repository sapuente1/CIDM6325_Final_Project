# BRIEF: Build keyboard navigation and HTMX focus management slice

Goal

- Guarantee keyboard navigability and sensible focus management, including HTMX-updated regions, to meet PRD §7 (F-007/F-008) and ADR-1.0.15.

Scope (single PR)

- Files to touch: navigation templates, interactive components (menus, modals if present), HTMX result/partial templates, any JS snippets that manage focus.
- Behavior: Ensure tab order is logical; add skip links if missing; focus moves to meaningful content after HTMX swaps (e.g., set focus on results heading or first interactive item); dynamic regions use `aria-live` or manual focus for announcements.
- Non-goals: Rebuilding navigation structure; adding new pages.

Standards

- Commits: conventional style (feat/chore/docs).
- No secrets; env via settings.
- Django tests: unittest/Django TestCase (no pytest). Manual/axe checks acceptable for focus, with notes in PR.

Acceptance

- User flow: Keyboard-only users can tab through nav, forms, and results in order; after HTMX updates, focus is placed on the updated region or a logical element; skip link (if present) is reachable and visible on focus.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Add a skip-to-content link and ensure it is visible on focus; verify tab order in nav."
- "After HTMX partial update, move focus to the results heading and mark the region `aria-live='polite'` (or set focus manually)."
