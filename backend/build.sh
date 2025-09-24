#!/bin/bash
# Build script for Render deployment

echo "Starting build process for AlphaQuest backend..."

# Set memory-friendly pip options
export PIP_NO_CACHE_DIR=1
export PIP_DISABLE_PIP_VERSION_CHECK=1

# Install Python dependencies with reduced memory usage
echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Collect static files for production
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

echo "Build process completed successfully!"