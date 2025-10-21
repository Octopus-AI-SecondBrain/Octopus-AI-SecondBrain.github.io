# 🚀 Complete Deployment Guide

This guide walks you through deploying your Second Brain app with a landing page on GitHub Pages and backend on Render.com - **completely free** using free tiers.

## 📋 Architecture Overview

- **Landing Page**: GitHub Pages (free, fast CDN)
  - URL: `https://yourusername.github.io/secondbrain/`
  - Content: Hero, features, demo video, beta signup form
  
- **React App**: GitHub Pages at `/app` subdirectory (free)
  - URL: `https://yourusername.github.io/secondbrain/app/`
  - Full Second Brain application
  
- **Backend API**: Render.com (free tier, 750 hours/month)
  - URL: `https://secondbrain-api.onrender.com/`
  - FastAPI, PostgreSQL database

- **Beta Signups**: Formspree (free, 50 submissions/month)
  - Or store in localStorage for now

## 🎯 Step 1: Deploy Backend to Render.com

### 1.1 Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (easiest option)
3. Verify email

### 1.2 Create PostgreSQL Database
1. Click **"New +"** → **"PostgreSQL"**
2. Settings:
   - Name: `secondbrain-db`
   - Database: `secondbrain`
   - User: (auto-generated)
   - Region: Choose closest to you
   - Plan: **Free** (0 GB storage, good for beta)
3. Click **"Create Database"**
4. Wait 2-3 minutes for provisioning
5. **Copy the Internal Database URL** (starts with `postgresql://`)

### 1.3 Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Settings:
   - Name: `secondbrain-api`
   - Region: Same as database
   - Branch: `main`
   - Root Directory: `.` (leave blank)
   - Runtime: **Python 3**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Plan: **Free** (512 MB RAM, spins down after 15 min inactivity)

4. **Environment Variables** (click "Advanced" → "Add Environment Variable"):
   ```
   DATABASE_URL = <paste Internal Database URL from step 1.2>
   SECRET_KEY = <generate random 32-character string>
   OPENAI_API_KEY = <your OpenAI key if you want semantic search>
   ENVIRONMENT = production
   ALLOWED_ORIGINS = https://yourusername.github.io
   ```

5. Click **"Create Web Service"**
6. Wait 5-10 minutes for first deployment
7. Check logs for "Application startup complete"
8. **Copy your service URL**: `https://secondbrain-api.onrender.com`

### 1.4 Run Database Migrations
1. In Render dashboard, go to your web service
2. Click **"Shell"** tab (opens terminal)
3. Run:
   ```bash
   alembic upgrade head
   python scripts/migrate_add_admin.py
   ```

### 1.5 Test Backend
```bash
curl https://secondbrain-api.onrender.com/health
# Should return: {"status":"healthy","version":"1.0.0"}
```

## 🎯 Step 2: Configure Beta Signup Form

