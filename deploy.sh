#!/bin/bash
# deploy.sh - Railway deployment helper

set -e

echo "🚀 Starting CFMP deployment..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    curl -fsSL https://railway.app/install.sh | sh
fi

# Check for required environment variables
if [ -z "$RAILWAY_TOKEN" ]; then
    echo "❌ RAILWAY_TOKEN not set. Please set your Railway token."
    exit 1
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login --token $RAILWAY_TOKEN

# Deploy the application
echo "📦 Deploying to Railway..."
railway up --detach

# Run migrations
echo "🗄️ Running migrations..."
railway run python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
railway run python manage.py collectstatic --noinput

# Check deployment health
echo "🏥 Checking deployment health..."
railway run python manage.py check --deploy

echo "✅ Deployment completed successfully!"
echo "🌐 Your application is available at: https://cfmp-production.up.railway.app"

echo "Deployment complete!"
echo "Remember to set environment variables in your hosting platform:"
echo "  - SECRET_KEY"
echo "  - ALLOWED_HOSTS"
echo "  - DB_NAME, DB_USER, DB_PASSWORD, DB_HOST"
echo "  - REDIS_URL (optional)"
echo "  - EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD (optional)"
echo ""
echo "Health check available at: /monitoring/health/"