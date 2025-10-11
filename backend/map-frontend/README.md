# Backend Test Files

⚠️ **These files are for local backend testing only!**

## Purpose

These HTML files are used for:
- Testing backend API endpoints directly
- Debugging authentication flows
- Manual testing during development

## Production Frontend

**The actual production frontend is in:** `frontend/` directory

**Live site:** https://octopus-ai-secondbrain.github.io

## Files in This Directory

- `auth.html` - Authentication testing
- `auth-test.html` - Auth flow tests
- `index.html` - Basic map interface test
- `debug.html` - Debug tools
- `manual-test.html` - Manual API testing
- `clear-test.html` - Database clearing tests
- `config.js` - Backend test configuration (now supports production URL)

## Usage

### Local Testing
1. Run backend: `python -m uvicorn backend.main:app --reload`
2. Open any HTML file directly in browser
3. Files auto-detect localhost vs production

### Production Testing (Not Recommended)
These files can technically connect to production backend, but:
- Use the official frontend instead: https://octopus-ai-secondbrain.github.io
- These are debugging tools, not production-ready

## Configuration

The `config.js` now auto-detects:
- **Localhost:** Uses `http://localhost:8000`
- **Production:** Uses `https://octopus-fa0y.onrender.com`

## Should I Delete These?

**No** - Keep them for local development and testing. They're useful when:
- Testing new API endpoints
- Debugging backend issues
- Verifying authentication flows
- Quick manual tests without running the full frontend

**They're not deployed to GitHub Pages** - only the `frontend/` folder is deployed.
