# BRIEF: Ongoing Tutorials for Each ADR

Goal

- After each ADR is completed, produce a concise tutorial (Markdown) that teaches the slice using Matt Layman’s "Understand Django" and official docs (Django, Bootstrap, HTMX) as anchors.

Scope (recurring per-ADR)

- Files to touch: `docs/travelmathlite_tutorials/adr-<id>/tutorial-ADR-<id>-<slug>.md`.
- Inputs: ADR text and the related briefs in `docs/travelmathlite/briefs/adr-<id>/`.
- Non-goals: Re-implement the feature; focus on explaining and guiding.

Standards

- Commits: conventional style (docs).
- Clear links to official documentation (Django, Bootstrap, HTMX) and to Layman’s book sections.
- Keep it short and practical; show minimal code snippets and commands.

Acceptance

- A Markdown tutorial exists per ADR under `docs/travelmathlite_tutorials/adr-<id>/`.
- Tutorial references: relevant ADR, briefs, Django docs, Bootstrap, HTMX, and Matt Layman.
- Tutorial includes: goals, prerequisites, step outline, key snippets, and "How to Verify".
- Include migration? no
- Update docs & PR checklist.

Deliverables (per ADR)

- [ ] `docs/travelmathlite_tutorials/adr-<id>/tutorial-ADR-<id>-<slug>.md`
  - [ ] Goals and context (link ADR + briefs)
  - [ ] Prereqs (env, dataset, settings)
  - [ ] Steps guided by the briefs
  - [ ] References (Django/Layman/Bootstrap/HTMX)
  - [ ] How to Verify (tests/URLs/expected output)

Prompts for Copilot

- "Generate a tutorial Markdown for ADR-ADRID by reading docs/travelmathlite/adr/ (the ADR file for ADRID) and briefs in docs/travelmathlite/briefs/ADRDIR/. Keep it concise, with links to Django docs, Bootstrap, and HTMX, and include pointers to relevant chapters from Matt Layman’s Understand Django."
- "Draft code snippets that mirror what was implemented, with copy-pasteable commands. Include a short ‘How to Verify’ section with URLs or tests to run."

Summary

- Status: Ongoing — run after each ADR merge.
- Files: `docs/travelmathlite_tutorials/adr-<id>/*.md`.
- Tests: N/A (docs).
- Issue: optional per ADR.

---
Resources

- [Understand Django (Matt Layman)](https://www.mattlayman.com/understand-django/)
- [Django documentation](https://docs.djangoproject.com/)
- [Bootstrap documentation](https://getbootstrap.com/docs/)
- [HTMX documentation](https://htmx.org/docs/)
