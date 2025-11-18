# 🚀 Google Cloud Run Deployment Guide

Complete guide to deploy SecondBrain to Google Cloud Run with **$300 free credit** for new accounts.

## ⚡ Quick Start (Automated)

The easiest way - use the deployment script:

```bash
cd /Users/noel.thomas/secondbrain
chmod +x deploy_gcloud.sh
./deploy_gcloud.sh
```

This script will:
- ✅ Install/authenticate gcloud CLI
- ✅ Enable required APIs
- ✅ Create Cloud SQL PostgreSQL (optional)
- ✅ Build Docker image
- ✅ Deploy to Cloud Run
- ✅ Run database migrations
- ✅ Configure all environment variables

**Time:** 15-20 minutes total

---

## 💰 Cost Breakdown

### With $300 Free Credit (New Accounts):

**Monthly Costs:**
- **Cloud Run**: $0-5/month (2M requests free, then $0.40/M requests)
- **Cloud SQL (db-f1-micro)**: ~$7/month
- **Cloud Build**: $0 (120 build-minutes/day free)
- **Container Registry**: $0 (first 500MB free)
- **Total**: ~$7-12/month

### Credit Duration:
- $300 ÷ $10/month = **30 months free** (or until credit expires)

### Free Tier (Always Free):
- Cloud Run: 2M requests/month
- Cloud Build: 120 build-minutes/day
- Outbound data: 1GB/month

---

## 📋 Manual Setup (Step-by-Step)

If you prefer manual setup:

### Step 1: Create Google Cloud Account

1. Go to https://cloud.google.com/
2. Sign up with your email
3. **$300 credit automatically applied** for new accounts
4. No charges until you upgrade to paid account

### Step 2: Install gcloud CLI

**macOS:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL  # Restart shell
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows:**
Download from: https://cloud.google.com/sdk/docs/install

### Step 3: Authenticate & Setup Project

```bash
# Login
gcloud auth login

# Create project
PROJECT_ID="secondbrain-$(date +%s)"
gcloud projects create $PROJECT_ID --name="SecondBrain"

# Set project
gcloud config set project $PROJECT_ID

# Enable billing (required)
# Visit: https://console.cloud.google.com/billing
```

### Step 4: Enable Required APIs

```bash
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    sql-component.googleapis.com \
    sqladmin.googleapis.com \
    compute.googleapis.com
```

### Step 5: Setup Database

**Option A: Cloud SQL (Recommended)**

```bash
# Create PostgreSQL instance
gcloud sql instances create secondbrain-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1

# Create database
gcloud sql databases create secondbrain \
    --instance=secondbrain-db

# Set password
gcloud sql users set-password postgres \
    --instance=secondbrain-db \
    --password=YOUR_SECURE_PASSWORD

# Enable pgvector extension
gcloud sql connect secondbrain-db --user=postgres
# Then run: CREATE EXTENSION IF NOT EXISTS vector;
```

**Option B: External PostgreSQL**

Use free/cheap alternatives:
- **ElephantSQL**: https://www.elephantsql.com/ (Free 20MB)
- **Supabase**: https://supabase.com/ (Free 500MB)
- **Neon**: https://neon.tech/ (Free tier)

### Step 6: Build & Deploy

```bash
# From project root
cd /Users/noel.thomas/secondbrain

# Generate SECRET_KEY
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Build image
gcloud builds submit \
    --tag gcr.io/$PROJECT_ID/secondbrain-api \
    --file=infra/Dockerfile.cloudrun \
    .

# Get Cloud SQL connection (if using Cloud SQL)
CONNECTION_NAME=$(gcloud sql instances describe secondbrain-db \
    --format="value(connectionName)")

# Deploy to Cloud Run
gcloud run deploy secondbrain-api \
    --image gcr.io/$PROJECT_ID/secondbrain-api \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --add-cloudsql-instances=$CONNECTION_NAME \
    --set-env-vars="ENVIRONMENT=production,DEBUG=false,SECRET_KEY=$SECRET_KEY,CORS_ORIGINS=https://your-username.github.io,DATABASE_URL=postgresql://postgres:PASSWORD@localhost/secondbrain?host=/cloudsql/$CONNECTION_NAME"
```

