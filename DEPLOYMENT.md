# Deployment Guide - GitHub Pages + Render

This guide walks you through deploying SecondBrain with the frontend on GitHub Pages and the backend on Render.

## Quick Deployment Steps

### 1. Push to GitHub

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Production-ready deployment"

# Create GitHub repo at https://github.com/new
# Then connect and push:
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git push -u origin main
```

### 2. Deploy Backend to Render.com

#### Option A: Free Tier (Good for testing)
1. Go to [render.com](https://render.com) and sign up
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `secondbrain-api` (or your choice)
   - **Environment**: `Docker`
   - **Branch**: `main`
   - **Plan**: Free (or paid for better performance)

5. Add Environment Variables:
   ```
   ENVIRONMENT=production
   SECRET_KEY=<generate-with-command-below>
   DATABASE_URL=<will-be-added-automatically>
   ENABLE_HTTPS=true
   CORS_ORIGINS=https://YOUR-USERNAME.github.io
   LOG_LEVEL=INFO
   ```

   Generate SECRET_KEY:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

6. Add PostgreSQL Database (Recommended for production):
   - In Render dashboard: **New** → **PostgreSQL**
   - Copy the **Internal Database URL**
   - Set as `DATABASE_URL` environment variable

7. For persistent ChromaDB storage:
   - Add a **Disk** in Render
   - Mount path: `/app/data/vector_db`
   - Set `SECONDBRAIN_CHROMA_PATH=/app/data/vector_db`

8. Click **Create Web Service**
9. Wait for deployment (first deploy takes ~5 minutes)
10. Note your backend URL: `https://secondbrain-api.onrender.com`

#### Option B: Railway.app (Alternative)
Similar to Render, supports Docker, provides PostgreSQL, and has a free tier.

### 3. Update Frontend Configuration

Edit `frontend/assets/js/config.js`:

```javascript
BACKEND_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000'
  : 'https://secondbrain-api.onrender.com', // YOUR ACTUAL BACKEND URL
```

Commit and push:
```bash
git add frontend/assets/js/config.js
git commit -m "Update backend URL for production"
git push
```

### 4. Enable GitHub Pages

1. Go to your GitHub repo → **Settings** → **Pages**
2. Under **Build and deployment**:
   - Source: **GitHub Actions**
3. The workflow (`.github/workflows/deploy-pages.yml`) will automatically deploy
4. Wait 2-3 minutes, then visit: `https://YOUR-USERNAME.github.io/YOUR-REPO`

If your repo name is `YOUR-USERNAME.github.io`:
- Your site will be at: `https://YOUR-USERNAME.github.io`
- Update workflow path if needed

### 5. Update Backend CORS

In Render (or your host), update the `CORS_ORIGINS` environment variable to include your GitHub Pages URL:

```
CORS_ORIGINS=https://YOUR-USERNAME.github.io,https://YOUR-USERNAME.github.io/YOUR-REPO
```

Restart the backend service after updating.

### 6. Test Your Deployment

1. Visit your GitHub Pages URL
2. Create an account (use a strong password!)
3. Create notes and test the 3D visualization
4. Check browser DevTools → Network to ensure API calls work

## Troubleshooting

### CORS Errors
**Problem**: `Access-Control-Allow-Origin` errors in browser console

**Solution**:
- Verify `CORS_ORIGINS` in backend includes exact GitHub Pages URL
- No trailing slashes in URLs
- Restart backend after changing env vars

### Backend Not Responding
**Problem**: Frontend can't connect to backend

**Solution**:
- Check backend URL in `config.js` matches your Render URL
- Verify Render service is running (check logs)
- Test backend directly: `https://your-backend.onrender.com/health`

### Authentication Issues
**Problem**: Can't sign up or login

**Solution**:
- Check `SECRET_KEY` is set in backend environment
- SECRET_KEY must be 32+ characters
- Check backend logs in Render dashboard

### Database Connection Issues
**Problem**: Backend crashes or can't store data

