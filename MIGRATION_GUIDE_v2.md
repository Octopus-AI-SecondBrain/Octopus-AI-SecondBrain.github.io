# SecondBrain Migration Guide

This document describes the major architectural changes introduced in the latest version and provides step-by-step migration instructions for existing deployments.

## Overview of Changes

### 1. Centralized Configuration (Pydantic Settings)
- **Before**: Configuration scattered across multiple files (`settings.py`, hardcoded values)
- **After**: Single `backend/config/config.py` using Pydantic BaseSettings
- **Benefits**: Type validation, environment variable management, clearer defaults

### 2. Cookie-Based Authentication
- **Before**: JWTs stored in localStorage (vulnerable to XSS)
- **After**: JWTs stored in secure, httpOnly cookies
- **Benefits**: Immune to XSS attacks, automatic CSRF protection with SameSite

### 3. Alembic Database Migrations
- **Before**: `Base.metadata.create_all()` and `ensure_sqlite_schema()` at startup
- **After**: Alembic-managed migrations
- **Benefits**: Version control for schema, safe production upgrades, rollback support

### 4. Thread-Safe Vector Store
- **Before**: Global variables without locking
- **After**: Singleton pattern with threading locks
- **Benefits**: Safe concurrent access, better error handling

### 5. Enhanced Security
- **Before**: Optional security checks, hardcoded defaults
- **After**: Enforced SECRET_KEY in production, conditional HSTS
- **Benefits**: Prevents insecure deployments, better production defaults

## Migration Steps

### For New Deployments

New deployments should follow the standard setup in README.md. No migration needed.

### For Existing Deployments

#### Step 1: Backup Your Data

```bash
# Backup database
cp data/database/secondbrain.db data/database/secondbrain.db.backup

# Backup vector store
cp -r data/vector_db data/vector_db.backup
```

#### Step 2: Update Dependencies

```bash
# Activate your virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Update Python packages
pip install -r requirements.txt

# This includes:
# - pydantic-settings==2.2.1
# - alembic==1.13.1
```

#### Step 3: Configure Environment

```bash
# Copy the new environment template
cp .env.example .env.new

# Transfer your existing settings from .env to .env.new
# CRITICAL: Set a strong SECRET_KEY if you haven't already
# Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"

# For production, also set:
# ENVIRONMENT=production
# ENABLE_HTTPS=true  # if using HTTPS

# Review and move
mv .env .env.old
mv .env.new .env
```

#### Step 4: Initialize Alembic

```bash
# The Alembic configuration is already set up, but you need to
# initialize the migration state for your existing database

# If you're using SQLite (development):
# The initial migration will detect existing tables
alembic stamp head

# If you're using PostgreSQL (production):
# Ensure your DATABASE_URL is set correctly
alembic stamp head
```

#### Step 5: Update Frontend Files

If you customized `index.html` or JavaScript files:

1. **Authentication Changes**: The frontend now uses cookies instead of localStorage
   - Remove any code that reads/writes `localStorage.getItem('sb_token')`
   - Remove Authorization headers from fetch calls
   - Add `credentials: 'include'` to all API requests

2. **Logout Changes**: Use the `/auth/logout` endpoint instead of just clearing localStorage

Example changes:
```javascript
// OLD CODE - REMOVE:
const token = localStorage.getItem('sb_token');
headers['Authorization'] = 'Bearer ' + token;

// NEW CODE - ADD:
const options = {
  credentials: 'include',  // Include cookies automatically
  // ... other options
};
```

#### Step 6: Restart Application

```bash
# Stop the old application (Ctrl+C or kill process)

# Start with the new startup script
./scripts/start.sh

# This will:
# 1. Run Alembic migrations (alembic upgrade head)
# 2. Start the FastAPI server
```

#### Step 7: Test Authentication

1. Open the application in your browser
2. If you have an existing session, you'll be logged out (cookie format changed)
3. Log in again - your credentials are still valid
4. Verify the new cookie is set (check browser DevTools → Application → Cookies)
5. Test that authentication persists across page reloads

#### Step 8: Verify Database

