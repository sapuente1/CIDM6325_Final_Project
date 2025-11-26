# BRIEF: Build a “Fly or Drive” comparison page

Goal

- Deliver a combined “Fly or Drive” experience (from/to form) that outputs flight vs. driving distance, time, and cost with a clear recommendation, similar to the TravelMath fly-or-drive page. Keep accessibility standards from ADR-1.0.15.

Scope (single PR)

- Files to touch: `apps/calculators/forms.py` (new FlyOrDrive form), `apps/calculators/views.py`, `apps/calculators/templates/calculators/fly_or_drive.html`, `apps/calculators/partials/fly_or_drive_result.html`, `apps/calculators/urls.py` (route), optional CSS tweaks if needed.
- Behavior: New page with a single from/to form:
  - Inputs: origin, destination (city/airport/IATA/lat,lon); passengers; trip type (one-way/round); route factor; avg driving speed; vehicle fuel economy; fuel price. Defaults pulled from settings.
  - Driving outputs: distance, time, fuel cost (optionally CO₂ estimate); show assumptions (route factor, avg speed, fuel price/economy).
  - Flying outputs: nearest airports for origin/destination (top 1–2 each); flight distance; flight time = airborne time + fixed buffer (e.g., 90 min) + optional layover penalty if nearest airports differ; flight cost = per-mile/km heuristic × passengers (configurable).
  - Recommendation: “Fly” vs “Drive” based on total cost/time with a one-line rationale (e.g., “Drive is cheaper by $X but slower by Y hours”).
- UX: mirror the TravelMath fly-or-drive feel—clear from/to form, a summary header (distance, time, cost for each mode), and a recommendation block, plus a detail section with assumptions.
- Non-goals: Real routing APIs, live fares, booking links.

Standards

- Commits: conventional (feat/docs/chore).
- No secrets; env via settings.
- Django tests: use unittest/Django TestCase (no pytest). Add a basic view test to ensure the page renders, validates inputs, and produces both flight/driving outputs.
- Accessibility: labels, describedby for help/errors, aria-live on results; reuse focus/contrast styles from ADR-1.0.15.

Acceptance

- User flow: From a single form, user can submit origin/destination and see both fly vs. drive results plus a recommendation on one page, with assumptions displayed.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Create a fly_or_drive form/view/template that takes origin/destination, passengers, trip type, fuel economy/price, route factor, avg speed; compute driving distance/time/cost and flight distance/time/cost (nearest airports, buffer, per-mile fare) and render a recommendation with assumptions."
- "Add a new URL `calculators/fly-or-drive/` and keep CTAs on home/calculators pages pointing to it."
