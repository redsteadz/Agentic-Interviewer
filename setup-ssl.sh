#!/bin/bash

# SSL Setup with Let's Encrypt
# Run this after your domain is pointed to your droplet

echo "🔒 Setting up SSL with Let's Encrypt..."

# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
echo "📝 Please enter your domain name (e.g., yourdomain.com):"
read DOMAIN

# Obtain SSL certificate
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN

# Set up auto-renewal
sudo crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | sudo crontab -

echo "✅ SSL setup complete!"
echo "🌐 Your site is now available at https://$DOMAIN"
