# Tutorial: Static, media, and asset pipeline (ADR-1.0.7)

Goal

- Teach how to implement a simple, course-friendly static & media pipeline for a Django app: local vendor assets, collectstatic, optional Manifest+WhiteNoise for demo/prod, an avatar upload flow, automation for collectstatic, and tests/visual attestation. This tutorial follows the briefs in `docs/travelmathlite/briefs/adr-1.0.7/`.

Prerequisites

- Python 3.12, virtualenv; repo checked out at project root.
- Project tooling: `uv` helper available (recommended). Activate the project's virtualenv before running commands:

```bash
source .venv/Scripts/activate  # Windows bash-style, adjust if needed
```

- Familiarity with Django basics (models, templates, management commands).

Overview (Sections)

- Static & media folders + base template (brief-01)
- WhiteNoise + ManifestStaticFilesStorage (brief-02)
- Media / avatar upload flow (brief-03)
- Collectstatic automation + logs (brief-04)
- Tests + visual attestation (brief-05)

Section 1 — Static & media folders + base template

Brief context and goal

- Replace CDN references with local vendor files; configure `STATIC_URL`, `STATICFILES_DIRS`, `STATIC_ROOT`, `MEDIA_URL`, and `MEDIA_ROOT` so `collectstatic` can gather assets for deployment.

Relevant concepts (brief summary)

- Django `static` template tag: use `{% load static %}` and `static('path')` to reference assets.
- `STATICFILES_DIRS` is where you keep source assets during development; `STATIC_ROOT` is the single folder `collectstatic` will write to for deploys.

Implementation steps

- Update settings (`travelmathlite/core/settings.py`):

```py
# static
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# media
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

- Move or add vendor files under `travelmathlite/static/vendor/` (e.g., `vendor/bootstrap/css/bootstrap.min.css`).

- Update templates to use `{% load static %}` and reference local assets:

```django
{% load static %}
<link rel="stylesheet" href="{% static 'vendor/bootstrap/css/bootstrap.min.css' %}">
```

- Verify discovery with a dry-run:

```bash
uv run python manage.py collectstatic --dry-run
```

Verification

- `collectstatic --dry-run` should list files under `travelmathlite/static/` and show where they would be copied.
- The development server serves media from `MEDIA_URL` when `DEBUG=True` (no extra infra required).

Section 2 — WhiteNoise + Manifest storage (production-like)

Brief context and goal

- Produce hashed filenames for cache-busting using `ManifestStaticFilesStorage` and serve them from the Django process using WhiteNoise for demo/prod setups.

Relevant concepts

- `ManifestStaticFilesStorage` rewrites filenames and emits `staticfiles.json` (manifest) mapping original paths to hashed versions.
- WhiteNoise middleware serves static files directly from the Django process (good for demos without CDN/nginx).

Implementation steps

- Add dependency in `pyproject.toml` (if not already present): `whitenoise`.

- In `travelmathlite/core/settings.py` insert WhiteNoise middleware after `SecurityMiddleware` and conditionally set `STATICFILES_STORAGE`:

```py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ...
]

