# MileSync Deployment Guide - Render + Vercel + PostgreSQL

This guide will help you deploy MileSync with:
- **Frontend**: Vercel
- **Backend**: Render
- **Database**: PostgreSQL (Render)

---

## 🗄️ Step 1: Create PostgreSQL Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure the database:
   - **Name**: `milesync-db`
   - **Database**: `milesync`
   - **User**: `milesync_user`
   - **Region**: Choose the same region as your backend (e.g., Oregon)
   - **Plan**: Free (for testing) or Starter
4. Click **"Create Database"**
5. Wait for the database to be provisioned (~2 minutes)
6. **Copy the "Internal Database URL"** from the database page
   - It looks like: `postgresql://milesync_user:abc123@dpg-xxxxx-a/milesync`
   - ⚠️ Use the **Internal** URL, not the External one

---

## 🔧 Step 2: Deploy Backend to Render

### 2.1 Create Web Service

1. Go to Render Dashboard → Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `iamhariprasanth/MileSync`
3. Configure the service:
   - **Name**: `milesync-backend`
   - **Region**: Same as your database
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

### 2.2 Set Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add these:

```bash
# Database - Use the Internal Database URL from Step 1
DATABASE_URL=postgresql://milesync_user:YOUR_PASSWORD@dpg-xxxxx-a/milesync

# Authentication - Generate a secure key with: openssl rand -hex 32
SECRET_KEY=your-production-secret-key-change-this-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# OpenAI API
OPENAI_API_KEY=sk-your-openai-api-key-here

# Opik (Optional - for AI observability)
OPIK_API_KEY=your-opik-api-key
OPIK_WORKSPACE=your-workspace
OPIK_PROJECT_NAME=MileSync-AI-Coach

# Frontend URL (you'll update this after deploying to Vercel)
FRONTEND_URL=http://localhost:3000

# App Settings
DEBUG=False
DEFAULT_USER_QUOTA=100000
QUOTA_RESET_DAYS=30

# Python version
PYTHON_VERSION=3.11.0
```

4. Click **"Create Web Service"**
5. Wait for deployment to complete (~5-10 minutes)
6. **Copy your backend URL** (e.g., `https://milesync-backend.onrender.com`)

---

## 🌐 Step 3: Deploy Frontend to Vercel

### 3.1 Connect Repository

1. Go to [Vercel](https://vercel.com/new)
2. Import your GitHub repository: `iamhariprasanth/MileSync`
3. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 3.2 Set Environment Variables

Click **"Environment Variables"** and add:

```bash
VITE_API_URL=https://milesync-backend.onrender.com
```

(Replace with your actual Render backend URL from Step 2)

4. Click **"Deploy"**
5. Wait for deployment (~2-3 minutes)
6. **Copy your frontend URL** (e.g., `https://milesync.vercel.app`)

---

## 🔄 Step 4: Update Backend Environment Variables

1. Go back to your Render backend service
2. Go to **"Environment"** tab
3. Update the `FRONTEND_URL` variable:
   ```bash
   FRONTEND_URL=https://milesync.vercel.app
   ```
   (Use your actual Vercel URL from Step 3)
4. Click **"Save Changes"**
5. Render will automatically redeploy

---

## 👥 Step 5: Initialize Database (Optional - for demo users)

The database tables are created automatically when the backend starts. If you want to add demo users:

### Option A: Using Render Shell

1. Go to your Render backend service
2. Click **"Shell"** tab
3. Run:
   ```bash
   python scripts/init_postgres.py
   ```

### Option B: Manual Registration

Just go to your frontend URL and register a new account using the signup page.

---

## ✅ Verification Checklist

- [ ] PostgreSQL database created on Render
- [ ] Backend deployed on Render with correct `DATABASE_URL`
- [ ] Frontend deployed on Vercel with correct `VITE_API_URL`
- [ ] Backend `FRONTEND_URL` updated with Vercel URL
- [ ] Can access frontend at Vercel URL
- [ ] Can register/login successfully
- [ ] Can create goals through the chat interface

---

## 🐛 Troubleshooting

### Backend doesn't start
- Check logs in Render → Your service → "Logs"
- Verify `DATABASE_URL` is correct (use Internal URL)
- Make sure all environment variables are set

### Frontend can't connect to backend
- Check `VITE_API_URL` in Vercel environment variables
- Verify backend is running (visit `https://your-backend.onrender.com/docs`)
- Check for CORS errors in browser console

### Database connection errors
- Make sure you're using the **Internal Database URL** (not External)
- Verify the database is in the **same region** as your backend
- Check that PostgreSQL database is active in Render

### 500 errors when creating goals
- Check backend logs for specific errors
- Verify `OPENAI_API_KEY` is set correctly
- Check that database tables were created (visible in logs on first startup)

---

## 📝 Notes

1. **Free Tier Limitations**:
   - Render Free: Services sleep after 15 minutes of inactivity
   - PostgreSQL Free: 90 days, then needs manual refresh or upgrade
   
2. **Database Persistence**:
   - PostgreSQL on Render is persistent (unlike SQLite)
   - Data is retained across deployments

3. **First Deployment**:
   - May take 5-10 minutes
   - Subsequent deployments are faster

4. **Environment Variables**:
   - Changes to environment variables trigger automatic redeployment
   - Wait 2-3 minutes after updating environment variables

---

## 🔐 Security Reminders

- ✅ Generate a strong `SECRET_KEY` (use `openssl rand -hex 32`)
- ✅ Never commit `.env` files with real credentials
- ✅ Use Render's secret environment variables for sensitive data
- ✅ Keep your `OPENAI_API_KEY` secure