**Solution**:
- For SQLite: Ensure `/app/data` directory is writable
- For PostgreSQL: Verify `DATABASE_URL` is set correctly
- Check Render logs for database connection errors

### GitHub Pages 404
**Problem**: GitHub Pages shows 404

**Solution**:
- Wait 2-3 minutes after first deployment
- Check GitHub Actions tab for build status
- Verify `frontend` folder exists and has `index.html`

## Architecture

```
┌─────────────────────────────────────┐
│   GitHub Pages (Static Frontend)   │
│   https://username.github.io        │
└─────────────┬───────────────────────┘
              │ API Calls
              ▼
┌─────────────────────────────────────┐
│   Render.com (FastAPI Backend)     │
│   https://app.onrender.com          │
│                                     │
│   ┌──────────────┐ ┌─────────────┐│
│   │ PostgreSQL   │ │  ChromaDB   ││
│   │   Database   │ │ (Disk Mount)││
│   └──────────────┘ └─────────────┘│
└─────────────────────────────────────┘
```

## Cost Breakdown

### Free Tier (Testing)
- **GitHub Pages**: Free (unlimited)
- **Render**: Free tier with limitations
  - Backend sleeps after 15 min inactivity
  - 750 hours/month free
  - Limited resources

**Total: $0/month**

### Production Tier (Recommended)
- **GitHub Pages**: Free
- **Render Starter**: $7/month
  - Always on
  - 512MB RAM
  - Better performance
- **PostgreSQL**: $7/month (Starter)
- **Disk Storage**: $1/month per GB

**Total: ~$15/month**

## Custom Domain (Optional)

### For GitHub Pages:
1. Buy domain (e.g., Namecheap, Google Domains)
2. Add CNAME record: `www` → `YOUR-USERNAME.github.io`
3. In GitHub repo settings → Pages → Custom domain
4. Update `CORS_ORIGINS` in backend

### For Backend:
1. In Render: Settings → Custom Domain
2. Add domain: `api.yourdomain.com`
3. Update DNS: Add CNAME `api` → `your-app.onrender.com`
4. Update `config.js` with new backend URL

## Environment Variables Reference

### Required:
- `SECRET_KEY`: 32+ char secret (generate new)
- `ENVIRONMENT`: `production`
- `DATABASE_URL`: PostgreSQL connection string
- `CORS_ORIGINS`: Your GitHub Pages URL

### Optional:
- `ENABLE_HTTPS`: `true` (for HSTS headers)
- `LOG_LEVEL`: `INFO` or `WARNING`
- `OPENAI_API_KEY`: For enhanced embeddings
- `SECONDBRAIN_CHROMA_PATH`: ChromaDB storage path

## Local Testing Before Deploy

Test the Docker build locally:

```bash
# Build
docker build -t secondbrain-backend .

# Run
docker run -p 8000:8000 \
  -e SECRET_KEY="test-secret-key-min-32-chars-long" \
  -e ENVIRONMENT=development \
  secondbrain-backend

# Test
curl http://localhost:8000/health
```

## Monitoring

### Render Dashboard:
- View logs in real-time
- Monitor CPU/Memory usage
- Check deployment history

### Recommended Tools:
- **Uptime Monitoring**: UptimeRobot (free)
- **Error Tracking**: Sentry (free tier)
- **Analytics**: Plausible or Simple Analytics

## Backup Strategy

### Database:
- Render provides daily backups (paid plans)
- Manual: `pg_dump` via Render shell

### User Data:
- Notes and embeddings in PostgreSQL
- ChromaDB data on persistent disk
- Export via API periodically

## Next Steps

1. ✅ Deploy and test
2. 📊 Set up monitoring
3. 🔐 Enable 2FA on GitHub/Render
4. 📧 Configure email notifications for downtime
5. 📝 Document your custom domain setup
6. 🎨 Customize branding and theme

## Support

For issues:
- Check `MIGRATION_GUIDE.md` for common problems
- Review Render logs for backend errors
- Test backend health: `/health` and `/docs` endpoints
- Check GitHub Actions for deployment failures

---

**Your SecondBrain is now live! 🧠✨**
