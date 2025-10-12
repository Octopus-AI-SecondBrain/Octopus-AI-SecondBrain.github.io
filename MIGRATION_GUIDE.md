# SecondBrain Migration Guide (Legacy)

> **⚠️ OUTDATED**: This document is from an earlier version. For the latest migration guide, see:
> - **[MIGRATION_GUIDE_v2.md](MIGRATION_GUIDE_v2.md)** - Complete v2.0 migration guide with Alembic, cookie auth, and more

## Overview

This document describes an earlier security and configuration refactor. The current version (v2.0+) includes additional changes:
- Cookie-based authentication (replacing localStorage)
- Alembic database migrations (replacing direct schema creation)
- Thread-safe vector store
- Docker Compose support
- Enhanced security features

**For new deployments or upgrades, please refer to MIGRATION_GUIDE_v2.md**

---

## Legacy Information (Pre-v2.0)

### Database Initialization (Replaced by Alembic)

The old approach used direct schema creation:
```bash
# OLD METHOD - NO LONGER RECOMMENDED:
python -c "from backend.models.db import Base, engine; Base.metadata.create_all(bind=engine)"

# NEW METHOD - USE THIS INSTEAD:
alembic upgrade head
```
- Single limiter instance reduces overhead

**Rate Limits:**
- Signup: 5/minute
- Login: 10/minute  
- Other endpoints: 100/minute (default)

### 4. Security Hardening

**Changed:**
- SECRET_KEY validation: Raises `RuntimeError` if default key used in production
- Conditional HSTS: Only sets HSTS header when `ENVIRONMENT=production` AND `ENABLE_HTTPS=true`
- Password validation: Enforces strong passwords (min 8 chars, uppercase, lowercase, digit)
- Username validation: Min 3 chars, alphanumeric with hyphens/underscores/periods

**Production Requirements:**
```bash
# REQUIRED in production
SECRET_KEY=<generate-with-secrets.token_urlsafe(32)>
ENVIRONMENT=production

# When using HTTPS
ENABLE_HTTPS=true
```

**Generate Secure Key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Removed Hardcoded Credentials

**Changed:**
- `frontend/index.html` - Removed pre-filled demo credentials
- `scripts/demo/create_demo_notes.py` - Now requires env vars `DEMO_USERNAME` and `DEMO_PASSWORD`
- Removed token logging from frontend console

**Usage:**
```bash
# Run demo script
DEMO_USERNAME=myuser DEMO_PASSWORD=MyPass123 python scripts/demo/create_demo_notes.py
```

### 6. Test Updates

**Changed:**
- `tests/test_app.py` now imports from `backend.*` instead of `app.*`
- Tests respect `SECONDBRAIN_DB_URL` and `SECONDBRAIN_CHROMA_PATH` environment variables
- Database tables are created in test fixtures (since removed from main.py)

**Running Tests:**
```bash
# Install test dependencies
pip install pytest httpx

# Run tests
PYTHONPATH=$(pwd) pytest tests/ -v
```

### 7. Configuration Files

**Added:**
- `.gitignore` - Comprehensive Python/Node/Data exclusions
- `.env.example` - Updated with secure defaults and documentation

**Updated:**
- `README.md` - New configuration section and setup instructions
- `docs/api.md` - Updated API documentation with rate limits and validation rules
- `scripts/setup.sh` - Now mentions SECRET_KEY requirement
- `scripts/start.sh` - Database initialization added

## 🚀 Deployment Checklist

### For Production Deployment:

1. **Set Environment Variables:**
   ```bash
   ENVIRONMENT=production
   SECRET_KEY=<your-strong-secret-key-min-32-chars>
   ENABLE_HTTPS=true
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   CORS_ORIGINS=https://yourdomain.com
   ```

2. **Database:**
   - Use PostgreSQL in production (not SQLite)
   - Run migrations before starting:
     ```bash
     # Current: Manual table creation
     python -c "from backend.models.db import Base, engine; Base.metadata.create_all(bind=engine)"
     
     # Future: alembic upgrade head
     ```

3. **Security:**
   - Ensure SECRET_KEY is strong (32+ characters)
   - Set ENABLE_HTTPS=true when behind HTTPS
   - Configure CORS_ORIGINS for your domain
   - Review rate limits for your use case

4. **Monitoring:**
   - Set LOG_LEVEL=INFO or WARNING
   - Configure LOG_FILE for persistent logs
   - Enable JSON logging with ENABLE_JSON_LOGGING=true

### For Local Development:

1. **Quick Start:**
   ```bash
   ./scripts/setup.sh
   # Edit .env and set SECRET_KEY
   ./scripts/start.sh
   ```

2. **Environment Variables:**
   - Copy `.env.example` to `.env`
   - Generate a SECRET_KEY (required even for dev)
   - Default SQLite database works fine

## 📋 Breaking Changes

### None for existing deployments!

All changes are backward-compatible:
- Legacy `SECONDBRAIN_DB_URL` still works
- Legacy `SECONDBRAIN_CHROMA_PATH` still works
- Default configurations work for local development
- Existing databases continue to work

### API Changes:

- **Auth signup response**: No longer returns `message` or `user_id`, now returns `id` and `username`
- **Rate limiting**: Now returns proper JSON on 429 errors instead of HTML

## 🔧 Troubleshooting

### "RuntimeError: CRITICAL: Default SECRET_KEY detected in production"
**Solution:** Set a strong SECRET_KEY environment variable

### "Rate limit exceeded"
**Solution:** Wait 60 seconds or adjust rate limits in backend/config/config.py

### "Database tables not found"
**Solution:** Run database initialization via scripts/start.sh or manually

### Tests failing with import errors
**Solution:** Set PYTHONPATH: `export PYTHONPATH=$(pwd)`

## 📚 Additional Resources

- Configuration options: See `.env.example`
- API documentation: `docs/api.md`
- Development setup: `README.md`
- Security best practices: `docs/PROFESSIONAL_GUIDELINES.md`

## ✨ Next Steps

1. **Alembic Integration:** Set up proper database migrations
2. **CI/CD:** Add GitHub Actions for automated testing
3. **Docker:** Create Dockerfile for containerized deployments
4. **Monitoring:** Add Prometheus/Grafana metrics
5. **Backup:** Implement automated database backups

---

**Migration completed:** October 10, 2025
**Test status:** ✅ All tests passing
**Production ready:** ✅ Yes, with proper SECRET_KEY configuration
