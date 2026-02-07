# MileSync Deployment Guide - AWS EC2

This guide will help you deploy MileSync on an AWS EC2 Ubuntu instance.

---

## 📋 Prerequisites

- ✅ EC2 instance running Ubuntu 20.04 or 22.04
- ✅ SSH access to the instance
- ✅ Security group allowing ports: 22 (SSH), 80 (HTTP), 443 (HTTPS), 3000 (Frontend dev), 8000 (Backend dev)
- ✅ Domain name pointed to your EC2 public IP (optional, for production)

---

## 🚀 Step 1: Initial Server Setup

SSH into your EC2 instance (you're already connected):

```bash
ssh -i "milesync.pem" ubuntu@ec2-3-7-110-104.ap-south-1.compute.amazonaws.com
```

### 1.1 Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### 1.2 Install Required Software

```bash
# Install Python 3.11, pip, and venv
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install Node.js 18.x and npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PostgreSQL (recommended for production)
sudo apt install -y postgresql postgresql-contrib

# Install Nginx (web server/reverse proxy)
sudo apt install -y nginx

# Install Git
sudo apt install -y git

# Install build essentials (for Python packages)
sudo apt install -y build-essential libpq-dev
```

### 1.3 Verify Installations

```bash
python3.11 --version  # Should show Python 3.11.x
node --version        # Should show v18.x.x
npm --version         # Should show 9.x.x or higher
psql --version        # Should show PostgreSQL version
nginx -v              # Should show nginx version
```

---

## 🗄️ Step 2: Setup PostgreSQL Database

### 2.1 Create Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# Inside PostgreSQL shell, run these commands:
CREATE DATABASE milesync;
CREATE USER milesync_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE milesync TO milesync_user;
\q  # Exit PostgreSQL
```

### 2.2 Test Database Connection

```bash
psql -U milesync_user -d milesync -h localhost -W
# Enter the password when prompted
# If successful, you'll see the PostgreSQL prompt
\q  # Exit
```

---

## 📦 Step 3: Clone and Setup Backend

### 3.1 Create Application Directory

```bash
sudo mkdir -p /var/www/milesync
sudo chown -R ubuntu:ubuntu /var/www/milesync
cd /var/www/milesync
```

### 3.2 Clone Repository

```bash
git clone https://github.com/iamhariprasanth/MileSync.git .
```

### 3.3 Setup Backend

```bash
cd /var/www/milesync/backend

# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.4 Create Environment File

```bash
nano .env
```

Add the following content (replace values as needed):

```bash
# Database
DATABASE_URL=postgresql://milesync_user:your_secure_password_here@localhost/milesync

# Authentication - Generate with: openssl rand -hex 32
SECRET_KEY=your-production-secret-key-min-32-characters-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# OpenAI API
OPENAI_API_KEY=sk-your-openai-api-key-here

# Opik (Optional)
OPIK_API_KEY=your-opik-api-key
OPIK_WORKSPACE=your-workspace
OPIK_PROJECT_NAME=MileSync-AI-Coach

# Frontend URL (update after frontend setup)
FRONTEND_URL=http://YOUR_EC2_PUBLIC_IP

# App Settings
DEBUG=False
DEFAULT_USER_QUOTA=100000
QUOTA_RESET_DAYS=30
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

### 3.5 Initialize Database

```bash
# Still in the backend directory with venv activated
python scripts/init_postgres.py
```

---

## 🎨 Step 4: Setup Frontend

### 4.1 Install Dependencies

```bash
cd /var/www/milesync/frontend
npm install
```

### 4.2 Create Environment File

```bash
nano .env
```

Add:

```bash
VITE_API_URL=http://YOUR_EC2_PUBLIC_IP:8000
```

Replace `YOUR_EC2_PUBLIC_IP` with your actual EC2 public IP address.

Press `Ctrl+X`, then `Y`, then `Enter` to save.

### 4.3 Build Frontend

```bash
npm run build
```

---

## 🔧 Step 5: Setup Systemd Services

### 5.1 Create Backend Service

```bash
sudo nano /etc/systemd/system/milesync-backend.service
```

Add:

```ini
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
```

Save and exit (`Ctrl+X`, `Y`, `Enter`).

### 5.2 Create Frontend Service

```bash
sudo nano /etc/systemd/system/milesync-frontend.service
```

Add:

```ini
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
```

Save and exit.

### 5.3 Enable and Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable milesync-backend
sudo systemctl enable milesync-frontend

# Start services
sudo systemctl start milesync-backend
sudo systemctl start milesync-frontend

# Check status
sudo systemctl status milesync-backend
sudo systemctl status milesync-frontend
```

---

## 🌐 Step 6: Configure Nginx (Reverse Proxy)

### 6.1 Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/milesync
```

Add:

```nginx
server {
    listen 80;
    server_name 3.7.110.104;  # Your EC2 Public IP

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend docs
    location /docs {
        proxy_pass http://localhost:8000;
    }
}
```

Save and exit.

### 6.2 Enable Nginx Configuration

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/milesync /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

## ✅ Step 7: Verify Deployment

### 7.1 Check Services Status

```bash
sudo systemctl status milesync-backend
sudo systemctl status milesync-frontend
sudo systemctl status nginx
```

All should show "active (running)".

### 7.2 Test Application

Open your browser and navigate to:
- Frontend: `http://YOUR_EC2_PUBLIC_IP`
- Backend API Docs: `http://YOUR_EC2_PUBLIC_IP/docs`

### 7.3 Test Demo Login

Use the demo credentials:
- **Admin**: `admin@milesync.demo` / `admin123`
- **User**: `user@milesync.demo` / `user123`

---

## 🔒 Step 8: Optional - Setup SSL with Let's Encrypt

If you have a domain name:

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

Update your frontend `.env` to use HTTPS:
```bash
VITE_API_URL=https://yourdomain.com
```

Then rebuild and restart:
```bash
cd /var/www/milesync/frontend
npm run build
sudo systemctl restart milesync-frontend
```

---

## 🛠️ Useful Commands

### View Logs

```bash
# Backend logs
sudo journalctl -u milesync-backend -f

# Frontend logs
sudo journalctl -u milesync-frontend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Restart Services

```bash
sudo systemctl restart milesync-backend
sudo systemctl restart milesync-frontend
sudo systemctl restart nginx
```

### Update Application

```bash
cd /var/www/milesync
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart milesync-backend

# Update frontend
cd ../frontend
npm install
npm run build
sudo systemctl restart milesync-frontend
```

### Check Database

```bash
psql -U milesync_user -d milesync -h localhost
# List tables: \dt
# Exit: \q
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
sudo journalctl -u milesync-backend -n 50

# Common issues:
# - Database connection failed → Check DATABASE_URL in .env
# - Port already in use → Check: sudo lsof -i :8000
# - Missing packages → Reinstall: pip install -r requirements.txt
```

### Frontend won't start
```bash
# Check logs
sudo journalctl -u milesync-frontend -n 50

# Common issues:
# - Build failed → Rebuild: npm run build
# - Port already in use → Check: sudo lsof -i :3000
```

### Can't access from browser
```bash
# Check security group in AWS Console
# Ensure ports 80 (HTTP) and 443 (HTTPS) are open

# Check Nginx
sudo nginx -t
sudo systemctl status nginx
```

---

## 📝 Security Checklist

- [ ] Changed default database password
- [ ] Generated secure SECRET_KEY
- [ ] Configured firewall (UFW or AWS Security Groups)
- [ ] Only opened necessary ports (22, 80, 443)
- [ ] Disabled root SSH login
- [ ] Setup SSL certificate (Let's Encrypt)
- [ ] Regular security updates: `sudo apt update && sudo apt upgrade`

---

## 🎉 Congratulations!

Your MileSync application is now deployed on AWS EC2! 🚀
