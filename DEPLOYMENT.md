# 🚀 Deployment Guide

This guide covers deploying the SecondBrain application with:
- **Frontend**: GitHub Pages (free, automatic deployment) - React + Vite SPA
- **Backend**: Render.com (free tier available, managed PostgreSQL)

## 📋 Prerequisites

1. **GitHub Repository**: Push your code to GitHub
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **OpenAI API Key** (Optional): For AI-powered search explanations (can also be set in Settings page)

## 🌐 Frontend Deployment (GitHub Pages)

### Automatic Deployment Setup

1. **Enable GitHub Pages**:
   ```bash
   # Go to your GitHub repo → Settings → Pages
   # Source: Deploy from a branch
   # Branch: gh-pages
   # Folder: / (root)
   ```

2. **Set Repository Secret**:
   ```bash
   # Go to GitHub repo → Settings → Secrets and variables → Actions
   # Add new repository secret:
   Name: VITE_API_URL
   Value: https://your-backend-name.onrender.com
   ```

3. **Deploy**:
   - Push to `main` branch triggers automatic deployment via GitHub Actions
   - The workflow builds the Vite app and deploys to gh-pages branch
   - Visit: `https://octopus-ai-secondbrain.github.io/Octopus-AI-SecondBrain.github.io/`

### Manual Local Build

```bash
cd frontend
npm install
npm run build

# Test production build locally
npm run preview
```

## 🖥️ Backend Deployment (Render.com)

### Step 1: Create PostgreSQL Database

1. **Create Database**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "PostgreSQL"
   - Name: `secondbrain-db`
   - Plan: Free (or paid for production)
   - Region: Choose closest to your users

2. **Note Database Details**:
   - Save the `DATABASE_URL` (Internal Database URL)

### Step 2: Create Web Service

1. **Create Web Service**:
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Configuration:
     ```
     Name: secondbrain-api
     Environment: Python 3
     Build Command: pip install -r requirements.txt
     Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
     ```

2. **Environment Variables**:
   ```bash
   # Required
   DATABASE_URL=<your-postgresql-url-from-step-1>
   SECRET_KEY=<generate-32-character-secret>
   
   # Application
   ENVIRONMENT=production
   DEBUG=false
   ENABLE_HTTPS=true
   LOG_LEVEL=INFO
   
   # CORS - use host origins only, no path segments
   # Add your Render backend URL and GitHub Pages origin
   CORS_ORIGINS=https://octopus-ai-secondbrain.github.io,https://your-backend-name.onrender.com
   
   # Optional: AI Features
   OPENAI_API_KEY=<your-openai-api-key>  # Can also be set in Settings page
   
   # Server
   HOST=0.0.0.0
   ```

3. **Deploy**:
   - Click "Deploy Web Service"
   - First deployment takes 5-10 minutes
   - Your API will be available at: `https://your-service-name.onrender.com`

### Step 3: Configure Automatic Migrations

**IMPORTANT**: Database migrations must run before the application starts!

**Option 1: Use predeploy script (Recommended)**

Add to your Render web service configuration:
```bash
# In Render Dashboard → Settings → Build & Deploy
Build Command: pip install -r requirements.txt
Pre-Deploy Command: alembic upgrade head
Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

**Option 2: Manual migration via Shell** (for first-time setup):

1. **Connect to Render Shell**:
   - Go to your web service dashboard
   - Click "Shell" tab
   - Run migrations:
   ```bash
   alembic upgrade head
   ```

2. **Create Admin User** (optional):
   ```bash
   python scripts/migrate_add_admin.py
   ```

The application startup will now fail gracefully with a 503 error if migrations haven't been run, preventing silent schema issues.

## 🔧 Configuration Updates

### Update Frontend API URL

Update your GitHub repository secret:
```bash
# GitHub repo → Settings → Secrets → Actions
VITE_API_URL=https://your-actual-backend-name.onrender.com
```

### Required Environment Variables

**Backend (Render)**:
```bash
# Database
DATABASE_URL=<postgresql-connection-string>

# Security  
SECRET_KEY=<32-character-random-string>
ENVIRONMENT=production
ENABLE_HTTPS=true

