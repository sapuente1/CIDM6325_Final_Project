# Tutorial: ADR-1.0.8 — Settings configuration and secrets

This tutorial teaches the implementation and reasoning for ADR-1.0.8 (Settings configuration and secrets). It follows the briefs and provides step-by-step instructions, embedded documentation context, code snippets, and verification steps.

## Goals and context

- ADR: `docs/travelmathlite/adr/adr-1.0.8-settings-configuration-and-secrets.md`
- Briefs: `docs/travelmathlite/briefs/adr-1.0.8/`

Goal: Split Django settings into `base`, `local`, and `prod` modules, load configuration from environment with `django-environ`, enforce secure production defaults, and provide docs and tests.

## Prereqs

- `uv` available and configured for this repo.
- Project root: `C:/Users/Jeff/source/repos/courses/CIDM6325`
- Python venv managed by `uv` (use `uv run`/`uv add`/`uv sync` as shown).

## 1) Settings split (brief-01)

Brief objective

- Create `core/settings/{base.py, local.py, prod.py}` with shared defaults in `base.py` and environment-driven overrides.

Why this matters (Django context)

- Splitting settings helps make production vs. development behavior explicit. Django's `settings` is a standard Python module; importing different modules via `DJANGO_SETTINGS_MODULE` controls app behavior.

Implementation steps

1. Create a settings package at `travelmathlite/core/settings/__init__.py` that re-exports a default (e.g., `local` for developer convenience):

```py
# travelmathlite/core/settings/__init__.py
from .local import *  # default to local for dev
```

2. Add `base.py` containing shared settings and an `environ.Env()` instance to read variables:

```py
# travelmathlite/core/settings/base.py
import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parents[2]
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY', default='dev-secret')
DEBUG = env.bool('DEBUG', default=False)

INSTALLED_APPS = [
    # ... keep existing apps
]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

```

3. Add `local.py` to enable debug and local DB defaults:

```py
# travelmathlite/core/settings/local.py
from .base import *
DEBUG = True
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3','NAME': BASE_DIR / 'db.sqlite3'}}
```

4. Add `prod.py` to enforce prod defaults and security flags:

```py
# travelmathlite/core/settings/prod.py
from .base import *
DEBUG = False
SECRET_KEY = env('SECRET_KEY')  # required
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware', *MIDDLEWARE]
# WhiteNoise integration example
USE_WHITENOISE = True
if USE_WHITENOISE:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

```

Verification

Run a quick import to verify modules load in the `uv` environment:

```bash
uv run python -c "import importlib; importlib.import_module('core.settings')"
```

Expected: no exceptions.

## 2) Environment variables and docs (brief-02)

Brief objective

- Provide `.env.example` and docs showing which env vars are required and how to run with different `DJANGO_SETTINGS_MODULE` values.

Implementation steps

1. Create `travelmathlite/.env.example` with keys:

```text
# .env.example
SECRET_KEY=changeme
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

2. Update `docs/travelmathlite/ops/settings.md` to document running locally vs. prod. Example run commands:

```bash
# local (default)
uv run python travelmathlite/manage.py runserver

# prod (example)
DJANGO_SETTINGS_MODULE=core.settings.prod uv run python travelmathlite/manage.py check_settings
```

Verification

Show that `.env` variables are read by printing a value:

```bash
uv run python -c "import environ,os; env=environ.Env(); env.read_env('travelmathlite/.env'); print(env('SECRET_KEY'))"
```

## 3) Prod security + WhiteNoise (brief-03)

Brief objective

- Harden production settings and enable WhiteNoise for static file serving.

Implementation steps

1. Ensure `whitenoise` is installed via `uv add whitenoise` and `MIDDLEWARE` includes `whitenoise.middleware.WhiteNoiseMiddleware` as shown earlier.

2. Configure `STATIC_ROOT` in `base.py` and run collectstatic during deployment:

```bash
uv run python travelmathlite/manage.py collectstatic --noinput
```

Verification

Run `collectstatic --dry-run` first:

```bash
uv run python travelmathlite/manage.py collectstatic --dry-run
```

Confirm no errors and static files are discoverable.

## 4) Tests and invariants (brief-04)

Brief objective

- Add lightweight tests that import `core.settings` variants and assert `DEBUG` and security flags.

Implementation steps

1. Create tests under `travelmathlite/core/tests/test_settings_local.py` and `test_settings_prod.py` using Django `TestCase` or simple import assertions.

2. Run the tests with `uv`:

```bash
uv run python travelmathlite/manage.py test core.tests.test_settings_prod core.tests.test_settings_local
```

Verification

Both tests should pass and CI should install dependencies using `uv` before running the test suite.

## Summary and next steps

- Tutorial complete: settings split, `.env.example`, prod security with WhiteNoise, and tests.
- Next: add this tutorial to the ADR deliverables, open a PR, and ensure CI runs `uv sync`/installs deps from `pyproject.toml` before tests.

## References

- ADR: `docs/travelmathlite/adr/adr-1.0.8-settings-configuration-and-secrets.md`
- Briefs: `docs/travelmathlite/briefs/adr-1.0.8/`
- Django docs: <https://docs.djangoproject.com/>
- django-environ: <https://pypi.org/project/django-environ/>
- WhiteNoise: <http://whitenoise.evans.io/>

