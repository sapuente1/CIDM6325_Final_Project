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