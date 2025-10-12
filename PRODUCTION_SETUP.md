# 🚀 Production Setup Guide - PostgreSQL + Clean Database

## Step 1: Add PostgreSQL Database on Render

### Create Database (5 minutes)

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Click **New +** (top right)
   - Select **PostgreSQL**

2. **Configure Database**
   ```
   Name: octopus-db
   Database: octopus
   User: octopus_user (auto-generated)
   Region: Oregon (USA) - SAME as your web service
   PostgreSQL Version: 15 (latest)
   ```

3. **Choose Plan**
   - **Free (256 MB)** - Good for testing, expires after 90 days
   - **Starter ($7/mo, 1 GB)** - Recommended for production
   - **Standard ($20/mo, 10 GB)** - For heavy use

4. **Create Database**
   - Click **Create Database**
   - Wait ~2 minutes for provisioning
   - Status will change to "Available"

### Get Connection Details

5. **Copy Database URL**
   - Click on your new `octopus-db` database
   - Scroll down to **Connections**
   - Copy the **Internal Database URL**
   - Format: `postgresql://user:password@internal-host/octopus`
   
   **IMPORTANT:** Use "Internal" not "External" - web service needs internal URL!

---

## Step 2: Connect Backend to PostgreSQL

### Update Environment Variables

1. **Go to Web Service**
   - Dashboard → Your `octopus-api` web service
   - Click **Environment** (left sidebar)

2. **Add/Update DATABASE_URL**
   - Click **Add Environment Variable**
   - Key: `DATABASE_URL`
   - Value: Paste the Internal Database URL
   - Example: `postgresql://octopus_user:long_password_here@dpg-xxxxx-a.oregon-postgres.render.com/octopus`

3. **Review All Variables**
   
   Make sure you have ALL of these:
   ```bash
   DATABASE_URL=postgresql://user:pass@internal-host/octopus
   SECRET_KEY=<your-32-char-secret-key>
   ENVIRONMENT=production
   ENABLE_HTTPS=true
   CORS_ORIGINS=https://octopus-ai-secondbrain.github.io
   LOG_LEVEL=INFO
   ```

4. **Save Changes**
   - Click **Save Changes**
   - Render will automatically redeploy (~5 minutes)
   - Watch the **Logs** tab for deployment progress

### Verify Deployment

5. **Check Logs**
   - Look for: `==> Your service is live 🎉`
   - Check for database connection success
   - No errors about PostgreSQL connection

6. **Test Health Endpoint**
   ```bash
   curl https://octopus-fa0y.onrender.com/health
   ```
   
   Should return:
   ```json
   {"status":"healthy","version":"0.1.0","environment":"production"}
   ```

---

## Step 3: Production-Ready Database (Clean Slate)

### Option A: Fresh Start (Recommended)

Your new PostgreSQL database is **empty** - perfect for production!

**No action needed** - just:
1. Visit your site: https://octopus-ai-secondbrain.github.io
2. Create your first production account
3. Start using!

### Option B: Remove Test Users (If SQLite data exists)

If you had test data in SQLite and want to clean it:

**Skip this** - PostgreSQL is fresh, no test users exist yet!

---

## Step 4: Add Admin-Only Features (Hide Demo Mode)

Let me create an admin system so only you can access certain features.

### Update User Model with Admin Flag

Add this to your code to mark your account as admin:

```python
# backend/models/user.py
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # NEW
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    notes: Mapped[list["Note"]] = relationship("Note", back_populates="owner")
```

### Hide Debug/Test Features

Update frontend to hide development tools:

```javascript
// frontend/assets/js/config.js
const CONFIG = {
    BACKEND_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : 'https://octopus-fa0y.onrender.com',
    
    // Hide debug features in production
    IS_PRODUCTION: window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1',
    
    FEATURES: {
        DEBUG_LOGGING: false,  // Always off in production
        CONNECTION_TESTING: false,  // Hide connection tests
        SHOW_BACKEND_CONFIG: false,  // Hide backend URL settings
        ENHANCED_3D: true
    }
};
```

### Remove Test/Debug HTML Files

These files are for development only - remove from production:

```bash
# Delete test files
rm frontend/auth-test.html
rm frontend/clear-test.html
rm frontend/debug.html
rm frontend/manual-test.html
```

### Clean Frontend

Keep only production files:
```
frontend/
├── index.html          ← Main app
├── auth.html           ← Login/signup
├── auth.css           ← Styling
├── assets/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── app.js
│       ├── auth.js
│       └── config.js
```

---

## Step 5: Security Hardening

### Disable API Documentation in Production

Your code already does this! Check `backend/main.py`:

```python
app = FastAPI(
    title=f"{settings.app_name} - {settings.environment.title()}",
    version=settings.app_version,
    description="Neural knowledge mapping with 3D visualization",
    docs_url="/docs" if not settings.is_production() else None,  # ✅ Disabled
    redoc_url="/redoc" if not settings.is_production() else None,  # ✅ Disabled
    debug=settings.debug
)
```

When `ENVIRONMENT=production`, these URLs return 404:
- ❌ `/docs` (Swagger UI)
- ❌ `/redoc` (ReDoc)

