#!/bin/bash

# Digital Ocean Droplet Deployment Script
# Run this script on your Ubuntu droplet

set -e

echo "🚀 Starting deployment on Digital Ocean droplet..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install required system packages
echo "🔧 Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib supervisor git curl

# Install Node.js
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p /var/www/django-react-auth
sudo chown $USER:$USER /var/www/django-react-auth
cd /var/www/django-react-auth

# Clone repository (you'll need to replace with your repo URL)
echo "📥 Cloning repository..."
if [ ! -d ".git" ]; then
    git clone https://github.com/redsteadz/Agentic-Interviewer.git .
else
    git pull origin main
fi

# Set up Python virtual environment
echo "🐍 Setting up Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up PostgreSQL database
echo "🗄️ Setting up PostgreSQL database..."
sudo -u postgres psql << EOF
CREATE DATABASE django_react_auth;
CREATE USER django_user WITH PASSWORD 'secure_password_123';
ALTER ROLE django_user SET client_encoding TO 'utf8';
ALTER ROLE django_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE django_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE django_react_auth TO django_user;
\q
EOF

# Set up environment variables
echo "🔧 Setting up environment variables..."
cat > .env << EOF
DJANGO_ENVIRONMENT=production
DEBUG=False
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=your-domain.com,your-ip-address
DATABASE_URL=postgresql://django_user:secure_password_123@localhost/django_react_auth
EOF

# Run Django setup
echo "🔄 Running Django migrations and collecting static files..."
python manage.py migrate
python manage.py collectstatic --noinput

# Build frontend
echo "🎨 Building frontend..."
cd ../frontend
npm install
npm run build

# Move frontend build to Django static directory
echo "📁 Moving frontend build to Django static directory..."
rm -rf ../backend/staticfiles/frontend
mkdir -p ../backend/staticfiles/frontend
cp -r dist/* ../backend/staticfiles/frontend/

echo "✅ Application setup complete!"
echo "🔧 Now configuring Nginx and Supervisor..."
