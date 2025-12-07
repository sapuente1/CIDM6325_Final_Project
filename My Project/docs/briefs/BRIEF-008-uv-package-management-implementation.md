# BRIEF-008: UV Package Management & Modern Python Tooling Implementation

**Date**: 2025-12-07  
**Related ADR**: ADR-008-uv-package-management.md  
**Issue**: Implement modern Python package management with UV + pyproject.toml  
**Sprint Goal**: Modernize CFMP development workflow with industry-standard tooling

## Goal

Transform CFMP from traditional pip/requirements.txt to modern UV-based package management with comprehensive development tooling, automated code quality, and reproducible environments aligned with class README standards.

## Scope (Single PR)

### Files to Create/Update:
- **pyproject.toml**: Complete project configuration with dependencies, dev groups, and tool settings
- **scripts/setup-dev.sh**: Development environment setup automation
- **.pre-commit-config.yaml**: Code quality automation hooks
- **Makefile**: Common development task shortcuts
- **.vscode/settings.json**: VS Code integration for UV/Ruff
- **.vscode/launch.json**: Django debugging configuration
- **.env.example**: Environment variable template
- **cfmp/settings/__init__.py**: Environment-based settings loader
- **cfmp/management/commands/setup_project.py**: Custom Django command for project setup

### Files to Migrate:
- **requirements.txt**: Convert to pyproject.toml dependencies
- **cfmp/settings.py**: Split into development/production/test modules

### Non-goals for this PR:
- Deployment configuration (covered in ADR-007)
- Database migrations (existing setup works)
- UI/frontend changes
- Docker containerization

## Standards & Requirements

### Code Quality
- **Ruff**: All Python code must pass ruff check and ruff format
- **Pre-commit**: Automated hooks for trailing whitespace, YAML validation, Django checks
- **Type Hints**: Required on all new public functions and methods
- **Docstrings**: Required on all public classes and functions
- **Test Coverage**: Maintain existing coverage, add tests for new management commands

### Dependency Management
- **UV**: Use `uv pip install` for all dependency operations
- **Dependency Groups**: Separate dev, test, prod, and docs dependencies
- **Version Pinning**: Pin major versions, allow minor/patch updates
- **Security**: Regular dependency scanning and updates

### Environment Management
- **python-environ**: Load environment variables with type safety
- **Settings Split**: Separate development, test, production, and staging configurations
- **Secret Management**: All sensitive data via environment variables
- **Default Values**: Sensible defaults for development environment

## Acceptance Criteria

### UC-001: Modern Package Management
**Given** a fresh clone of the CFMP repository  
**When** a developer runs the setup script  
**Then** they should have a working development environment with:
- Virtual environment created with UV
- All dependencies installed in correct groups
- Pre-commit hooks configured and working
- Django migrations applied
- Test suite passing

**Validation Steps**:
```powershell
# Test the complete setup process
git clone <repo-url> cfmp-test
cd cfmp-test
./scripts/setup-dev.sh
uv pip list
pre-commit run --all-files
python manage.py test
```

### UC-002: Code Quality Automation
**Given** a developer makes code changes  
**When** they commit their changes  
**Then** the code should automatically:
- Pass Ruff linting and formatting
- Pass Django system checks
- Have properly formatted HTML templates
- Have no trailing whitespace or merge conflicts

**Validation Steps**:
```powershell
# Make a test change and verify pre-commit works
echo "test = 'badly formatted'" >> cfmp/test_file.py
git add .
git commit -m "test commit"  # Should trigger pre-commit and fix formatting
```

### UC-003: Development Workflow Integration
**Given** a developer wants to perform common tasks  
**When** they use the provided shortcuts  
**Then** they should be able to:
- Run tests with coverage: `make test`
- Format code: `make format`
- Start development server: `make run`
- Access Django shell: `make shell`
- Create/apply migrations: `make migrate`

**Validation Steps**:
```powershell
# Test all make commands
make help
make test
make lint
make format
make run  # Verify server starts on localhost:8000
```

### UC-004: VS Code Integration
**Given** a developer opens CFMP in VS Code  
**When** they edit Python files  
**Then** VS Code should:
- Use the correct Python interpreter from .venv
- Automatically format code on save with Ruff
- Show linting errors and warnings inline
- Provide Django-aware syntax highlighting for templates
- Enable debugging with proper launch configuration

**Validation Steps**:
- Open VS Code in project directory
- Verify status bar shows correct Python interpreter
- Edit a Python file and save (should auto-format)
- Set breakpoint and start Django debugger

### UC-005: Environment Configuration
**Given** a new developer setting up CFMP  
**When** they configure their environment  
**Then** they should:
- Copy .env.example to .env
- Understand which variables are required vs optional
- Have working defaults for development
- Be able to override settings per environment

**Validation Steps**:
```powershell
# Test environment loading
cp .env.example .env
python manage.py shell -c "from django.conf import settings; print(settings.DEBUG)"
```

## Implementation Guidance for Copilot

