# Digital Ocean Deployment Guide

## Prerequisites

1. **Digital Ocean Droplet** (Ubuntu 20.04/22.04 LTS)
   - Minimum: 1GB RAM, 1 vCPU ($6/month)
   - Recommended: 2GB RAM, 1 vCPU ($12/month)

2. **Domain Name** (optional but recommended)
   - Point A record to your droplet's IP address

## Quick Deployment Steps

### 1. Create Digital Ocean Droplet

1. Log in to Digital Ocean
2. Create a new droplet with Ubuntu 22.04 LTS
3. Choose your preferred size (1GB RAM minimum)
4. Add your SSH key for secure access
5. Note down the droplet's IP address

### 2. Connect to Your Droplet

```bash
ssh root@your-droplet-ip
```

### 3. Deploy the Application

```bash
# Download and run the deployment script
curl -O https://raw.githubusercontent.com/redsteadz/Agentic-Interviewer/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

### 4. Configure the Server

```bash
# Run the server configuration script
./setup-server.sh
```

### 5. Update Configuration

Edit the configuration files with your actual details:

```bash
# Update Nginx configuration
sudo nano /etc/nginx/sites-available/django-react-auth
# Replace 'your-domain.com' and 'your-ip-address' with actual values

# Update environment variables
nano /var/www/django-react-auth/backend/.env
# Update ALLOWED_HOSTS with your domain/IP
```

### 6. Restart Services

```bash
sudo systemctl restart nginx
sudo systemctl restart django-react-auth
```

### 7. Set Up SSL (Optional but Recommended)

```bash
./setup-ssl.sh
```

## Manual Deployment (Step by Step)

If you prefer to understand each step:

### 1. System Setup

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git curl
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 2. Application Setup

```bash
sudo mkdir -p /var/www/django-react-auth
sudo chown $USER:$USER /var/www/django-react-auth
cd /var/www/django-react-auth
git clone https://github.com/redsteadz/Agentic-Interviewer.git .
```

### 3. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Database Setup

```bash
sudo -u postgres psql
CREATE DATABASE django_react_auth;
CREATE USER django_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE django_react_auth TO django_user;
\q
```

### 5. Environment Configuration

Create `.env` file in `/var/www/django-react-auth/backend/`:

```env
DJANGO_ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-generated-secret-key
ALLOWED_HOSTS=yourdomain.com,your-ip-address
DATABASE_URL=postgresql://django_user:your_secure_password@localhost/django_react_auth
```

### 6. Django Setup

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 7. Frontend Build

```bash
cd ../frontend
npm install
npm run build
rm -rf ../backend/staticfiles/frontend
mkdir -p ../backend/staticfiles/frontend
cp -r dist/* ../backend/staticfiles/frontend/
```

## Service Management

### Check Status
```bash
sudo systemctl status django-react-auth
sudo systemctl status nginx
```

### View Logs
```bash
sudo journalctl -u django-react-auth -f
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
sudo systemctl restart django-react-auth
sudo systemctl restart nginx
```

## Updating the Application

```bash
cd /var/www/django-react-auth
git pull origin main
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
cd ../frontend
npm install
npm run build
rm -rf ../backend/staticfiles/frontend
mkdir -p ../backend/staticfiles/frontend
cp -r dist/* ../backend/staticfiles/frontend/
sudo systemctl restart django-react-auth
```

## Security Considerations

1. **Firewall Setup**
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

2. **Regular Updates**
```bash
sudo apt update && sudo apt upgrade -y
```

3. **Database Backups**
```bash
pg_dump -U django_user django_react_auth > backup.sql
```

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**: Check if Django service is running
2. **Static files not loading**: Check nginx configuration and file permissions
3. **Database connection error**: Verify PostgreSQL is running and credentials are correct

### Useful Commands

```bash
# Check Django service logs
sudo journalctl -u django-react-auth --no-pager

# Test nginx configuration
sudo nginx -t

# Check open ports
sudo netstat -tlnp

# Check file permissions
ls -la /var/www/django-react-auth/
```

## Cost Estimation

- **$6/month**: Basic droplet (1GB RAM) - suitable for small apps
- **$12/month**: Standard droplet (2GB RAM) - recommended for production
- **$0**: SSL certificate (Let's Encrypt)
- **Domain**: $10-15/year (optional)

**Total: $6-12/month** (much cheaper than Render!)

## Support

If you encounter issues:
1. Check the logs using the commands above
2. Verify all configuration files are correct
3. Ensure your domain DNS is pointing to the droplet IP
4. Check firewall settings