### Step 7: Run Migrations

```bash
# Create migration job
gcloud run jobs create migrate-db \
    --image gcr.io/$PROJECT_ID/secondbrain-api \
    --region us-central1 \
    --set-env-vars=DATABASE_URL=<your-database-url> \
    --command=alembic \
    --args="upgrade,head"

# Execute migration
gcloud run jobs execute migrate-db --region us-central1 --wait
```

### Step 8: Get Service URL

```bash
# Get URL
SERVICE_URL=$(gcloud run services describe secondbrain-api \
    --platform managed \
    --region us-central1 \
    --format="value(status.url)")

echo "Backend URL: $SERVICE_URL"

# Test health
curl ${SERVICE_URL}/api/healthz
```

### Step 9: Configure Frontend

**A. Set GitHub Secret:**

1. Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`
2. Click **New repository secret**
3. Name: `VITE_API_URL`
4. Value: `<your-service-url>` (from Step 8)
5. Click **Add secret**

**B. Deploy Frontend:**

```bash
git add .
git commit -m "Configure for Google Cloud backend"
git push origin main
```

---

## 🔧 Troubleshooting

### Issue: "Permission denied" during gcloud auth

**Solution:**
```bash
# Re-authenticate
gcloud auth login --no-launch-browser

# Or use service account
gcloud auth activate-service-account --key-file=key.json
```

### Issue: "Billing not enabled"

**Solution:**
1. Visit: https://console.cloud.google.com/billing
2. Link your project to billing account
3. Apply $300 credit if not automatically applied

### Issue: "Cloud SQL connection failed"

**Solution:**
```bash
# Verify connection name
gcloud sql instances describe secondbrain-db \
    --format="value(connectionName)"

# Test connection
gcloud sql connect secondbrain-db --user=postgres

# Check Cloud Run service has correct connection
gcloud run services describe secondbrain-api --region us-central1
```

### Issue: "Container failed to start"

**Solution:**
```bash
# Check logs
gcloud run services logs read secondbrain-api \
    --region us-central1 \
    --limit 50

# Common fixes:
# 1. Ensure PORT=8080 in Dockerfile
# 2. Check DATABASE_URL is correct
# 3. Verify pgvector extension is enabled
```

### Issue: "pgvector extension missing"

**Solution:**
```bash
# Connect to database
gcloud sql connect secondbrain-db --user=postgres

# Enable extension
CREATE EXTENSION IF NOT EXISTS vector;

# Verify
\dx vector
```

### Issue: "CORS errors in frontend"

**Solution:**
```bash
# Update CORS_ORIGINS
gcloud run services update secondbrain-api \
    --region us-central1 \
    --update-env-vars CORS_ORIGINS=https://your-username.github.io,https://your-domain.com
```

### Issue: "502 Bad Gateway"

**Solution:**
```bash
# Check service health
gcloud run services describe secondbrain-api --region us-central1

# Check logs
gcloud run services logs read secondbrain-api --region us-central1

# Redeploy
gcloud run services update secondbrain-api \
    --region us-central1 \
    --image gcr.io/$PROJECT_ID/secondbrain-api
```

---

## 📊 Monitoring & Logs

### View Logs

```bash
# Runtime logs (live)
gcloud run services logs tail secondbrain-api \
    --region us-central1

# Recent logs
gcloud run services logs read secondbrain-api \
    --region us-central1 \
    --limit 100

# Filter errors
gcloud run services logs read secondbrain-api \
    --region us-central1 \
    --filter="severity>=ERROR"
```

### Cloud Console

View in browser:
```
https://console.cloud.google.com/run?project=$PROJECT_ID
```

### Database Monitoring

```bash
# List instances
gcloud sql instances list

# Describe instance
gcloud sql instances describe secondbrain-db

# Check operations
gcloud sql operations list --instance=secondbrain-db
```

---

## 🚀 Advanced Configuration

### Custom Domain

```bash
# Map domain
gcloud run services update secondbrain-api \
    --region us-central1 \
    --add-domain your-domain.com