### Verify Security Settings

Make sure these are set in Render:

```bash
ENVIRONMENT=production          # Disables debug mode & API docs
ENABLE_HTTPS=true              # Enables HSTS headers
SECRET_KEY=<32+ chars>         # Secure JWT signing
CORS_ORIGINS=<your-pages-url>  # Only allow your frontend
LOG_LEVEL=INFO                 # Don't expose debug logs
```

---

## Step 6: First Production User (You!)

### Create Your Admin Account

1. **Visit:** https://octopus-ai-secondbrain.github.io/auth.html
2. **Sign Up:**
   - Username: `your-username` (remember this!)
   - Password: Strong password (8+ chars, uppercase, lowercase, digit)
   - Example: `MySecure2024Pass!`
3. **Click Create Account**

### Mark Yourself as Admin (Optional)

If you added the `is_admin` field, mark your account:

```bash
# Connect to PostgreSQL (from Render dashboard → Database → Connect)
# Or use psql command from your terminal

psql <paste-external-database-url>

# Mark your user as admin
UPDATE users SET is_admin = true WHERE username = 'your-username';

# Verify
SELECT id, username, is_admin FROM users;

# Exit
\q
```

---

## Step 7: Clean Up Development Files

### Remove Test Files from Repository

```bash
cd /Users/noel.thomas/secondbrain

# Remove test HTML files from frontend
git rm frontend/auth-test.html
git rm frontend/clear-test.html
git rm frontend/debug.html
git rm frontend/manual-test.html
git rm frontend/frontend.log

# Remove backend test files (optional - these aren't deployed)
git rm -r backend/map-frontend

# Commit
git commit -m "Remove test/debug files for production"
git push
```

### Update .gitignore

Make sure these are ignored:

```
# Add to .gitignore
frontend.log
*.log
auth-test.html
debug.html
clear-test.html
manual-test.html
```

---

## Step 8: Verify Production Setup

### Checklist

- [ ] PostgreSQL database created on Render
- [ ] DATABASE_URL set in web service environment
- [ ] Service redeployed successfully (check logs)
- [ ] Health endpoint works
- [ ] Can create account at /auth.html
- [ ] Can login and create notes
- [ ] API docs disabled (/docs returns 404)
- [ ] Test files removed from frontend
- [ ] CORS only allows your GitHub Pages domain
- [ ] Strong SECRET_KEY set (32+ chars)

### Test Production Site

```bash
# 1. Health check
curl https://octopus-fa0y.onrender.com/health

# 2. API docs should be disabled
curl https://octopus-fa0y.onrender.com/docs
# Should return: {"detail":"Not Found"}

# 3. Root endpoint
curl https://octopus-fa0y.onrender.com/
# Should return: {"name":"SecondBrain API","version":"0.1.0",...}

# 4. Frontend loads
# Visit: https://octopus-ai-secondbrain.github.io
# Should show clean interface with no test/debug elements
```

---

## Step 9: Monitoring & Maintenance

### Setup UptimeRobot (Keep Render Awake)

1. Go to https://uptimerobot.com
2. Sign up (free)
3. Add monitor:
   - URL: `https://octopus-fa0y.onrender.com/health`
   - Interval: 5 minutes
4. Get email alerts for downtime

### Enable Render Notifications

1. Render Dashboard → Account Settings
2. Enable email notifications for:
   - Deploy failures
   - Service crashes
   - Database issues

### Backup Strategy

**Render Starter Plan ($7/mo) includes:**
- Daily automatic backups
- 7-day retention
- One-click restore

**Manual backup (free tier):**
```bash
# From Render dashboard → Database → Connect
# Copy External Database URL

pg_dump <external-url> > backup_$(date +%Y%m%d).sql
```

Schedule weekly via cron or GitHub Actions.

---

## Production URLs

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | https://octopus-ai-secondbrain.github.io | ✅ |
| **Backend** | https://octopus-fa0y.onrender.com | ✅ |
| **Database** | Render PostgreSQL (internal) | 🔒 |
| **Health** | https://octopus-fa0y.onrender.com/health | ✅ |
| **Docs** | ❌ Disabled in production | 🔒 |

---

## Cost Breakdown

### Current Setup (Recommended):

- **GitHub Pages:** Free (unlimited)
- **Render Web Service:** $7/month (Starter)
- **PostgreSQL:** $7/month (Starter, 1GB)
- **Total:** **$14/month**

### Budget Option:

- **GitHub Pages:** Free
- **Render Web Service:** Free (sleeps after 15min)
- **PostgreSQL:** Free (256MB, expires after 90 days)
- **UptimeRobot:** Free (keeps backend awake)
- **Total:** **$0/month** (with some limitations)

---

## Next Steps

1. ✅ **Add PostgreSQL** on Render (Step 1)
2. ✅ **Set DATABASE_URL** environment variable (Step 2)
3. ✅ **Wait for redeploy** (~5 minutes)
4. ✅ **Create your account** (Step 6)
5. ✅ **Remove test files** (Step 7)
6. ✅ **Verify everything works** (Step 8)
7. ✅ **Setup monitoring** (Step 9)

---

**Ready to start? Follow Step 1 above!** 🚀
