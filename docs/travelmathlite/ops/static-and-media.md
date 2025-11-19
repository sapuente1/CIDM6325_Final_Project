# Static and Media (Ops)

This document explains the layout and operator steps for static assets and media in TravelMathLite.

Folder layout (defaults)

- `travelmathlite/static/` — place design and vendor source files (CSS, JS, images). Example: `travelmathlite/static/vendor/bootstrap/` and `travelmathlite/static/img/`.
- `travelmathlite/staticfiles/` — default `STATIC_ROOT` target where `collectstatic` places compiled/collected assets for deployment. This path can be overridden with `STATIC_ROOT` env var.
- `travelmathlite/media/` — `MEDIA_ROOT` for user-uploaded content (avatars, uploaded images). This path can be overridden with `MEDIA_ROOT` env var.

Developer workflow (local)

1. Add vendor or site assets under `travelmathlite/static/` in the appropriate subfolders. For example, put `bootstrap.min.css` at `static/vendor/bootstrap/css/bootstrap.min.css`.
2. In templates, reference assets using the `static` template tag: `{% load static %}` and `<link href="{% static 'vendor/bootstrap/css/bootstrap.min.css' %}" rel="stylesheet">`.
3. To verify settings without writing files, run a dry-run:

```bash
# from repo root in bash
uv run python manage.py collectstatic --dry-run
```

Operator/deploy workflow

- Before deploying to a demo/prod environment, ensure `collectstatic` has run and artifacts are present under `STATIC_ROOT`.

Example deploy checklist snippet:

```bash
# Optional: export env overrides
export STATIC_ROOT=/opt/app/staticfiles
export MEDIA_ROOT=/opt/app/media
export USE_MANIFEST_STATIC=1  # enable only when also configuring WhiteNoise/Manifest

# Run collectstatic and capture transcript for attestation
uv run python manage.py collectstatic --noinput | tee collectstatic-$(date +%Y%m%d-%H%M%S).log
```

Notes & guidance

- For course/demo deployments we use WhiteNoise + `ManifestStaticFilesStorage` in later ADRs. For now, ensure local templates do not point to external CDNs if you want fully offline demos; store vendor files under `static/vendor/`.
- Keep vendor assets small. If replacing with upstream distribution, prefer the minified bundles.
- `media/` is in `.gitignore`; do not commit uploaded user files. Use `media/.gitkeep` to ensure the folder is present on disk if needed.

Troubleshooting

- If `collectstatic` reports missing files referenced in templates, double-check the `{% static %}` path and that files exist under `travelmathlite/static/` or another `STATICFILES_DIRS` path.
- If templates still load CDN assets, ensure you've removed the CDN links and replaced them with `{% static %}` references, then run `collectstatic`.

Evidence and attestation

- Save the `collectstatic` log and any screenshots of the site showing local assets under `docs/travelmathlite/screenshots/` for ADR evidence.
