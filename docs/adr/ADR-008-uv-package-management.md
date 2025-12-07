# ADR-008: UV Package Management & Project Setup

**Date**: 2025-12-07  
**Status**: Proposed  
**Related PRD**: Section 8 (Technical Requirements), Section 9 (Development Workflow)

## Context

CFMP requires modern Python package management and development tooling to align with industry best practices demonstrated in the class README.MD. The current project setup lacks standardized dependency management, development workflow automation, and code quality tools that are expected in professional Django development.

Current gaps:
- Missing `pyproject.toml` for modern Python packaging
- No UV-based dependency management (recommended in README)
- Missing Ruff integration for code formatting and linting
- No pre-commit hooks for code quality enforcement
- Inconsistent development environment setup
- Missing development vs production dependency separation

## Decision Drivers

- **Class Standards**: README emphasizes UV for fast, reproducible Python workflows
- **Industry Practices**: Modern Python projects use `pyproject.toml` and UV
- **Code Quality**: Automated formatting and linting with Ruff
- **Development Experience**: Consistent, fast environment setup
- **Academic Requirements**: Demonstrate modern Python tooling knowledge
- **Team Collaboration**: Reproducible development environments

## Options Considered

### A) Traditional pip + requirements.txt
```txt
# requirements.txt
Django==5.2.6
psycopg[binary]==3.1.13
gunicorn==21.2.0
# ... more dependencies
```

**Pros**: Familiar, simple, widely supported  
**Cons**: Slow dependency resolution, no lock files, no development/production separation

### B) Poetry + pyproject.toml
```toml
[tool.poetry]
name = "cfmp"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.12"
Django = "5.2.6"
```

**Pros**: Modern packaging, dependency groups, lock files  
**Cons**: Not specifically recommended in class, slower than UV

### C) UV + pyproject.toml (Recommended)
```toml
[project]
name = "cfmp"
version = "0.1.0"
dependencies = [
    "Django==5.2.6",
]

[dependency-groups]
dev = [
    "ruff",
    "pre-commit",
    "django-debug-toolbar",
]
```

**Pros**: Fast dependency resolution, class-recommended, modern packaging  
**Cons**: Newer tool, learning curve

## Decision

**We choose UV + pyproject.toml** because:

1. **Class Alignment**: Specifically recommended in README.MD for this course
2. **Performance**: Significantly faster dependency resolution than pip/poetry
3. **Modern Standards**: Industry-standard `pyproject.toml` configuration
4. **Development Groups**: Clean separation of development and production dependencies
5. **Professor Expectations**: Demonstrates awareness of modern Python tooling
6. **Future Proof**: UV is the emerging standard for Python package management

## Implementation Strategy

### Project Structure and Configuration

#### pyproject.toml Configuration
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "cfmp"
version = "0.1.0"
description = "Community Food Management Platform - Django web application for connecting food donors with pantries"
readme = "README.md"
license = "MIT"
requires-python = ">=3.12"
authors = [
    {name = "Steven Puente", email = "sapuente1@buffs.wtamu.edu"},
]
keywords = ["django", "food-management", "community", "donations"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Framework :: Django",
    "Framework :: Django :: 5.2",
    "Intended Audience :: Education",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
]

# Core runtime dependencies
dependencies = [
    "Django>=5.2.6,<5.3",
    "psycopg[binary]>=3.1.13",
    "django-environ>=0.11.2",
    "Pillow>=10.1.0",
    "whitenoise>=6.6.0",
    "gunicorn>=21.2.0",
    "redis>=5.0.1",
]

[dependency-groups]
# Development dependencies
dev = [
    "ruff>=0.6.9",
    "pre-commit>=3.6.0",
    "django-debug-toolbar>=4.2.0",
    "django-extensions>=3.2.3",
    "ipython>=8.18.0",
    "model-bakery>=1.17.0",
    "coverage>=7.3.0",
]

# Testing dependencies
test = [
    "pytest-django>=4.7.0",
    "pytest-cov>=4.1.0",
    "factory-boy>=3.3.0",
    "freezegun>=1.2.2",
]