### Phase 1: Core Configuration Files
**Prompt**: "Create a complete pyproject.toml for Django 5.2.6 project with UV package management. Include dependency groups for dev, test, prod, and docs. Configure Ruff for linting/formatting with Django-specific rules. Include coverage and pytest configuration."

**Key Requirements**:
- Python 3.12+ requirement
- Django 5.2.6 with psycopg, environ, pillow, whitenoise, gunicorn
- Development group: ruff, pre-commit, django-debug-toolbar, ipython
- Test group: pytest-django, coverage, factory-boy
- Production group: sentry-sdk, django-csp, redis
- Ruff configuration with Django plugin and security checks

### Phase 2: Development Automation
**Prompt**: "Create development automation scripts including setup-dev.sh for UV environment creation, .pre-commit-config.yaml with Ruff and Django checks, and Makefile with common development tasks (test, lint, format, run, migrate)."

**Key Requirements**:
- Bash script that checks UV installation, creates venv, installs deps
- Pre-commit hooks for Ruff, Django checks, trailing whitespace
- Makefile with help command showing available targets
- Error handling and informative output

### Phase 3: Settings Architecture
**Prompt**: "Refactor Django settings into development/production/test modules with environment variable loading. Create base settings with common configuration, then environment-specific overrides. Use django-environ for type-safe environment variable loading."

**Key Requirements**:
- cfmp/settings/__init__.py with environment detection
- Base, development, production, test settings modules
- Environment variable loading with defaults
- Security settings appropriate to each environment

### Phase 4: VS Code Integration
**Prompt**: "Create VS Code workspace configuration for Django development with UV virtual environment, Ruff formatting, and Django debugging. Include settings.json for Python interpreter, formatting, and testing configuration plus launch.json for Django runserver debugging."

**Key Requirements**:
- Python interpreter path to .venv
- Ruff as formatter and linter
- Django-HTML syntax highlighting
- Django debug configuration with proper environment

### Phase 5: Custom Management Commands
**Prompt**: "Create Django management command 'setup_project' that automates initial project setup including migrations, static files, superuser creation, and optional sample data loading. Include proper argument handling and informative output."

**Key Requirements**:
- Handle migrations, collectstatic, createsuperuser
- --with-data flag for sample data
- Proper Django management command structure
- Error handling and progress feedback

## Migration Strategy

### Dependency Transition
1. **Audit Current Dependencies**: Review existing requirements.txt
2. **Group Dependencies**: Categorize into runtime, development, testing, production
3. **Pin Versions**: Use compatible version ranges (>=major.minor.0,<next.0)
4. **Test Migration**: Verify all functionality works with new dependency structure

### Settings Refactoring
1. **Extract Common Settings**: Move shared configuration to base.py
2. **Environment-Specific**: Create development.py, production.py, test.py
3. **Environment Variables**: Replace hardcoded values with env var loading
4. **Backwards Compatibility**: Ensure existing deployment still works

### Developer Onboarding
1. **Documentation**: Update README with UV setup instructions
2. **Scripts**: Provide automated setup for new developers
3. **VS Code**: Include workspace configuration in repository
4. **Training**: Document new workflow and common tasks

## Risk Mitigation

### Compatibility Risks
- **Risk**: UV compatibility issues with existing tools
- **Mitigation**: Maintain requirements.txt as fallback during transition
- **Rollback**: Keep both UV and pip workflows functional

### Performance Risks
- **Risk**: UV dependency resolution slower than expected
- **Mitigation**: Profile setup times and optimize dependency groups
- **Monitoring**: Track developer setup time metrics

### Learning Curve Risks
- **Risk**: Developers unfamiliar with UV workflow
- **Mitigation**: Comprehensive documentation and setup automation
- **Support**: Provide troubleshooting guide and common error solutions

## Verification Checklist

### Pre-Deployment
- [ ] pyproject.toml validates with UV
- [ ] All dependency groups install correctly
- [ ] Pre-commit hooks pass on existing codebase
- [ ] Make commands work on Windows/macOS/Linux
- [ ] VS Code configuration loads correctly
- [ ] Django management commands work
- [ ] Environment variable loading functional
- [ ] Test suite passes with new configuration

### Post-Deployment
- [ ] CI/CD pipeline updated for UV workflow
- [ ] Documentation updated with new setup instructions
- [ ] Team trained on new development workflow
- [ ] Monitoring setup for dependency security updates
- [ ] Backup plan tested for reverting to pip if needed

## Success Metrics

### Development Experience
- Setup time for new developers < 5 minutes
- Zero manual configuration steps required
- Automated code quality enforcement
- Consistent development environments across team

### Code Quality
- 100% pre-commit hook adoption
- Zero linting errors in main branch
- Consistent code formatting across codebase
- Improved test coverage and reliability

### Maintenance
- Simplified dependency management
- Clear separation of environment concerns
- Automated security updates
- Reduced configuration drift between environments

This brief provides comprehensive guidance for implementing modern Python tooling while maintaining CFMP's existing functionality and ensuring a smooth transition for all developers.