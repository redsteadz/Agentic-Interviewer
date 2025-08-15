#!/bin/bash

# Server Configuration Script
# Run this after the main deployment script

echo "🔧 Configuring Nginx..."

# Copy nginx configuration
sudo cp /var/www/django-react-auth/nginx.conf /etc/nginx/sites-available/django-react-auth

# Create symlink to enable the site
sudo ln -sf /etc/nginx/sites-available/django-react-auth /etc/nginx/sites-enabled/

# Remove default nginx site
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Configure systemd service
echo "🔧 Setting up systemd service..."
sudo cp /var/www/django-react-auth/django-react-auth.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable django-react-auth
sudo systemctl start django-react-auth

# Set up proper permissions
echo "🔒 Setting up permissions..."
sudo chown -R www-data:www-data /var/www/django-react-auth
sudo chmod -R 755 /var/www/django-react-auth

# Restart services
echo "🔄 Restarting services..."
sudo systemctl restart nginx
sudo systemctl restart django-react-auth

# Check status
echo "📊 Checking service status..."
sudo systemctl status django-react-auth --no-pager
sudo systemctl status nginx --no-pager

echo "✅ Server configuration complete!"
echo "🌐 Your application should now be accessible at http://your-domain.com"
echo "📝 Don't forget to:"
echo "   1. Update your domain/IP in nginx.conf"
echo "   2. Update ALLOWED_HOSTS in .env"
echo "   3. Set up SSL with Let's Encrypt (optional)"
