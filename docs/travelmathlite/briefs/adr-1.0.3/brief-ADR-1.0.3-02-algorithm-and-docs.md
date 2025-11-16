# BRIEF: Build nearest-airport algorithm documentation slice

Goal

- Document nearest-airport algorithm (bounding box prefilter + haversine) addressing PRD §4 F-002, §7 NF-001.

Scope (single PR)

- Files to touch: `docs/travelmathlite/algorithms/nearest-airport.md`.
- Non-goals: App code changes; focus on docs with formulas, examples, and limitations.

Standards

- Commits: conventional style (docs).
- Clear explanations for non-technical readers; include formulas and examples.

Acceptance

- User flow: Reader understands method, defaults, and trade-offs (SQLite-first portability).
- Document includes: bounding box derivation, haversine formula, example query, unit handling, performance notes.
- Include migration? no
- Update docs & PR checklist.

Deliverables

- [ ] `docs/travelmathlite/algorithms/nearest-airport.md` with:
  - [ ] Bounding box derivation and lat/lon deltas from radius
  - [ ] Haversine formula and constants
  - [ ] Example: coordinate → top 3 airports (with distances)
  - [ ] Unit handling (km, mi) and conversion
  - [ ] Limitations; perf targets (p95 < 300 ms on sample dataset)

Prompts for Copilot

- "Generate `docs/travelmathlite/algorithms/nearest-airport.md` explaining the bounding box + haversine approach. Include equations, rationale, an example, and limitations."
- "Add a note about index usage and why this works well on SQLite without PostGIS."

Summary

- Status: Planned — algorithms doc only.
- Files: `docs/travelmathlite/algorithms/nearest-airport.md`.
- Tests: N/A (documentation).
- Issue: #TODO

---
ADR: adr-1.0.3-nearest-airport-lookup-implementation.md
PRD: §4 F-002; §7 NF-001
Requirements: FR-F-002-1
