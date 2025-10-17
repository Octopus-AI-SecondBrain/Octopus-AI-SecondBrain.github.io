# 🚀 Deployment Guide

This guide covers deploying the SecondBrain application with:
- **Frontend**: GitHub Pages (free, automatic deployment)
- **Backend**: Render.com (free tier available, managed PostgreSQL)

## 📋 Prerequisites

1. **GitHub Repository**: Push your code to GitHub
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **OpenAI API Key**: Required for embedding functionality

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
   - Push to `main` branch triggers automatic deployment
   - Visit: `https://octopus-ai-secondbrain.github.io/Octopus-AI-SecondBrain.github.io/`

### Manual Local Build

```bash
cd frontend
npm install
npm run build

# Test locally
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
   OPENAI_API_KEY=<your-openai-api-key>
   
   # Application
   ENVIRONMENT=production
   DEBUG=false
   ENABLE_HTTPS=true
   LOG_LEVEL=INFO
   
   # CORS (adjust if your frontend URL differs)
   CORS_ORIGINS=https://octopus-ai-secondbrain.github.io,https://octopus-ai-secondbrain.github.io/Octopus-AI-SecondBrain.github.io
   
   # Server
   HOST=0.0.0.0
   ```

3. **Deploy**:
   - Click "Deploy Web Service"
   - First deployment takes 5-10 minutes
   - Your API will be available at: `https://your-service-name.onrender.com`

### Step 3: Run Database Migrations

After first deployment:

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

## 🔧 Configuration Updates

### Update Frontend API URL

Update your GitHub repository secret:
```bash
# GitHub repo → Settings → Secrets → Actions
VITE_API_URL=https://your-actual-backend-name.onrender.com
```

Then redeploy frontend by pushing to main branch.

### Test the Deployment

1. **Frontend**: Visit `https://octopus-ai-secondbrain.github.io/Octopus-AI-SecondBrain.github.io/`
2. **Backend Health**: Visit `https://your-backend.onrender.com/health`
3. **API Docs**: Visit `https://your-backend.onrender.com/docs`

## 🔒 Security Considerations

### Production Secrets

Generate strong secrets:
```bash
# Generate SECRET_KEY (32+ characters)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use openssl
openssl rand -base64 32
```

### Environment Variables

Never commit real secrets to git. Use:
- `.env.development` for local development
- Render environment variables for production
- GitHub Secrets for frontend build-time variables

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