### Option A: Formspree (Recommended - Easiest)
1. Go to [formspree.io](https://formspree.io)
2. Sign up (free tier: 50 submissions/month)
3. Create new form
4. Copy form ID (looks like `xvgopqrs`)
5. Update `docs/script.js` line 42:
   ```javascript
   const response = await fetch('https://formspree.io/f/xvgopqrs', {
   ```
6. Uncomment lines 41-46 and comment out lines 57-60 (simulation code)

### Option B: Backend Endpoint (More Control)
1. Create endpoint in `backend/routes/auth.py`:
   ```python
   @router.post("/beta-signup")
   async def beta_signup(
       email: str = Body(...),
       name: str = Body(None),
       use_case: str = Body(None),
       db: Session = Depends(get_db)
   ):
       # Store in database
       # Send confirmation email
       return {"message": "Success"}
   ```
2. Update `docs/script.js` line 49 with your backend URL

### Option C: Keep LocalStorage (For Testing)
- Current setup stores signups in browser localStorage
- Run `exportBetaSignups()` in console to download CSV
- Good for initial testing before setting up backend

## 🎯 Step 3: Update Frontend URLs

### 3.1 Update Landing Page Demo Link
Edit `docs/index.html` line 186:
```html
<a href="https://yourusername.github.io/secondbrain/app/" 
   id="launchDemo" 
   class="btn btn-primary">
```

### 3.2 Update API URL in Frontend
Edit `frontend/src/utils/api.js`:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 
  'https://secondbrain-api.onrender.com/api';
```

### 3.3 Update Backend CORS
Edit `backend/main.py` to allow GitHub Pages:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://yourusername.github.io"  # Add this
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🎯 Step 4: Deploy to GitHub Pages

### 4.1 Enable GitHub Pages
1. Go to your GitHub repository
2. **Settings** → **Pages**
3. Source: **Deploy from a branch**
4. Branch: **gh-pages** / **(root)**
5. Click **Save**

### 4.2 Push to GitHub
```bash
cd /Users/noel.thomas/secondbrain

# Commit all changes
git add .
git commit -m "Add landing page and deployment configuration"
git push origin main
```

### 4.3 Monitor Deployment
1. Go to **Actions** tab in GitHub
2. Watch workflow "Deploy to GitHub Pages"
3. Should take 3-5 minutes
4. Check logs for errors
5. Once complete, go to **Settings** → **Pages**
6. Click the URL (e.g., `https://yourusername.github.io/secondbrain/`)

### 4.4 Test Deployment
1. Landing page loads: `https://yourusername.github.io/secondbrain/`
2. App loads: `https://yourusername.github.io/secondbrain/app/`
3. Beta form works
4. "Try Demo" button opens app
5. App connects to backend (check browser console for errors)

## 🎯 Step 5: Update Repository README

Add deployment URLs to your README.md:
```markdown
## 🌐 Live Demo

- **Landing Page**: https://yourusername.github.io/secondbrain/
- **App**: https://yourusername.github.io/secondbrain/app/
- **API**: https://secondbrain-api.onrender.com

## 🚀 Quick Start

### Try the Demo
Visit [our landing page](https://yourusername.github.io/secondbrain/) and click "Try Demo"

### Sign Up for Beta
Join our waitlist at [secondbrain.io](https://yourusername.github.io/secondbrain/#beta)
```

## 🎯 Step 6: Optional Enhancements

### 6.1 Custom Domain (Optional)
If you own a domain (e.g., `secondbrain.io`):
1. Add `CNAME` file to `docs/` with domain name
2. Configure DNS:
   - Type: CNAME
   - Name: @ (or subdomain)
   - Value: `yourusername.github.io`
3. GitHub Settings → Pages → Custom domain: `secondbrain.io`

### 6.2 Analytics (Optional)
Add Google Analytics to `docs/index.html`:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### 6.3 Demo Video
1. Record screencast with QuickTime or OBS
2. Upload to YouTube
3. Update `docs/index.html` line 147:
   ```html
   <iframe 
     src="https://www.youtube.com/embed/YOUR_VIDEO_ID"
     frameborder="0" 
     allowfullscreen>
   </iframe>
   ```

### 6.4 SSL Certificate (Automatic)
- GitHub Pages automatically provides HTTPS
- Render.com automatically provides HTTPS
- No action needed!

## 🎯 Step 7: Monitoring & Maintenance

### Backend Monitoring (Render.com)
1. Dashboard shows:
   - Uptime (should be ~99.9%)
   - Response time
   - Memory usage
   - Error rate
2. Free tier spins down after 15 min inactivity
   - First request after sleep: 30-60 second delay
   - Subsequent requests: fast
3. Logs available in Dashboard → Logs tab

### Frontend Monitoring
1. GitHub Pages uptime: 99.9%+
2. Check **Actions** tab for deployment status
3. Monitor browser console for JS errors

### Database Backups
- Render free tier: No automated backups
- Manual backup command:
  ```bash
  pg_dump DATABASE_URL > backup.sql
  ```

## 🎯 Troubleshooting

### Landing page loads but app shows 404
- Check GitHub Actions logs
- Ensure `docs/app/` directory exists with built frontend
- Check `.nojekyll` file exists in `docs/`

### App loads but can't connect to backend
- Check browser console for CORS errors
- Verify `ALLOWED_ORIGINS` in Render environment variables
- Check backend logs in Render dashboard

### Beta form doesn't submit
- Check Formspree quota (50/month free tier)
- Verify form ID in `docs/script.js`
- Check browser console for errors

### Backend shows "Application not responding"
- Free tier spins down after 15 min inactivity
- Wait 30-60 seconds for wake up
- Consider upgrading to paid tier ($7/month) for always-on

### Search returns no results
- Check OpenAI API key in Render environment variables
- Verify OpenAI billing is set up
- Check backend logs for "OpenAI API error"
- Fallback: System uses hashed embeddings (lower quality)

## 💰 Cost Breakdown

### Current Setup (Free)
- GitHub Pages: $0/month (unlimited static hosting)
- Render.com Web Service: $0/month (512 MB RAM, 750 hours)
- Render.com PostgreSQL: $0/month (1 GB storage)
- Formspree: $0/month (50 submissions)
- OpenAI API: ~$0.10-0.20/month (with $5 credit)
- **Total: $0-0.20/month** ✅

### Future Scaling (Paid Tiers)
When you exceed free limits:
- Render Web Service: $7/month (always-on, 512 MB RAM)
- Render PostgreSQL: $7/month (10 GB storage, backups)
- Formspree: $10/month (1000 submissions)
- OpenAI API: ~$5-20/month (depends on usage)
- **Total with users: ~$30-45/month**

## 🎉 You're Live!

Your Second Brain is now deployed and accessible worldwide:
- ✅ Landing page for user acquisition
- ✅ Full app with 3D neural map
- ✅ Beta signup form
- ✅ Backend API with database
- ✅ Semantic search (with OpenAI)
- ✅ Free hosting (GitHub Pages + Render)

Share your landing page URL on social media and start collecting beta signups! 🚀

## 📞 Need Help?

- GitHub Issues: Report bugs
- GitHub Discussions: Ask questions
- Email: support@yourdomain.com (set this up)

---

**Note**: After deployment, monitor your first few signups to ensure everything works. Then focus on user feedback and iteration! 🎯
