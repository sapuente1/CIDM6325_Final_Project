# BRIEF: Static overrides and asset versioning for Bootstrap/HTMX

Goal

- Define how we vendor/pin Bootstrap and HTMX, load overrides, and manage cache-busting/versioning per ADR-1.0.17. Document where to place custom CSS/JS.

Scope (single PR)

- Files to touch: static overrides file(s) (`travelmathlite/static/css/overrides.css` or existing), notes in README/docs, optional settings for vendored assets path.
- Behavior: Pin Bootstrap/HTMX versions (documented), load custom overrides after Bootstrap, and define how to switch CDN vs. local vendored assets. Clarify cache-busting approach (ManifestStaticFilesStorage already in place). Ensure overrides are minimal and documented.
- Non-goals: Introducing build tools or new asset pipeline; theming beyond light overrides.

Standards

- Commits: conventional (docs/chore).
- No secrets; env via settings.
- Django tests: not required (docs/config only).

Acceptance

- User flow: Clear instructions for asset sourcing (CDN vs. vendored), override file location, and version pins; cache-busting documented via existing static pipeline.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Document asset pinning for Bootstrap/HTMX, where to place overrides, and how ManifestStaticFilesStorage handles cache busting."
- "If needed, add an overrides CSS stub loaded after Bootstrap."
