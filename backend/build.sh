#!/bin/bash
# Build script for Render deployment

echo "Starting build process for AlphaQuest backend..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files for production
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

echo "Build process completed successfully!"