# CORS - GitHub Pages and Render origins
CORS_ORIGINS=https://octopus-ai-secondbrain.github.io,https://your-backend.onrender.com
GITHUB_PAGES_URL=https://octopus-ai-secondbrain.github.io
RENDER_EXTERNAL_URL=https://your-backend.onrender.com

# Optional
OPENAI_API_KEY=<your-openai-key>
```

**Frontend (GitHub Secrets)**:
```bash
VITE_API_URL=https://your-backend.onrender.com
```

### Test the Deployment

1. **Frontend**: Visit `https://octopus-ai-secondbrain.github.io/secondbrain/`
2. **Backend Health**: Visit `https://your-backend.onrender.com/health`
3. **API Docs**: Visit `https://your-backend.onrender.com/docs`

### Testing Cross-Origin Authentication

1. **Sign up**: Create an account from the frontend
2. **Login**: Test authentication flow
3. **Check cookies**: Verify cookies are set with `SameSite=None` in production
4. **Protected routes**: Test authenticated API calls

## 🔒 Security Considerations

### Production Secrets

Generate strong secrets:
```bash
# Generate SECRET_KEY (32+ characters)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use openssl
openssl rand -base64 32
```

### Cross-Origin Authentication

The backend is configured to support cross-origin authentication from GitHub Pages to Render:

- **Cookies**: Use `SameSite=None; Secure` when `ENABLE_HTTPS=true` for cross-site cookies to work
- **CORS**: Properly configured to accept credentials from GitHub Pages origin
- **HTTPS Required**: Both frontend and backend must use HTTPS for cross-origin cookies

### Environment Variables

Never commit real secrets to git. Use:
- `.env` or `.env.development` for local development (gitignored)
- Render environment variables for backend production config
- GitHub Secrets for frontend build-time variables (VITE_API_URL)

## 🚨 Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Check `CORS_ORIGINS` includes your GitHub Pages URL
   - Verify frontend `VITE_API_URL` points to correct backend

2. **Database Connection**:
   - Ensure `DATABASE_URL` is correctly set
   - Check Render database is running
   - Verify migrations have been run

3. **Authentication Issues**:
   - Check `SECRET_KEY` is set and consistent
   - Verify JWT tokens are being sent correctly

4. **Build Failures**:
   - Check build logs in Render dashboard
   - Ensure all dependencies in `requirements.txt`
   - Verify Python version compatibility

### Logs and Monitoring

1. **Frontend Logs**: GitHub Actions tab shows build logs
2. **Backend Logs**: Render service dashboard → Logs tab
3. **Database Logs**: Render PostgreSQL dashboard → Logs

## 💰 Cost Estimation

### Free Tier Limits

**GitHub Pages**: Unlimited for public repos
**Render Free Tier**:
- Web Service: 750 hours/month (enough for 24/7)
- PostgreSQL: 1GB storage, 1 month retention
- Limitations: Sleeps after 15 min inactivity

### Upgrading to Paid

For production use, consider:
- **Render Starter Plan** ($7/month): No sleep, better performance
- **PostgreSQL Starter** ($7/month): 1GB storage, daily backups

## 🔄 CI/CD Pipeline

### Automatic Deployments

1. **Frontend**: Auto-deploys on push to `main`
2. **Backend**: Auto-deploys on push to `main` (if connected to GitHub)

### Manual Deployments

```bash
# Frontend only
git push origin main

# Force backend redeploy (if needed)
# Go to Render dashboard → Manual Deploy
```

## 📱 Mobile Considerations

The app is responsive and works on mobile browsers. For better mobile experience:
1. Add PWA manifest (future enhancement)
2. Optimize for touch interactions
3. Consider offline functionality

---

## 🆘 Need Help?

1. **Frontend Issues**: Check GitHub Actions build logs
2. **Backend Issues**: Check Render service logs  
3. **Database Issues**: Check Render PostgreSQL logs
4. **CORS Issues**: Verify environment variables match URLs

For additional support, check the project issues or create a new one with:
- Error messages
- Relevant logs
- Steps to reproduce