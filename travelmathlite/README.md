# TravelMathLite

A Django-based travel calculation platform inspired by travelmath.com, providing distance calculations, nearest airport lookup, and trip planning tools.

## Quick Start

```bash
# Install dependencies
uv sync

# Run migrations
uv run python manage.py migrate

# Import airport data
uv run python manage.py import_airports

# Start development server
uv run python manage.py runserver
```

Visit http://127.0.0.1:8000 to see the application.

## Features

- **Airport Data**: Comprehensive airport database from OurAirports
- **Distance Calculator**: Calculate distances between locations
- **Nearest Airport**: Find airports near any location
- **Search**: Search airports by name, code, or location
- **Trip Planning**: Estimate travel costs and time

## Documentation

### Getting Started

- **[Contributing Guide](../docs/travelmathlite/CONTRIBUTING.md)** - Onboarding for new contributors
- **[Project Setup with uv](../docs/travelmathlite/django-project-setup-with-uv.md)** - Initial setup guide

### Dataset and Data Management

- **[Data Model Integration](../docs/travelmathlite/data-model-integration.md)** - Import workflow and troubleshooting
- **[Schema Mapping](../docs/travelmathlite/schema-mapping-airports.md)** - Field mapping reference
- **[Update Automation](../docs/travelmathlite/update-automation-airports.md)** - Scheduled updates
- **[Licensing Compliance](../docs/travelmathlite/licensing-compliance-airports.md)** - Dataset license and attribution

### Architecture

- **[ADRs](../docs/travelmathlite/adr/)** - Architecture Decision Records
- **[PRD](../docs/travelmathlite/prd/)** - Product Requirements Document
- **[Briefs](../docs/travelmathlite/briefs/)** - Task-level implementation guides

## Project Structure

```
travelmathlite/
├── apps/
│   ├── accounts/       # User authentication
│   ├── airports/       # Airport data and import commands
│   ├── base/          # Country/City normalized models
│   ├── calculators/   # Distance and cost calculations
│   ├── search/        # Search functionality
│   └── trips/         # Trip planning
├── core/              # Django project settings
├── downloads/         # Downloaded dataset files
└── templates/         # Base templates
```

## Management Commands

### Airport Data

```bash
# Import/update airport data from OurAirports
uv run python manage.py import_airports

# Import from local file
uv run python manage.py import_airports --file downloads/airports.csv

# Preview changes without writing to database
uv run python manage.py import_airports --dry-run

# Validate data quality
uv run python manage.py validate_airports

# Automated updates with logging
uv run python manage.py update_airports
```

See [Data Model Integration](../docs/travelmathlite/data-model-integration.md) for detailed workflow documentation.

## Development

### Code Standards

- Python 3.12 + Django
- PEP 8 style with docstrings and type hints
- Django TestCase for testing (no pytest)
- Conventional commits (feat/fix/docs/refactor/test/chore)

### Linting and Formatting

```bash
# Check for issues
uvx ruff check .

# Format code
uvx ruff format .
```

### Testing

```bash
# Run all tests
uv run python manage.py test

# Test specific apps
uv run python manage.py test apps.base apps.airports
```

### Debugging

```bash
# Run with verbose output
uv run python manage.py import_airports --verbose

# Check import without Country/City linking
uv run python manage.py import_airports --skip-country-link --skip-city-link
```

## Contributing

1. Read the [Contributing Guide](../docs/travelmathlite/CONTRIBUTING.md)
2. Review the [PRD](../docs/travelmathlite/prd/travelmathlite_prd_v1.0.0.md)
3. Check [ADRs](../docs/travelmathlite/adr/) for architectural decisions
4. Follow conventional commit style with issue references

### Pull Request Checklist

- [ ] Lint-clean (`uvx ruff check .`)
- [ ] Formatted (`uvx ruff format .`)
- [ ] Tests pass (`uv run python manage.py test`)
- [ ] Small PR (<300 lines changed)
- [ ] Migration plan included
- [ ] Commit references issue (Refs #N or Closes #N)

## License

This project is for educational purposes as part of CIDM 6325.

Dataset: OurAirports data is in the public domain. See [Licensing Compliance](../docs/travelmathlite/licensing-compliance-airports.md).

## Support

- Documentation: `docs/travelmathlite/`
- Architecture: `docs/travelmathlite/adr/`
- Issues: GitHub Issues
- Class: CIDM 6325 discussions

---

Built with Django, Python, and ❤️ for CIDM 6325.
