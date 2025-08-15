#!/usr/bin/env bash
# Build script for Render

set -o errexit  # exit on error

echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running database migrations..."
python manage.py migrate

echo "Installing frontend dependencies..."
cd ../frontend
npm ci

echo "Building frontend..."
npm run build

echo "Moving frontend build to Django static files..."
rm -rf ../backend/staticfiles/frontend
mkdir -p ../backend/staticfiles/frontend
cp -r dist/* ../backend/staticfiles/frontend/

echo "Build completed successfully!"
