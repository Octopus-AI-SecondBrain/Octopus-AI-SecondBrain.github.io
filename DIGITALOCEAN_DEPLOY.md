# 🚀 DigitalOcean Deployment Guide

Complete guide to deploy SecondBrain to DigitalOcean with your **$200 GitHub Student Pack credit**.

## ⚡ Quick Start (Automated)

The easiest way - use the deployment script:

```bash
cd /Users/noel.thomas/secondbrain
./deploy_digitalocean.sh
```

This script will:
- ✅ Install doctl CLI (if needed)
- ✅ Authenticate with DigitalOcean
- ✅ Generate secure SECRET_KEY
- ✅ Create PostgreSQL database with pgvector
- ✅ Deploy backend API
- ✅ Set up auto-deployments from GitHub
- ✅ Configure all environment variables

**Time:** 10-15 minutes total

---

## 📋 Manual Setup (Step-by-Step)

If you prefer manual setup or the script doesn't work:

### Step 1: Activate GitHub Student Pack ($200 Credit)

1. Go to https://education.github.com/pack
2. Verify student status (if not already done)
3. Find **DigitalOcean** in the pack
4. Click "Get access to DigitalOcean"
5. Copy your $200 credit code

### Step 2: Create DigitalOcean Account

1. Go to https://www.digitalocean.com/
2. Sign up with your student email
3. Go to **Billing** → **Promo Code**
4. Enter your $200 credit code
5. Verify you have $200 in credits

### Step 3: Install doctl CLI

**macOS:**
```bash
brew install doctl
```

**Linux:**
```bash
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.104.0/doctl-1.104.0-linux-amd64.tar.gz
tar xf doctl-1.104.0-linux-amd64.tar.gz
sudo mv doctl /usr/local/bin
```

**Windows:**
```powershell
# Download from: https://github.com/digitalocean/doctl/releases
# Extract and add to PATH
```

### Step 4: Authenticate doctl

```bash
# Get API token
# 1. Go to: https://cloud.digitalocean.com/account/api/tokens
# 2. Generate New Token (name: 'secondbrain-deploy')
# 3. Copy the token

# Authenticate
doctl auth init
# Paste your token when prompted
```

### Step 5: Update Configuration Files

**A. Update `.do/app.yaml`:**

```bash
# Replace these placeholders:
YOUR_GITHUB_USERNAME/YOUR_REPO_NAME  # e.g., johndoe/secondbrain
YOUR_GITHUB_USERNAME  # e.g., johndoe
```

**B. Generate SECRET_KEY:**

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Save this key - you'll need it
```

### Step 6: Deploy to DigitalOcean

```bash
# From project root
cd /Users/noel.thomas/secondbrain

# Create app
doctl apps create --spec .do/app.yaml

# Get your App ID (from output)
APP_ID="<your-app-id>"

# Set SECRET_KEY
doctl apps update $APP_ID --env "SECRET_KEY=<your-generated-secret-key>"

# Optional: Set OpenAI API Key
doctl apps update $APP_ID --env "OPENAI_API_KEY=<your-openai-key>"

# Deploy
doctl apps create-deployment $APP_ID --wait
```

### Step 7: Verify Deployment

```bash
# Get your app URL
doctl apps get $APP_ID --format LiveURL --no-header

# Test health endpoint
curl https://your-app-name.ondigitalocean.app/api/healthz

# Should return:
# {"status":"healthy","timestamp":"..."}
```

### Step 8: Configure Frontend

**A. Set GitHub Secret:**

1. Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`
2. Click **New repository secret**
3. Name: `VITE_API_URL`
4. Value: `https://your-app-name.ondigitalocean.app` (from Step 7)
5. Click **Add secret**

**B. Update Frontend (if needed):**

Your GitHub Actions workflow should already use `VITE_API_URL`. Verify in `.github/workflows/deploy-pages.yml`:

```yaml
- name: Build
  env:
    VITE_API_URL: ${{ secrets.VITE_API_URL }}
  run: |
    cd frontend
    npm ci
    npm run build
```

### Step 9: Deploy Frontend

```bash
# Push to trigger GitHub Actions
git add .
git commit -m "Deploy to DigitalOcean"
git push origin main

# GitHub Actions will auto-deploy frontend to GitHub Pages
```

---

## 🔧 Troubleshooting

### Issue: "Database connection failed"

**Solution:**
```bash
# Check database status
doctl databases list

# Get connection string
doctl databases connection $DB_ID --format ConnectionString

# Verify it matches DATABASE_URL in app config
doctl apps get $APP_ID
```

### Issue: "App build failed"

**Solution:**
```bash
# Check build logs
doctl apps logs $APP_ID --type BUILD

# Common fixes:
# 1. Ensure pyproject.toml is in /backend directory
# 2. Verify source_dir in app.yaml is correct
# 3. Check Python version compatibility
```

### Issue: "Migration failed"

