# 🚀 Octopus SecondBrain - Complete Deployment Guide# 🚀 Deployment Guide



> **Production-ready deployment guide for your AI-powered knowledge management system**This guide covers deploying the SecondBrain application with:

- **Frontend**: GitHub Pages (free, automatic deployment) - React + Vite SPA

---- **Backend**: Render.com (free tier available, managed PostgreSQL)



## 📋 Quick Navigation## 📋 Prerequisites



- [**Quick Start**](#-quick-start) - Get deployed in under 2 hours1. **GitHub Repository**: Push your code to GitHub

- [**Hosting Setup**](#%EF%B8%8F-hosting-setup) - Database, Backend, Frontend2. **Render Account**: Sign up at [render.com](https://render.com)

- [**Configuration**](#-environment-configuration) - Environment variables3. **OpenAI API Key** (Optional): For AI-powered search explanations (can also be set in Settings page)

- [**Troubleshooting**](#-troubleshooting) - Common issues and fixes

## 🌐 Frontend Deployment (GitHub Pages)

---

### Automatic Deployment Setup

## 🎯 Quick Start

1. **Enable GitHub Pages**:

### What You'll Deploy   ```bash

   # Go to your GitHub repo → Settings → Pages

```   # Source: Deploy from a branch

Frontend:  GitHub Pages (FREE)   # Branch: gh-pages

Backend:   Render.com (FREE → $7/month)   # Folder: / (root)

Database:  Supabase PostgreSQL (FREE → $25/month)   ```



Total Cost: $0 (testing) → $32/month (production)2. **Set Repository Secret**:

Timeline:   1-2 hours setup   ```bash

```   # Go to GitHub repo → Settings → Secrets and variables → Actions

   # Add new repository secret:

### Architecture   Name: VITE_API_URL

   Value: https://your-backend-name.onrender.com

```   ```

GitHub Pages (React) → Render.com (FastAPI) → Supabase (PostgreSQL + pgvector)

```3. **Deploy**:

   - Push to `main` branch triggers automatic deployment via GitHub Actions

---   - The workflow builds the Vite app and deploys to gh-pages branch

   - Visit: `https://octopus-ai-secondbrain.github.io/Octopus-AI-SecondBrain.github.io/`

## 🗄️ Step 1: Database (Supabase)

### Manual Local Build

### 1.1 Create Project

```bash

1. Go to [supabase.com](https://supabase.com) → Sign upcd frontend

2. New Project:npm install

   - Name: `secondbrain-prod`npm run build

   - Password: **Save securely!**

   - Region: Closest to users# Test production build locally

3. Wait ~2 minutes for initializationnpm run preview

```

### 1.2 Get Connection String

## 🖥️ Backend Deployment (Render.com)

```bash

# Settings > Database > Connection string > URI format:### Step 1: Create PostgreSQL Database

postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres

```1. **Create Database**:

   - Go to [Render Dashboard](https://dashboard.render.com)

### 1.3 Enable Vectors   - Click "New" → "PostgreSQL"

   - Name: `secondbrain-db`

```sql   - Plan: Free (or paid for production)

-- SQL Editor > New Query:   - Region: Choose closest to your users

CREATE EXTENSION IF NOT EXISTS vector;

```2. **Note Database Details**:

   - Save the `DATABASE_URL` (Internal Database URL)

### 1.4 Run Migrations

### Step 2: Create Web Service

```bash

# From your local machine:1. **Create Web Service**:

export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres"   - Click "New" → "Web Service"

alembic upgrade head   - Connect your GitHub repository

```   - Configuration:

     ```

**Verify:** Check Table Editor for `users`, `notes`, `tags` tables     Name: secondbrain-api

     Environment: Python 3

---     Build Command: pip install -r requirements.txt

     Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT

## 🖥️ Step 2: Backend (Render.com)     ```



### 2.1 Create Service2. **Environment Variables**:

   ```bash

1. Go to [render.com](https://render.com) → Sign up   # Required

2. New → Web Service   DATABASE_URL=<your-postgresql-url-from-step-1>

3. Connect GitHub repo: `Octopus-AI-SecondBrain/Octopus-AI-SecondBrain.github.io`   SECRET_KEY=<generate-32-character-secret>

   

### 2.2 Configure   # Application

   ENVIRONMENT=production

**Basic:**   DEBUG=false

```   ENABLE_HTTPS=true

Name:        secondbrain-api   LOG_LEVEL=INFO

Environment: Python 3   

Region:      Oregon   # CORS - use host origins only, no path segments

Branch:      main   # Add your Render backend URL and GitHub Pages origin

```   CORS_ORIGINS=https://octopus-ai-secondbrain.github.io,https://your-backend-name.onrender.com

   

**Build:**   # Optional: AI Features

```bash   OPENAI_API_KEY=<your-openai-api-key>  # Can also be set in Settings page

# Build Command:   

pip install -r requirements.txt   # Server

   HOST=0.0.0.0

# Start Command:   ```

uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 1

```3. **Deploy**:

   - Click "Deploy Web Service"

### 2.3 Environment Variables   - First deployment takes 5-10 minutes

   - Your API will be available at: `https://your-service-name.onrender.com`

```bash

# REQUIRED### Step 3: Configure Automatic Migrations

DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres

SECRET_KEY=[openssl rand -base64 48]**IMPORTANT**: Database migrations must run before the application starts!

ENVIRONMENT=production

GITHUB_PAGES_URL=https://octopus-ai-secondbrain.github.io**Option 1: Use predeploy script (Recommended)**

CORS_ORIGINS=https://octopus-ai-secondbrain.github.io

Add to your Render web service configuration:

# RECOMMENDED```bash

DEBUG=false# In Render Dashboard → Settings → Build & Deploy

ENABLE_HTTPS=trueBuild Command: pip install -r requirements.txt

LOG_LEVEL=INFOPre-Deploy Command: alembic upgrade head

Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT

# OPTIONAL```

OPENAI_API_KEY=sk-xxxxx

```**Option 2: Manual migration via Shell** (for first-time setup):



### 2.4 Deploy1. **Connect to Render Shell**:

   - Go to your web service dashboard

1. Click "Create Web Service"   - Click "Shell" tab

2. Wait 3-5 minutes   - Run migrations:

3. Test: Visit `https://secondbrain-api.onrender.com/health`   ```bash

4. Should see: `{"status":"healthy"}`   alembic upgrade head

   ```

**Save your URL:** `https://secondbrain-api.onrender.com`

2. **Create Admin User** (optional):

---   ```bash

   python scripts/migrate_add_admin.py

## 🎨 Step 3: Frontend (GitHub Pages)   ```



### 3.1 Update API ConfigurationThe application startup will now fail gracefully with a 503 error if migrations haven't been run, preventing silent schema issues.



Edit `frontend/src/utils/api.js`:## 🔧 Configuration Updates



```javascript### Update Frontend API URL

const API_URL = import.meta.env.VITE_API_URL || 

                (import.meta.env.PROD Update your GitHub repository secret:

                  ? 'https://secondbrain-api.onrender.com'  // ← Your URL```bash

                  : 'http://localhost:8000')# GitHub repo → Settings → Secrets → Actions

```VITE_API_URL=https://your-actual-backend-name.onrender.com

```

### 3.2 Update GitHub Actions

### Required Environment Variables

Edit `.github/workflows/deploy-pages.yml`:

**Backend (Render)**:

```yaml```bash

- name: Build# Database

  env:DATABASE_URL=<postgresql-connection-string>

    VITE_API_URL: https://secondbrain-api.onrender.com  # ← Add this

  run: |# Security  

    cd frontendSECRET_KEY=<32-character-random-string>

    npm ciENVIRONMENT=production

    npm run buildENABLE_HTTPS=true

```

# CORS - GitHub Pages and Render origins

### 3.3 DeployCORS_ORIGINS=https://octopus-ai-secondbrain.github.io,https://your-backend.onrender.com

GITHUB_PAGES_URL=https://octopus-ai-secondbrain.github.io

```bashRENDER_EXTERNAL_URL=https://your-backend.onrender.com

git add frontend/src/utils/api.js .github/workflows/deploy-pages.yml

git commit -m "Configure production API"# Optional

git push origin mainOPENAI_API_KEY=<your-openai-key>

``````



GitHub Actions will auto-deploy to: `https://octopus-ai-secondbrain.github.io`**Frontend (GitHub Secrets)**:

```bash

---VITE_API_URL=https://your-backend.onrender.com

```

## ✅ Verification

### Test the Deployment

### Test End-to-End

1. **Frontend**: Visit `https://octopus-ai-secondbrain.github.io/secondbrain/`

1. Visit `https://octopus-ai-secondbrain.github.io`2. **Backend Health**: Visit `https://your-backend.onrender.com/health`

2. Open browser console (F12)3. **API Docs**: Visit `https://your-backend.onrender.com/docs`

3. Check network tab shows requests to Render

4. Sign up for new account### Testing Cross-Origin Authentication

5. Create a note

6. Verify it saves1. **Sign up**: Create an account from the frontend

2. **Login**: Test authentication flow

### Health Checks3. **Check cookies**: Verify cookies are set with `SameSite=None` in production

4. **Protected routes**: Test authenticated API calls

```bash

# Backend:## 🔒 Security Considerations

curl https://secondbrain-api.onrender.com/health

### Production Secrets

# Frontend:

curl -I https://octopus-ai-secondbrain.github.ioGenerate strong secrets:

``````bash

# Generate SECRET_KEY (32+ characters)

---python -c "import secrets; print(secrets.token_urlsafe(32))"



## 🔧 Environment Configuration# Or use openssl

openssl rand -base64 32

### Complete Variable Reference```



#### Backend (Render)### Cross-Origin Authentication



```bashThe backend is configured to support cross-origin authentication from GitHub Pages to Render:

# Database

DATABASE_URL=postgresql://...  # From Supabase- **Cookies**: Use `SameSite=None; Secure` when `ENABLE_HTTPS=true` for cross-site cookies to work

- **CORS**: Properly configured to accept credentials from GitHub Pages origin

# Security  - **HTTPS Required**: Both frontend and backend must use HTTPS for cross-origin cookies

SECRET_KEY=[32+ character string]  # openssl rand -base64 48

ENVIRONMENT=production### Environment Variables

DEBUG=false

Never commit real secrets to git. Use:

# CORS- `.env` or `.env.development` for local development (gitignored)

GITHUB_PAGES_URL=https://octopus-ai-secondbrain.github.io- Render environment variables for backend production config

CORS_ORIGINS=https://octopus-ai-secondbrain.github.io- GitHub Secrets for frontend build-time variables (VITE_API_URL)



# Optional## 🚨 Troubleshooting

OPENAI_API_KEY=sk-xxx  # For embeddings

ENABLE_HTTPS=true### Common Issues

LOG_LEVEL=INFO

ACCESS_TOKEN_EXPIRE_MINUTES=301. **CORS Errors**:

```   - Check `CORS_ORIGINS` includes your GitHub Pages URL

   - Verify frontend `VITE_API_URL` points to correct backend

#### Frontend (GitHub Actions)

2. **Database Connection**:

```yaml   - Ensure `DATABASE_URL` is correctly set

# In .github/workflows/deploy-pages.yml   - Check Render database is running

env:   - Verify migrations have been run

  VITE_API_URL: https://secondbrain-api.onrender.com

```3. **Authentication Issues**:

   - Check `SECRET_KEY` is set and consistent

---   - Verify JWT tokens are being sent correctly



## 🐛 Troubleshooting4. **Build Failures**:

   - Check build logs in Render dashboard

### "CORS Error"   - Ensure all dependencies in `requirements.txt`

   - Verify Python version compatibility

```bash

# Fix: Ensure CORS_ORIGINS matches exactly (no trailing slash):### Logs and Monitoring

CORS_ORIGINS=https://octopus-ai-secondbrain.github.io

1. **Frontend Logs**: GitHub Actions tab shows build logs

# Restart Render service after changing2. **Backend Logs**: Render service dashboard → Logs tab

```3. **Database Logs**: Render PostgreSQL dashboard → Logs



### "Failed to fetch" in Frontend## 💰 Cost Estimation



```javascript### Free Tier Limits

// Check API URL in browser console

// Should be HTTPS (not HTTP)**GitHub Pages**: Unlimited for public repos

// Verify in frontend/src/utils/api.js**Render Free Tier**:

```- Web Service: 750 hours/month (enough for 24/7)

- PostgreSQL: 1GB storage, 1 month retention

### "Database connection failed"- Limitations: Sleeps after 15 min inactivity



```bash### Upgrading to Paid

# Verify DATABASE_URL format:

postgresql://postgres:PASSWORD@db.REF.supabase.co:5432/postgresFor production use, consider:

- **Render Starter Plan** ($7/month): No sleep, better performance

# Test with psql:- **PostgreSQL Starter** ($7/month): 1GB storage, daily backups

psql "YOUR_DATABASE_URL"

```## 🔄 CI/CD Pipeline



### Backend Sleeping (Free Tier)### Automatic Deployments



```bash1. **Frontend**: Auto-deploys on push to `main`

# Free tier sleeps after 15min2. **Backend**: Auto-deploys on push to `main` (if connected to GitHub)

# Cold start takes ~10-20 seconds

# Upgrade to $7/month for always-on### Manual Deployments

```

```bash

### "SECRET_KEY too short"# Frontend only

git push origin main

```bash

# Generate proper key:# Force backend redeploy (if needed)

openssl rand -base64 48# Go to Render dashboard → Manual Deploy

```

# Must be 32+ characters

```## 📱 Mobile Considerations



---The app is responsive and works on mobile browsers. For better mobile experience:

1. Add PWA manifest (future enhancement)

## 💰 Pricing & Upgrades2. Optimize for touch interactions

3. Consider offline functionality

### Free Tier (Perfect for Testing)

---

```

GitHub Pages:  $0/month  ✅ Unlimited## 🆘 Need Help?

Render:        $0/month  ⚠️  Sleeps after 15min

Supabase:      $0/month  ⚠️  500MB limit1. **Frontend Issues**: Check GitHub Actions build logs

──────────────────────────────────────2. **Backend Issues**: Check Render service logs  

Total:         $0/month3. **Database Issues**: Check Render PostgreSQL logs

```4. **CORS Issues**: Verify environment variables match URLs



### Production Tier (Recommended)For additional support, check the project issues or create a new one with:

- Error messages

```- Relevant logs

GitHub Pages:  $0/month- Steps to reproduce
Render:        $7/month  ✅ Always-on
Supabase:     $25/month  ✅ 8GB + backups
──────────────────────────────────────
Total:        $32/month
```

### When to Upgrade

- **Render ($7/month):** When cold starts annoy users
- **Supabase ($25/month):** When approaching 500MB data

---

## 📊 Monitoring

### Logs

**Render:**
1. Dashboard → secondbrain-api → Logs
2. Filter: ERROR or WARNING

**Supabase:**
1. Dashboard → Database → Logs
2. Check slow queries

### Backups

**Automatic** (Supabase Pro $25/month):
- Daily backups
- Point-in-time recovery

**Manual**:
```bash
pg_dump "DATABASE_URL" > backup-$(date +%Y%m%d).sql
```

---

## 🎉 Success Checklist

Your deployment is complete when:

- ✅ Frontend loads at GitHub Pages
- ✅ Backend /health returns 200
- ✅ Can create account
- ✅ Can add/edit notes
- ✅ Search works
- ✅ Neural map loads
- ✅ No console errors
- ✅ HTTPS everywhere

---

## 📚 Resources

- **Supabase Docs**: https://supabase.com/docs
- **Render Docs**: https://render.com/docs
- **GitHub Pages**: https://docs.github.com/pages
- **Issues**: https://github.com/Octopus-AI-SecondBrain/Octopus-AI-SecondBrain.github.io/issues

---

## 🔐 Security Checklist

- [ ] SECRET_KEY is strong (32+ chars)
- [ ] All secrets in environment (not in code)
- [ ] HTTPS enabled everywhere
- [ ] DEBUG=false in production
- [ ] Database password is secure
- [ ] CORS_ORIGINS is restrictive

---

## 🚀 Next Steps After Deployment

1. **Custom Domain** (Optional)
   - Add to GitHub Pages settings
   - Update CORS_ORIGINS

2. **Monitoring** (Recommended)
   - Set up error tracking (Sentry)
   - Uptime monitoring

3. **Backups** (Important)
   - Enable Supabase backups
   - Test restoration

4. **Upgrade** (When Ready)
   - Render Pro ($7/month) for no sleep
   - Supabase Pro ($25/month) for backups

---

**Need Help?** Open an issue or check troubleshooting above.

**Live App**: https://octopus-ai-secondbrain.github.io  
**API**: https://secondbrain-api.onrender.com
