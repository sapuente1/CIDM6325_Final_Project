# BRIEF: Build cost calculations slice

Goal
- Implement cost-of-driving calculations addressing PRD §4 F-003.

Scope (single PR)
- Files to touch: `apps/calculators/costs.py`, unit tests.
- Non-goals: Form integration, HTMX partials.

Standards
- Commits: conventional style (feat/fix/docs/refactor/test/chore).
- No secrets; env via settings.
- Django tests: use unittest/Django TestCase (no pytest).
- Type hints on new code; docstrings on public functions; PEP 8.

Acceptance
- User flow: Given driving distance, fuel economy, and fuel price, compute total fuel cost.
- Function uses defaults from settings but accepts overrides.
- Support multiple units (L/100km, MPG, price per liter/gallon).
- Include migration? no
- Update docs & PR checklist.

Deliverables
- [ ] `calculators/costs.py` module with functions:
  - `calculate_fuel_cost(distance_km: float, fuel_economy_l_per_100km: float = None, fuel_price_per_liter: float = None) -> float`
  - `mpg_to_l_per_100km(mpg: float) -> float`
  - `l_per_100km_to_mpg(l_per_100km: float) -> float`
  - `gallons_to_liters(gallons: float) -> float`
  - `liters_to_gallons(liters: float) -> float`
- [ ] Default values pulled from Django settings
- [ ] Unit tests with known scenarios:
  - 100 km drive with 7.5 L/100km at €1.50/L = €11.25
  - Test with override values
  - Test unit conversions (MPG ↔ L/100km)
- [ ] Test invariant: cost is deterministic for given inputs

Prompts for Copilot
- "Generate a Python module `calculators/costs.py` for cost-of-driving calculations. Function should accept distance in km, fuel economy in L/100km (with default from Django settings.FUEL_ECONOMY_L_PER_100KM), and fuel price per liter (with default from settings.FUEL_PRICE_PER_LITER). Include type hints and docstrings."
- "Add unit conversion functions for MPG ↔ L/100km and gallons ↔ liters with proper formulas."
- "Create Django TestCase for cost calculations with known scenarios. Test defaults from settings and test with override values."
- "Ensure cost calculation is deterministic and returns float rounded to 2 decimal places."
- "Propose commit messages for cost calculations implementation."

---
ADR: adr-1.0.2-geo-calculation-methods.md
PRD: §4 F-003, FR-F-003-1
Issue: #TODO
