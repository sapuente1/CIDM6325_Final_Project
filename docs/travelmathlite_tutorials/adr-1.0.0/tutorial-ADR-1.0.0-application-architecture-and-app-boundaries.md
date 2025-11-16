# Tutorial: ADR-1.0.0 Application Architecture & App Boundaries

Goal

- Understand the multi-app architecture, app boundaries, namespaced URLs, and template organization established by ADR-1.0.0.

Context

- ADR: `docs/travelmathlite/adr/adr-1.0.0-application-architecture-and-app-boundaries.md`
- Briefs: `docs/travelmathlite/briefs/adr-1.0.0/`
- Apps: `travelmathlite/apps/*` (calculators, airports, accounts, trips, search, base)

Prerequisites

- TravelMathLite project set up (use `docs/travelmathlite/django-project-setup-with-uv.md`)

Steps (guided by briefs)

1) App scaffolding (Brief 01)
   - Verify each app has `apps.py`, `urls.py`, `views.py`, and `templates/<app>/`.
   - INSTALLED_APPS includes all domain apps.
2) Settings (Brief 02)
   - Open `travelmathlite/core/settings.py` and review `INSTALLED_APPS` and template settings `DIRS`/`APP_DIRS`.
3) Project URLs (Brief 03)
   - Open `travelmathlite/core/urls.py` and verify namespaced includes for each app.
   - Try reversing URLs in a shell: `reverse('calculators:index')`, `reverse('airports:index')`.
4) Templates organization (Brief 04)
   - Confirm base layout at `travelmathlite/templates/base.html` and per-app templates under `templates/<app>/`.
5) Tests (Brief 05)
   - Run URL reverse and template smoke tests.
6) Docs (Brief 06)
   - Read `docs/travelmathlite/architecture/app-layout.md` if present for rationale and patterns.

Commands

```bash
uv run python travelmathlite/manage.py shell -c "from django.urls import reverse; print(reverse('calculators:index')); print(reverse('airports:index'))"
uv run python travelmathlite/manage.py test
```

How to Verify

- Visiting the app roots via navbar links works (`/calculators/`, `/airports/`, etc.).
- URL reversing succeeds for each app namespace.
- Templates render using `base.html`.

References

- [Understand Django (Matt Layman)](https://www.mattlayman.com/understand-django/)
  - Suggested topics: Project layout, Apps, URLs, Templates
- [Django documentation](https://docs.djangoproject.com/)
- [Bootstrap documentation](https://getbootstrap.com/docs/)
- [HTMX documentation](https://htmx.org/docs/)