**Solution:**
```bash
# Check migration logs
doctl apps logs $APP_ID --type DEPLOY

# Manually run migrations (if needed)
doctl apps run-command $APP_ID --component api -- alembic upgrade head
```

### Issue: "CORS errors in frontend"

**Solution:**
```bash
# Verify CORS_ORIGINS environment variable
doctl apps spec get $APP_ID

# Update CORS_ORIGINS
doctl apps update $APP_ID --env "CORS_ORIGINS=https://your-username.github.io,https://your-app.ondigitalocean.app"

# Redeploy
doctl apps create-deployment $APP_ID
```

### Issue: "502 Bad Gateway"

**Solution:**
```bash
# App might be starting up (cold start)
# Wait 30-60 seconds and try again

# Check app health
doctl apps get $APP_ID

# Check runtime logs
doctl apps logs $APP_ID --type RUN

# If issue persists, restart app
doctl apps create-deployment $APP_ID
```

---

## 📊 Monitoring & Logs

### View Logs

```bash
# Runtime logs (application output)
doctl apps logs $APP_ID --type RUN --follow

# Build logs
doctl apps logs $APP_ID --type BUILD

# Deploy logs (migrations)
doctl apps logs $APP_ID --type DEPLOY
```

### App Dashboard

View in browser:
```
https://cloud.digitalocean.com/apps/$APP_ID
```

### Database Console

```bash
# List databases
doctl databases list

# Connect to database
doctl databases connection $DB_ID --format URI

# Use with psql:
psql "<connection-uri>"
```

---

## 💰 Cost Breakdown

With **$200 GitHub Student Pack credit**:

### Monthly Costs:
- **App (Basic XXS)**: $5/month
- **PostgreSQL (Dev Database)**: $15/month
- **Bandwidth**: $0 (included)
- **Total**: $20/month

### Credit Duration:
- $200 ÷ $20/month = **10 months free**

### After Credit Runs Out:
- Upgrade to production database: $25/month
- Total: ~$30/month (or scale down/pause if needed)

---

## 🔒 Security Checklist

- ✅ SECRET_KEY is 32+ characters
- ✅ Database password is auto-generated
- ✅ HTTPS enabled (automatic)
- ✅ DEBUG=false in production
- ✅ CORS_ORIGINS is restrictive
- ✅ Environment variables stored as secrets
- ✅ GitHub tokens have minimal permissions

---

## 🚀 Advanced Configuration

### Enable Custom Domain

```bash
# Add domain to app
doctl apps update $APP_ID --domain your-domain.com

# Follow DNS instructions in dashboard
```

### Scale App

```bash
# Update instance size in app.yaml
# Change instance_size_slug to:
# - basic-xs: $10/month (512MB RAM)
# - basic-s: $20/month (1GB RAM)
# - basic-m: $40/month (2GB RAM)

# Apply changes
doctl apps update $APP_ID --spec .do/app.yaml
```

### Add Redis Cache (Optional)

```bash
# Create Redis cluster
doctl databases create redis-cache --engine redis --region nyc1 --size db-s-1vcpu-1gb

# Get Redis URL
doctl databases connection <redis-id> --format URI

# Add to app
doctl apps update $APP_ID --env "REDIS_URL=<redis-url>"
```

---

## 📱 Mobile/Desktop Apps (Future)

DigitalOcean App Platform supports:
- Static site hosting (for PWA)
- WebSocket support (for real-time features)
- CDN (for fast global access)

---

## 🆘 Need Help?

### Common Commands

```bash
# List all apps
doctl apps list

# Get app details
doctl apps get $APP_ID

# Update environment variable
doctl apps update $APP_ID --env "KEY=value"

# Restart app
doctl apps create-deployment $APP_ID

# Delete app (careful!)
doctl apps delete $APP_ID
```

### Resources

- **DigitalOcean Docs**: https://docs.digitalocean.com/products/app-platform/
- **doctl Reference**: https://docs.digitalocean.com/reference/doctl/
- **Community**: https://www.digitalocean.com/community/
- **Support**: https://cloud.digitalocean.com/support/tickets

### Contact

- GitHub Issues: https://github.com/Octopus-AI-SecondBrain/Octopus-AI-SecondBrain.github.io/issues
- Project Discussions: https://github.com/Octopus-AI-SecondBrain/Octopus-AI-SecondBrain.github.io/discussions

---

## ✅ Success Checklist

Your deployment is complete when:

- ✅ Backend returns 200 from `/api/healthz`
- ✅ API docs load at `/api/docs`
- ✅ Frontend loads from GitHub Pages
- ✅ Can sign up / login
- ✅ Can create and view notes
- ✅ Search functionality works
- ✅ Neural map loads
- ✅ No CORS errors in browser console
- ✅ HTTPS lock icon in browser

---

**Quick Deploy:** `./deploy_digitalocean.sh`

**Dashboard:** https://cloud.digitalocean.com/apps

**Your API will be at:** `https://secondbrain-api-xxxxx.ondigitalocean.app`
