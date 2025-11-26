# BRIEF: Build contrast + focus styling slice

Goal

- Ensure WCAG AA contrast and visible focus states across the app, addressing PRD §7 (F-007/F-008) and ADR-1.0.15.

Scope (single PR)

- Files to touch: global styles (e.g., `travelmathlite/static/css/*.css` or equivalent), shared templates (base/layout), component partials where contrast is defined.
- Behavior: Verify and adjust color tokens/utility classes for text, links, buttons, and alerts to meet WCAG AA; ensure focus styles are clearly visible (outline/offset) for all interactive elements.
- Non-goals: Full redesign or component rewrites; no JS changes unless required for focus visibility.

Standards

- Commits: conventional style (chore/docs/refactor as appropriate).
- No secrets; env via settings.
- Django tests: use unittest/Django TestCase (no pytest). For this slice, visual/manual checks are acceptable.

Acceptance

- User flow: Keyboard users can see focus outlines on links, buttons, form controls, and nav elements; text and UI elements meet AA contrast on default backgrounds.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Audit CSS variables/classes for contrast; propose minimal token tweaks to hit WCAG AA for text, links, buttons, alerts."
- "Add/standardize focus outlines (outline color + offset) for interactive elements without breaking Bootstrap defaults."