# Production monitoring and security
prod = [
    "sentry-sdk[django]>=1.38.0",
    "django-csp>=3.7",
    "django-ratelimit>=4.1.0",
    "celery[redis]>=5.3.4",
]

# Documentation
docs = [
    "sphinx>=7.2.6",
    "sphinx-rtd-theme>=1.3.0",
    "django-extensions>=3.2.3",
]

[project.urls]
Homepage = "https://github.com/sapuente1/cfmp"
Repository = "https://github.com/sapuente1/cfmp"
Documentation = "https://cfmp.readthedocs.io"
"Bug Tracker" = "https://github.com/sapuente1/cfmp/issues"

[project.scripts]
cfmp = "cfmp.cli:main"

# Hatchling configuration
[tool.hatch.build.targets.wheel]
packages = ["cfmp"]

[tool.hatch.metadata]
allow-direct-references = true

# Ruff configuration for linting and formatting
[tool.ruff]
target-version = "py312"
line-length = 88
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
    "DJ",   # flake8-django
    "S",    # flake8-bandit (security)
]
ignore = [
    "E501",  # line too long (handled by formatter)
    "S101",  # use of assert (OK in tests)
    "DJ01",  # nullable CharField (sometimes OK)
]

[tool.ruff.per-file-ignores]
"*/tests/*" = ["S101", "S105", "S106"]  # Allow assert and hardcoded passwords in tests
"*/migrations/*" = ["E501", "DJ01"]     # Ignore line length and nullable in migrations
"manage.py" = ["S101"]                  # Allow assert in manage.py
"*/settings/*" = ["S105"]               # Allow hardcoded passwords in settings

[tool.ruff.isort]
known-first-party = ["cfmp"]
known-django = ["django"]
section-order = ["future", "standard-library", "django", "third-party", "first-party", "local-folder"]

# Coverage configuration
[tool.coverage.run]
source = ["cfmp"]
omit = [
    "*/migrations/*",
    "*/venv/*",
    "*/env/*",
    "manage.py",
    "*/settings/*",
    "*/tests/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\bProtocol\):",
    "@(abc\.)?abstractmethod",
]

[tool.coverage.html]
directory = "htmlcov"

# Django configuration
[tool.django-stubs]
django_settings_module = "cfmp.settings.development"

# Pytest configuration
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "cfmp.settings.test"
addopts = "--reuse-db --nomigrations"
python_files = ["test_*.py", "*_test.py", "tests.py"]
testpaths = ["tests"]
```

#### UV Workflow Scripts
```bash
#!/bin/bash
# scripts/setup-dev.sh - Development environment setup

set -e

echo "🚀 Setting up CFMP development environment..."

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# Create virtual environment
echo "🐍 Creating virtual environment..."
uv venv .venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
uv pip install -e ".[dev,test]"

# Setup pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
pre-commit install

# Setup environment file
if [ ! -f .env ]; then
    echo "📄 Creating .env file..."
    cp .env.example .env
    echo "✏️  Please edit .env file with your configuration"
fi

# Run initial migrations
echo "🗄️  Running initial migrations..."
python manage.py migrate

# Create superuser if needed
echo "👤 Creating superuser..."
python manage.py createsuperuser --noinput --username admin --email admin@example.com || true

# Run tests to verify setup
echo "🧪 Running tests to verify setup..."
python manage.py test --verbosity=2

echo "✅ Development environment setup complete!"
echo "🌟 Start the server with: python manage.py runserver"
```

#### Pre-commit Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-case-conflict
      - id: check-merge-conflict

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/adamchainz/django-upgrade
    rev: 1.15.0
    hooks:
      - id: django-upgrade
        args: [--target-version, "5.2"]

  - repo: https://github.com/rtts/djhtml
    rev: 3.0.6
    hooks:
      - id: djhtml
        args: [--tabwidth, "2"]
        files: \.(html|txt)$

  - repo: local
    hooks:
      - id: django-check
        name: Django Check
        entry: python manage.py check
        language: system
        pass_filenames: false
        files: \.py$
```

### Development Workflow Integration