USE_MANIFEST_STATIC = os.environ.get('USE_MANIFEST_STATIC') == '1'
if USE_MANIFEST_STATIC or not DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
```

- Optionally wrap WSGI with WhiteNoise if using certain server entrypoints (brief includes examples for `core/wsgi.py`).

- Generate the manifest in a production-like run (CI or locally with DEBUG=False):

```bash
# Example (CI-like):
DEBUG=False USE_MANIFEST_STATIC=1 uv run python manage.py collectstatic --noinput
```

Verification

- `staticfiles.json` should appear under `STATIC_ROOT` and `collectstatic` output should show hashed filenames.
- Templates that use `{% static %}` will resolve to hashed filenames when `STATICFILES_STORAGE` is the manifest storage.

Section 3 — Media and avatar upload flow

Brief context and goal

- Allow authenticated users to upload avatars stored under `MEDIA_ROOT/avatars/`, with an env toggle to enable/disable the feature for demos.

Relevant concepts

- Use Django `ImageField` (requires `Pillow`) and `OneToOneField` for `Profile` pattern.
- Use `override_settings(MEDIA_ROOT=tmpdir)` in tests to avoid polluting the repo.

Implementation steps

- Add `Pillow` to dependencies.

- Create `apps/accounts/models.py`:

```py
from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"Profile({self.user.username})"
```

- Auto-create profile via `post_save` signal, add a `ProfileForm` (ModelForm), and a `ProfileUpdateView` (CBV `UpdateView` with `LoginRequiredMixin`). Wire up `urls.py` to `/accounts/profile/`.

- Templates: show avatar if present (`{% if user.profile.avatar %}`) and use a fallback static placeholder.

- Create and apply migrations:

```bash
uv run python manage.py makemigrations accounts
uv run python manage.py migrate
```

Verification

- Log in and visit `/accounts/profile/` to upload an image; verify the file lands under `travelmathlite/media/avatars/` and the template shows it.
- Run the profile test that overrides `MEDIA_ROOT` to ensure no repo files are written during tests.

Section 4 — Collectstatic automation and docs

Brief context and goal

- Provide a single, reproducible command to run `collectstatic` across local, CI, and deployments; capture logs and produce a concise summary for ADR evidence.

Implementation steps

- We implemented a Python helper: `travelmathlite/scripts/run_collectstatic.py`. It runs `collectstatic` in-process (via `django.setup()` + `call_command('collectstatic', ...)`), supports `--dry-run`, `--clear`, `--noinput`, `--settings`, `--log-dir`, and `--archive-logs`, and writes a timestamped log plus a `collectstatic-summary-*.md` into `docs/travelmathlite/ops/logs/` by default (repo-root anchored).

- How to use the helper (repo root):

```bash
uv run python travelmathlite/scripts/run_collectstatic.py --noinput --archive-logs
```

- CI snippet (example uses GitHub Actions) is included in `docs/travelmathlite/ops/static-and-media.md` — it runs the helper with `DEBUG=False` and `USE_MANIFEST_STATIC=1` and uploads the logs as artifacts.

Verification

- After a CI run or local prod-like run, confirm `docs/travelmathlite/ops/logs/collectstatic-summary-*.md` exists and `staticfiles.json` is present under `STATIC_ROOT`.

Section 5 — Tests and visual attestation

Brief context and goal

- Add unit tests that assert static URL behavior and add a Playwright-based visual check that captures a screenshot and the static asset links for attestation.

Implementation steps

- Unit tests added: `apps/base/tests/test_static_pipeline.py` — covers static URL resolution without a manifest and mocked manifest behavior by patching `staticfiles_storage.url`.

- Visual check script added: `travelmathlite/scripts/visual_checks/static_pipeline_check.py` — uses Playwright to capture screenshots and list static asset `href`/`src` values.

How to run tests & visual check

```bash
# unit tests
uv run python manage.py test apps.base.tests.test_static_pipeline

# visual check (requires Playwright browsers installed)
pip install playwright
playwright install
uv run python manage.py runserver  # in other terminal
uv run python travelmathlite/scripts/visual_checks/static_pipeline_check.py --url http://127.0.0.1:8000
```

Verification

- Unit tests pass on CI.
- Visual artifacts (PNG + links file) are saved under `travelmathlite/screenshots/static-pipeline/` and can be attached to ADR evidence.

Summary and next steps

- This tutorial walked through the ADR-1.0.7 implementation: static/media layout, manifest + WhiteNoise, avatar uploads, collectstatic automation, and tests/visual attestation.
- Next improvements:
  - Replace placeholder vendor files with official minified Bootstrap bundles.
  - Add more integration tests that run `collectstatic` with `DEBUG=False` in a disposable environment.
  - Add Playwright CI job to capture screenshots on each release.

References

- ADR: `docs/travelmathlite/adr/adr-1.0.7-static-media-and-asset-pipeline.md`
- Briefs: `docs/travelmathlite/briefs/adr-1.0.7/` (01–05)
- Django docs: [https://docs.djangoproject.com/](https://docs.djangoproject.com/)
- Understand Django (Matt Layman): [https://www.mattlayman.com/understand-django/](https://www.mattlayman.com/understand-django/)
- WhiteNoise: [http://whitenoise.evans.io/](http://whitenoise.evans.io/)
- Playwright: [https://playwright.dev/python/](https://playwright.dev/python/)