```bash
# Check that all tables exist and have the correct schema
# SQLite:
sqlite3 data/database/secondbrain.db ".schema"

# PostgreSQL:
psql -d secondbrain -c "\d+"

# Verify Alembic version table exists:
# SQLite:
sqlite3 data/database/secondbrain.db "SELECT * FROM alembic_version;"

# PostgreSQL:
psql -d secondbrain -c "SELECT * FROM alembic_version;"
```

## Breaking Changes

### 1. Authentication
- **Impact**: Users will be logged out and need to sign in again
- **Reason**: JWT storage moved from localStorage to httpOnly cookies
- **Action**: Communicate to users that they'll need to re-authenticate

### 2. Configuration
- **Impact**: Old environment variables may not work
- **Reason**: Centralized Pydantic settings with validation
- **Action**: Review `.env.example` and update your `.env` file
- **Legacy Support**: `SECONDBRAIN_DB_URL` and `SECONDBRAIN_CHROMA_PATH` still work

### 3. SECRET_KEY Enforcement
- **Impact**: Production deployments without a strong SECRET_KEY will fail to start
- **Reason**: Security hardening
- **Action**: Generate and set a strong SECRET_KEY (min 32 characters)

### 4. Database Initialization
- **Impact**: `Base.metadata.create_all()` and `ensure_sqlite_schema()` removed
- **Reason**: Replaced with Alembic migrations
- **Action**: Use `alembic upgrade head` instead

## Rollback Instructions

If you need to rollback to the previous version:

### Step 1: Restore Backups

```bash
# Restore database
cp data/database/secondbrain.db.backup data/database/secondbrain.db

# Restore vector store
rm -rf data/vector_db
cp -r data/vector_db.backup data/vector_db
```

### Step 2: Checkout Previous Version

```bash
# If using git
git checkout <previous-commit-hash>

# Reinstall old dependencies
pip install -r requirements.txt
```

### Step 3: Restore Old Environment

```bash
# Restore old .env
mv .env.old .env
```

### Step 4: Start Old Version

```bash
# Use the old startup method
export PYTHONPATH=$(pwd)
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Production Deployment Checklist

- [ ] SECRET_KEY set to a strong, unique value (min 32 characters)
- [ ] ENVIRONMENT=production
- [ ] ENABLE_HTTPS=true (if using HTTPS)
- [ ] DATABASE_URL points to PostgreSQL (not SQLite)
- [ ] Alembic migrations run successfully (`alembic upgrade head`)
- [ ] CORS_ORIGINS configured for your domain
- [ ] OPENAI_API_KEY set (optional but recommended)
- [ ] Backups configured for database and vector store
- [ ] Log aggregation configured (LOG_FILE or external service)
- [ ] Health check endpoint monitored (`/health`)
- [ ] Rate limiting configured appropriately
- [ ] SSL/TLS certificates valid and up-to-date

## Troubleshooting

### "SECRET_KEY is required when ENVIRONMENT=production"
**Solution**: Set a strong SECRET_KEY environment variable:
```bash
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

### "Alembic migration failed"
**Solution**: Check your database connection and run:
```bash
alembic current  # Check current version
alembic history  # View migration history
alembic upgrade head --sql  # Preview SQL without executing
```

### "Authentication not working"
**Solution**: 
1. Clear browser cookies and cache
2. Check CORS_ORIGINS includes your frontend URL
3. Verify backend logs for authentication errors
4. Ensure cookies are enabled in browser

### "Database schema out of sync"
**Solution**:
```bash
# Option 1: Stamp current state (for existing deployments)
alembic stamp head

# Option 2: Create a new migration (if you made model changes)
alembic revision --autogenerate -m "Sync schema"
alembic upgrade head
```

## Support

For issues or questions:
1. Check the [README.md](README.md) for setup instructions
2. Review [docs/development.md](docs/development.md) for development guidelines
3. Open an issue on GitHub with:
   - Error messages
   - Environment (development/production)
   - Database type (SQLite/PostgreSQL)
   - Steps to reproduce

## Version Compatibility

This migration guide is for upgrading to:
- **Version**: 2.0.0+
- **Date**: 2025-10-12
- **Breaking Changes**: Yes (authentication, configuration, database management)

Previous versions (< 2.0.0) used localStorage for auth and direct schema creation.
