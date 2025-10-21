# 🚀 Deployment Checklist

Quick reference for deploying Second Brain to production.

## ✅ Pre-Deployment Checklist

### Backend Preparation
- [ ] PostgreSQL database configured
- [ ] Environment variables set (DATABASE_URL, SECRET_KEY, OPENAI_API_KEY)
- [ ] CORS configured for GitHub Pages domain
- [ ] Database migrations run (`alembic upgrade head`)
- [ ] Test endpoints working (`/health`, `/api/auth/login`)

### Frontend Preparation
- [ ] API URL updated in `frontend/src/utils/api.js`
- [ ] Landing page demo link updated (`docs/index.html` line 186)
- [ ] Beta signup form configured (Formspree or backend endpoint)
- [ ] Build successful (`npm run build` in frontend/)
- [ ] No console errors in development

### GitHub Configuration
- [ ] Repository is public (or GitHub Pages enabled for private)
- [ ] GitHub Actions workflow file exists (`.github/workflows/deploy.yml`)
- [ ] No secrets needed (API URLs are public)

## 🎯 Deployment Steps

### 1. Deploy Backend (Render.com)
```bash
# Step 1: Create PostgreSQL database on Render
# Step 2: Copy Internal Database URL
# Step 3: Create Web Service
# Step 4: Add environment variables
# Step 5: Wait for build (5-10 min)
# Step 6: Run migrations in Shell tab
# Step 7: Test: curl https://your-app.onrender.com/health
```

**Status**: [ ] Backend deployed and healthy

### 2. Configure Beta Signups
```bash
# Option A: Formspree (recommended)
# - Sign up at formspree.io
# - Create form, get ID
# - Update docs/script.js line 42 with form ID
# - Uncomment lines 41-46

# Option B: Backend endpoint
# - Create /api/beta-signup endpoint
# - Update docs/script.js line 49 with URL

# Option C: Keep localStorage
# - No changes needed
# - Run exportBetaSignups() in console to download
```

**Status**: [ ] Beta form configured

### 3. Update URLs
```bash
# File: docs/index.html line 186
# Change: localhost:3000 → your-username.github.io/secondbrain/app/

# File: frontend/src/utils/api.js
# Change: API_BASE_URL → https://your-app.onrender.com/api

# File: backend/main.py
# Add to CORS: "https://your-username.github.io"
```

**Status**: [ ] All URLs updated

### 4. Deploy to GitHub Pages
```bash
cd /Users/noel.thomas/secondbrain

# Commit all changes
git add .
git commit -m "Deploy to production"
git push origin main

# Wait 3-5 minutes
# Check Actions tab for deployment status
```

**Status**: [ ] GitHub Actions successful

### 5. Enable GitHub Pages
```bash
# GitHub repo → Settings → Pages
# Source: Deploy from branch
# Branch: gh-pages / (root)
# Save and wait 2 minutes
```

**Status**: [ ] GitHub Pages enabled

### 6. Verify Deployment
- [ ] Landing page loads: `https://your-username.github.io/secondbrain/`
- [ ] Hero section visible with animated neural map
- [ ] "Try Demo" button works
- [ ] App loads: `https://your-username.github.io/secondbrain/app/`
- [ ] Can create account in app
- [ ] Can login
- [ ] Can create note
- [ ] Can see notes in list
- [ ] Can search notes
- [ ] Neural map renders (2D and 3D)
- [ ] Beta form submits successfully
- [ ] Success message shows after form submission
- [ ] No console errors

## 🐛 Common Issues

### Issue: "Application not responding" on Render
**Solution**: Free tier spins down after 15 min. Wait 30-60 seconds for wake up.

### Issue: CORS error in browser console
**Solution**: Add GitHub Pages URL to `backend/main.py` CORS `allow_origins`

### Issue: App loads but shows login error
**Solution**: Check `VITE_API_URL` in GitHub Actions workflow environment variables

### Issue: Beta form doesn't submit
**Solution**: 
- Check Formspree quota (50/month free)
- Verify form ID in `docs/script.js`
- Check browser console for errors

### Issue: GitHub Actions fails
**Solution**: 
- Check Actions tab → View logs
- Common: Node version mismatch (use Node 20)
- Common: npm install fails (delete package-lock.json and regenerate)

### Issue: 404 on app URL
**Solution**: 
- Ensure workflow copied `frontend/dist/*` to `docs/app/`
- Check `.nojekyll` file exists in `docs/`
- Re-run GitHub Actions workflow

## 📊 Post-Deployment

### Monitor
- [ ] Set up Google Analytics (optional)
- [ ] Check Render dashboard daily for errors
- [ ] Monitor beta signup count
- [ ] Check GitHub Actions for failed builds

### Share
- [ ] Post on Twitter/X
- [ ] Post on LinkedIn
- [ ] Share in relevant communities (Reddit, Discord, etc.)
- [ ] Add to Product Hunt (when ready)
- [ ] Email existing contacts

### Iterate
- [ ] Collect user feedback
- [ ] Fix reported bugs
- [ ] Add requested features
- [ ] Update landing page with testimonials
- [ ] Create demo video

## 🎉 Success!

Your Second Brain is live! Now focus on:
1. **User acquisition**: Share landing page URL
2. **Beta testing**: Onboard first 10-50 users
3. **Iteration**: Fix bugs, add features based on feedback
4. **Marketing**: Blog posts, social media, demo videos
5. **Scaling**: Monitor usage, upgrade tiers when needed

---

**Landing Page**: https://your-username.github.io/secondbrain/  
**App**: https://your-username.github.io/secondbrain/app/  
**Backend**: https://your-app.onrender.com  

**Next Steps**: Share your landing page and start collecting beta signups! 🚀
