#!/bin/bash

# Quick Update Script for Digital Ocean Deployment
# Run this script to update your application after pushing changes

echo "🔄 Updating Django React Auth application..."

cd /var/www/django-react-auth

# Pull latest changes
echo "📥 Pulling latest changes from Git..."
git pull origin main

# Update backend
echo "🐍 Updating backend..."
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# Update frontend
echo "🎨 Updating frontend..."
cd ../frontend
npm install
npm run build

# Move frontend build
echo "📁 Moving frontend build..."
rm -rf ../backend/staticfiles/frontend
mkdir -p ../backend/staticfiles/frontend
cp -r dist/* ../backend/staticfiles/frontend/

# Restart services
echo "🔄 Restarting services..."
sudo systemctl restart django-react-auth
sudo systemctl reload nginx

# Check status
echo "✅ Update complete! Checking service status..."
sudo systemctl status django-react-auth --no-pager

echo "🌐 Application updated successfully!"
