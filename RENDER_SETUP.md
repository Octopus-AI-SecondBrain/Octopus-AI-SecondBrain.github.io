# Render Setup Checklist ✅

## Backend Deployment Status

🎉 **Your backend is deployed at:** https://octopus-fa0y.onrender.com

### Required Environment Variables in Render

Go to your Render dashboard → `octopus-api` service → **Environment** tab and verify these are set:

#### ✅ Required Variables:

```bash
SECRET_KEY=Yo-awBGqFT0CMs9yquzAXt-nfB0nd-sqqp2NrWnVpD0
ENVIRONMENT=production
ENABLE_HTTPS=true
CORS_ORIGINS=https://octopus-ai-secondbrain.github.io
LOG_LEVEL=INFO
```

#### ⚠️ Important: Update CORS_ORIGINS

After the push, Render will automatically redeploy (takes ~5 minutes). Once it's done:

1. Go to Render dashboard: https://dashboard.render.com
2. Click on your `octopus-api` service
3. Go to **Environment** tab
4. Find `CORS_ORIGINS` and update it to:
   ```
   https://octopus-ai-secondbrain.github.io
   ```
5. Click **Save Changes** (this will trigger a redeploy)

---

## Frontend Deployment (GitHub Pages)

### Step 1: Enable GitHub Pages

1. Go to: https://github.com/Octopus-AI-SecondBrain/octopus/settings/pages
2. Under **Build and deployment**:
   - Source: **GitHub Actions**
3. Wait 2-3 minutes for the workflow to run

### Step 2: Check Deployment

1. Go to: https://github.com/Octopus-AI-SecondBrain/octopus/actions
2. You should see a workflow running called "Deploy to GitHub Pages"
3. Once it's green ✅, your site will be live at:
   
   **https://octopus-ai-secondbrain.github.io/octopus**

---

## Testing Your Live Site

### 1. Test Backend Health

```bash
curl https://octopus-fa0y.onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "production"
}
```

### 2. Test Backend Docs

Visit: https://octopus-fa0y.onrender.com/docs

⚠️ **Note:** Docs are disabled in production for security. You can enable them temporarily by setting:
```
ENVIRONMENT=development
```
in Render, but remember to switch back to `production` after testing!

### 3. Test Frontend

1. Visit: https://octopus-ai-secondbrain.github.io/octopus
2. Click **Sign Up**
3. Create an account with:
   - Username: min 3 characters, alphanumeric
   - Password: min 8 characters, must include uppercase, lowercase, and digit
   - Example: `testuser` / `TestPass123`
4. Create a note
5. View the 3D visualization

---

## Troubleshooting

### Issue: Backend shows "Not Found" (404)

**Check Render logs:**
1. Go to Render dashboard
2. Click your service
3. Click **Logs** tab
4. Look for startup errors

**Common causes:**
- Database initialization failed
- Python dependencies missing
- PORT environment variable incorrect

**Solution:** The latest push includes a better entrypoint script that shows detailed error messages.

### Issue: Frontend can't connect to backend (CORS error)

**Symptoms:** Browser console shows:
```
Access to XMLHttpRequest at 'https://octopus-fa0y.onrender.com' 
from origin 'https://octopus-ai-secondbrain.github.io' 
has been blocked by CORS policy
```

**Solution:**
1. Check `CORS_ORIGINS` in Render includes: `https://octopus-ai-secondbrain.github.io`
2. No trailing slash!
3. Include the protocol (`https://`)
4. Save and wait for redeploy

### Issue: "Invalid Host Header"

**Solution:** Already fixed in latest deployment!
- The Dockerfile now includes proper host configuration
- Render domains (*.onrender.com) are whitelisted

### Issue: Render service is "sleeping"

**Free tier limitation:** Services spin down after 15 minutes of inactivity.

**Symptoms:**
- First request after idle takes 30-60 seconds
- Shows "Service Unavailable" briefly

**Solutions:**
1. **Upgrade to paid tier** ($7/mo) for always-on
2. **Use UptimeRobot** (free) to ping your service every 14 minutes
3. **Accept it** - good enough for personal projects

---

## Production Checklist

- [x] Code pushed to GitHub
- [ ] Render environment variables set (check above)
- [ ] Render service deployed successfully
- [ ] Backend health check passes
- [ ] GitHub Pages enabled
- [ ] Frontend deployed to Pages
- [ ] Can sign up new user
- [ ] Can create notes
- [ ] 3D visualization works
- [ ] CORS configured correctly

---

## Next Steps (Optional)

### Add PostgreSQL Database (Recommended)

**Why:** SQLite on Render's ephemeral filesystem can lose data on redeploys.

**How:**
1. In Render dashboard: **New** → **PostgreSQL**
2. Settings:
   - Name: `octopus-db`
   - Region: Same as your web service
   - Plan: Free (256MB) or paid
3. Click **Create Database**
4. Wait 2 minutes
5. Copy **Internal Database URL**
6. In your web service → **Environment** → Add:
   ```
   DATABASE_URL=<paste-the-internal-url>
   ```
7. Save (triggers redeploy)

### Add Persistent Storage for ChromaDB

1. In Render dashboard, go to your web service
2. Click **Disks** (left sidebar)
3. Click **Add Disk**
4. Settings:
   - Name: `vector-storage`
   - Mount Path: `/app/data/vector_db`
   - Size: 1 GB (free tier)
5. Click **Save**
6. Add environment variable:
   ```
   SECONDBRAIN_CHROMA_PATH=/app/data/vector_db
   ```
7. Redeploy

### Monitor Your Service

**Free monitoring options:**
- **UptimeRobot** (https://uptimerobot.com) - Uptime monitoring
- **Sentry** (https://sentry.io) - Error tracking
- **LogTail** (https://logtail.com) - Log aggregation

---

## URLs Summary

| Service | URL |
|---------|-----|
| **Backend API** | https://octopus-fa0y.onrender.com |
| **Backend Health** | https://octopus-fa0y.onrender.com/health |
| **Frontend** | https://octopus-ai-secondbrain.github.io/octopus |
| **GitHub Repo** | https://github.com/Octopus-AI-SecondBrain/octopus |
| **Render Dashboard** | https://dashboard.render.com |
| **GitHub Pages Settings** | https://github.com/Octopus-AI-SecondBrain/octopus/settings/pages |
| **GitHub Actions** | https://github.com/Octopus-AI-SecondBrain/octopus/actions |

---

**Your SecondBrain is almost live! 🧠✨**

Wait ~5 minutes for Render to redeploy with the latest changes, then test the health endpoint!
