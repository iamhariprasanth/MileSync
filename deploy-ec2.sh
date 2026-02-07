#!/bin/bash

# MileSync EC2 Quick Setup Script
# Run this on your Ubuntu EC2 instance

set -e  # Exit on error

echo "🚀 MileSync EC2 Deployment Script"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as ubuntu user
if [ "$USER" != "ubuntu" ]; then
    echo -e "${RED}❌ Please run this script as the 'ubuntu' user${NC}"
    exit 1
fi

echo -e "${GREEN}Step 1:${NC} Updating system packages..."
sudo apt update
sudo apt upgrade -y

echo -e "${GREEN}Step 2:${NC} Installing dependencies..."
# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip build-essential libpq-dev

# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install Nginx
sudo apt install -y nginx

# Install Git
sudo apt install -y git

echo -e "${GREEN}Step 3:${NC} Setting up PostgreSQL database..."
# Get database password
read -sp "Enter PostgreSQL password for milesync_user: " DB_PASSWORD
echo ""

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE milesync;" 2>/dev/null || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER milesync_user WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE milesync TO milesync_user;"

echo -e "${GREEN}Step 4:${NC} Creating application directory..."
sudo mkdir -p /var/www/milesync
sudo chown -R ubuntu:ubuntu /var/www/milesync
cd /var/www/milesync

echo -e "${GREEN}Step 5:${NC} Cloning repository..."
if [ -d ".git" ]; then
    echo "Repository already exists, pulling latest changes..."
    git pull origin main
else
    git clone https://github.com/iamhariprasanth/MileSync.git .
fi

echo -e "${GREEN}Step 6:${NC} Setting up backend..."
cd /var/www/milesync/backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Get OpenAI API Key
echo ""
read -p "Enter your OpenAI API Key: " OPENAI_KEY

# Get EC2 Public IP
EC2_PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

# Generate SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)

# Create .env file
cat > .env << EOL
# Database
DATABASE_URL=postgresql://milesync_user:${DB_PASSWORD}@localhost/milesync

# Authentication
SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# OpenAI API
OPENAI_API_KEY=${OPENAI_KEY}

# Frontend URL
FRONTEND_URL=http://${EC2_PUBLIC_IP}

# App Settings
DEBUG=False
DEFAULT_USER_QUOTA=100000
QUOTA_RESET_DAYS=30
EOL

echo -e "${YELLOW}✓ Backend .env file created${NC}"

# Initialize database
echo -e "${GREEN}Step 7:${NC} Initializing database with demo users..."
python scripts/init_postgres.py

deactivate

echo -e "${GREEN}Step 8:${NC} Setting up frontend..."
cd /var/www/milesync/frontend

# Install dependencies
npm install

# Create .env file
cat > .env << EOL
VITE_API_URL=http://${EC2_PUBLIC_IP}:8000
EOL

echo -e "${YELLOW}✓ Frontend .env file created${NC}"

# Build frontend
npm run build

echo -e "${GREEN}Step 9:${NC} Creating systemd services..."

# Backend service
sudo tee /etc/systemd/system/milesync-backend.service > /dev/null << EOL
[Unit]
Description=MileSync Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/var/www/milesync/backend
Environment="PATH=/var/www/milesync/backend/venv/bin"
ExecStart=/var/www/milesync/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# Frontend service
sudo tee /etc/systemd/system/milesync-frontend.service > /dev/null << EOL
[Unit]
Description=MileSync Frontend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/var/www/milesync/frontend
ExecStart=/usr/bin/npm run preview -- --host 0.0.0.0 --port 3000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

echo -e "${YELLOW}✓ Systemd services created${NC}"

echo -e "${GREEN}Step 10:${NC} Configuring Nginx..."

sudo tee /etc/nginx/sites-available/milesync > /dev/null << EOL
server {
    listen 80;
    server_name ${EC2_PUBLIC_IP};

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Backend docs
    location /docs {
        proxy_pass http://localhost:8000;
    }
}
EOL

# Enable site
sudo ln -sf /etc/nginx/sites-available/milesync /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

echo -e "${GREEN}Step 11:${NC} Starting services..."

# Reload systemd
sudo systemctl daemon-reload

# Enable and start services
sudo systemctl enable milesync-backend milesync-frontend
sudo systemctl start milesync-backend milesync-frontend

# Wait a bit for services to start
sleep 3

echo ""
echo -e "${GREEN}=================================="
echo "✅ Deployment Complete!"
echo -e "==================================${NC}"
echo ""
echo -e "${YELLOW}Service Status:${NC}"
sudo systemctl status milesync-backend --no-pager -l | grep "Active:"
sudo systemctl status milesync-frontend --no-pager -l | grep "Active:"
sudo systemctl status nginx --no-pager -l | grep "Active:"
echo ""
echo -e "${YELLOW}Access your application:${NC}"
echo "  Frontend: http://${EC2_PUBLIC_IP}"
echo "  Backend API: http://${EC2_PUBLIC_IP}/docs"
echo ""
echo -e "${YELLOW}Demo Credentials:${NC}"
echo "  Admin: admin@milesync.demo / admin123"
echo "  User:  user@milesync.demo / user123"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "  View backend logs:  sudo journalctl -u milesync-backend -f"
echo "  View frontend logs: sudo journalctl -u milesync-frontend -f"
echo "  Restart backend:    sudo systemctl restart milesync-backend"
echo "  Restart frontend:   sudo systemctl restart milesync-frontend"
echo ""
echo -e "${GREEN}🎉 MileSync is ready to use!${NC}"
