# BRIEF: Build axe/manual checks and accessibility docs slice

Goal

- Run axe DevTools + manual keyboard/screen reader spot-checks on key pages and document guidance in `docs/ux/accessibility.md`, fulfilling PRD §7 (NF-002) and ADR-1.0.15 acceptance.

Scope (single PR)

- Files to touch: `docs/ux/accessibility.md` (add checklist/runbook), optionally README link; add screenshots/notes folder if needed; no code changes unless small fixes emerge from findings.
- Behavior: Define the page list to check (home/search/results/account), run axe DevTools, capture screenshots of reports, document keyboard walkthrough steps, and note focus/ARIA expectations (tie back to Briefs 01-03).
- Non-goals: Adding automated CI scanners; refactoring templates beyond quick fixes.

Standards

- Commits: conventional style (docs/chore/fix for any quick fixes).
- No secrets; env via settings.
- Django tests: unittest/Django TestCase (no pytest). This slice relies on manual/tool evidence; note results in PR.

Acceptance

- User flow: axe DevTools shows no critical violations on key pages; manual keyboard walkthrough succeeds (nav → form → submit → results).
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Draft an accessibility checklist/runbook for `docs/ux/accessibility.md` covering contrast, focus, labels, HTMX focus/announcements, and axe steps with evidence."
- "Summarize axe findings (if any) and propose quick template/CSS fixes."