#### Makefile for Common Tasks
```makefile
# Makefile - Common development tasks

.PHONY: help install dev test lint format clean migrate collectstatic run

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	uv pip install -e .

dev: ## Install development dependencies
	uv pip install -e ".[dev,test]"
	pre-commit install

test: ## Run tests with coverage
	coverage run --source='.' manage.py test
	coverage report
	coverage html

lint: ## Run linting checks
	ruff check .
	ruff format --check .
	python manage.py check

format: ## Format code
	ruff format .
	ruff check --fix .

clean: ## Clean temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage htmlcov/
	rm -rf build/ dist/ *.egg-info/

migrate: ## Run database migrations
	python manage.py makemigrations
	python manage.py migrate

collectstatic: ## Collect static files
	python manage.py collectstatic --noinput

run: ## Start development server
	python manage.py runserver

shell: ## Start Django shell
	python manage.py shell_plus

deploy: ## Deploy to production
	./scripts/deploy.sh

backup: ## Backup database
	python manage.py dumpdata --indent=2 > backup.json

restore: ## Restore database from backup
	python manage.py loaddata backup.json
```

#### VS Code Configuration
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "none",
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.codeActionsOnSave": {
            "source.organizeImports": "explicit"
        }
    },
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "."
    ],
    "files.associations": {
        "*.html": "django-html"
    },
    "emmet.includeLanguages": {
        "django-html": "html"
    }
}

// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Django",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/manage.py",
            "args": [
                "runserver"
            ],
            "django": true,
            "justMyCode": true
        }
    ]
}
```

### Environment File Management

#### Environment Templates
```bash
# .env.example - Template for environment variables
# Copy this file to .env and fill in your values

# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Cache (Redis - optional for development)
REDIS_URL=redis://127.0.0.1:6379/1

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=
EMAIL_USE_TLS=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Static files
STATIC_ROOT=staticfiles
MEDIA_ROOT=media

# Monitoring (optional)
SENTRY_DSN=

# Development tools
DJANGO_SETTINGS_MODULE=cfmp.settings.development
```

#### Environment Loading
```python
# cfmp/settings/__init__.py
import os
from django.core.exceptions import ImproperlyConfigured

# Load environment variables
try:
    import environ
    env = environ.Env()
    env.read_env(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
except ImportError:
    pass

# Determine which settings to use
DJANGO_ENVIRONMENT = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if DJANGO_ENVIRONMENT == 'production':
    from .production import *
elif DJANGO_ENVIRONMENT == 'staging':
    from .staging import *
elif DJANGO_ENVIRONMENT == 'test':
    from .test import *
else:
    from .development import *
```

### CLI Tool Integration

#### Custom Management Commands
```python
# management/commands/setup_project.py
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Setup project for development'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--with-data',
            action='store_true',
            help='Load sample data for development',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up CFMP project...'))
        
        # Run migrations
        call_command('migrate')
        
        # Collect static files
        call_command('collectstatic', interactive=False)
        
        # Create superuser
        call_command('createsuperuser', 
                    username='admin',
                    email='admin@example.com',
                    interactive=False)
        
        # Load sample data if requested
        if options['with_data']:
            self.load_sample_data()
        
        self.stdout.write(self.style.SUCCESS('Project setup complete!'))
    
    def load_sample_data(self):
        # Load sample donations, users, etc.
        pass
```

## Consequences

**Positive**:
- Modern Python packaging aligned with class expectations
- Fast dependency resolution and environment setup
- Consistent code quality through automated formatting/linting
- Professional development workflow
- Clear separation of development/production dependencies
- Reproducible development environments

**Negative**:
- Learning curve for UV and new tooling
- Additional configuration files to maintain
- Potential compatibility issues with older Python tools
- More complex initial setup

**Mitigation Strategies**:
- Comprehensive documentation and setup scripts
- Fallback to pip for compatibility if needed
- VS Code integration for seamless development experience
- Make commands for common tasks

## Security Considerations

### Dependency Security
- Regular dependency updates with UV
- Security scanning with safety and bandit
- Pinned versions for security patches
- Separate development dependencies to reduce production attack surface

### Environment Security
- Environment variables for all secrets
- .env files excluded from version control
- Template files for easy setup without exposing secrets
- Production environment isolation

This ADR establishes a modern, professional development environment that aligns with class expectations while providing the tools and workflows needed for efficient Django development.