# Follow DNS instructions in console
```

### Auto-scaling

```bash
# Update scaling
gcloud run services update secondbrain-api \
    --region us-central1 \
    --min-instances 0 \
    --max-instances 10 \
    --cpu 2 \
    --memory 2Gi
```

### CI/CD with GitHub Actions

Create `.github/workflows/deploy-cloudrun.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - id: auth
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - name: Deploy to Cloud Run
        uses: google-github-actions/deploy-cloudrun@v1
        with:
          service: secondbrain-api
          region: us-central1
          source: ./
          env_vars: |
            ENVIRONMENT=production
            SECRET_KEY=${{ secrets.SECRET_KEY }}
            CORS_ORIGINS=${{ secrets.CORS_ORIGINS }}
```

### Redis Cache (Optional)

```bash
# Create Memorystore Redis
gcloud redis instances create secondbrain-cache \
    --region=us-central1 \
    --tier=basic \
    --size=1

# Get Redis host
REDIS_HOST=$(gcloud redis instances describe secondbrain-cache \
    --region=us-central1 \
    --format="value(host)")

# Update Cloud Run
gcloud run services update secondbrain-api \
    --region us-central1 \
    --update-env-vars REDIS_URL=redis://$REDIS_HOST:6379
```

---

## 🔒 Security Checklist

- ✅ SECRET_KEY is 32+ characters
- ✅ Database password is strong
- ✅ HTTPS enabled (automatic on Cloud Run)
- ✅ DEBUG=false in production
- ✅ CORS_ORIGINS is restrictive
- ✅ Cloud SQL uses private IP (if needed)
- ✅ IAM permissions are minimal
- ✅ Container runs as non-root (if possible)

---

## 💵 Cost Optimization

### Reduce Cloud SQL Costs

```bash
# Use smallest tier
--tier=db-f1-micro  # $7/month

# Or use external free PostgreSQL:
# - ElephantSQL (free 20MB)
# - Supabase (free 500MB)
# - Neon (free tier)
```

### Reduce Cloud Run Costs

```bash
# Set min instances to 0 (cold starts OK)
--min-instances=0

# Use smaller memory
--memory=512Mi

# Reduce CPU
--cpu=1
```

### Free Alternative Stack

- **Backend**: Cloud Run (2M requests/month free)
- **Database**: ElephantSQL (free 20MB) or Supabase (free 500MB)
- **Frontend**: GitHub Pages (free)
- **Total**: $0/month

---

## 🆘 Need Help?

### Common Commands

```bash
# List services
gcloud run services list

# Describe service
gcloud run services describe secondbrain-api --region us-central1

# Update environment variable
gcloud run services update secondbrain-api \
    --region us-central1 \
    --update-env-vars KEY=value

# Redeploy
gcloud run deploy secondbrain-api \
    --image gcr.io/$PROJECT_ID/secondbrain-api \
    --region us-central1

# Delete service
gcloud run services delete secondbrain-api --region us-central1
```

### Resources

- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **Cloud SQL Docs**: https://cloud.google.com/sql/docs
- **gcloud Reference**: https://cloud.google.com/sdk/gcloud/reference
- **Community**: https://stackoverflow.com/questions/tagged/google-cloud-run
- **Support**: https://cloud.google.com/support

---

## ✅ Success Checklist

Your deployment is complete when:

- ✅ Backend returns 200 from `/api/healthz`
- ✅ API docs load at `/api/docs`
- ✅ Database connection works
- ✅ pgvector extension enabled
- ✅ Migrations completed successfully
- ✅ Frontend loads from GitHub Pages
- ✅ Can sign up / login
- ✅ Can create and view notes
- ✅ Search functionality works
- ✅ Neural map loads
- ✅ No CORS errors in browser console
- ✅ HTTPS lock icon in browser

---

**Quick Deploy:** `./deploy_gcloud.sh`

**Cloud Console:** https://console.cloud.google.com/run

**Your API will be at:** `https://secondbrain-api-xxxxx.run.app`
