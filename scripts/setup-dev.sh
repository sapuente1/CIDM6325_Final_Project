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

# Activate virtual environment (platform detection)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    echo "⚡ Activating virtual environment (Windows)..."
    source .venv/Scripts/activate
else
    echo "⚡ Activating virtual environment..."
    source .venv/bin/activate
fi

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