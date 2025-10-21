# 🏗️ Deployment Architecture

Visual overview of how Second Brain is deployed to production.

## 🌐 Production Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        INTERNET                              │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌──────────────────┐          ┌──────────────────┐
│  GitHub Pages    │          │   Render.com     │
│  (Free Tier)     │          │   (Free Tier)    │
├──────────────────┤          ├──────────────────┤
│                  │          │                  │
│  Landing Page    │          │  FastAPI Backend │
│  index.html      │◄─────────┤  main.py         │
│  styles.css      │   CORS   │  routes/         │
│  script.js       │          │  models/         │
│                  │          │  services/       │
│  React App       │          │                  │
│  /app/           │          │  PostgreSQL DB   │
│  └─ index.html   │          │  (Free 1GB)      │
│     └─ assets/   │          │                  │
│                  │          │  ChromaDB        │
│                  │          │  (vector store)  │
└──────────────────┘          └──────────────────┘
         │                             │
         │                             │
         └─────────────┬───────────────┘
                       │
                       ▼
              ┌────────────────┐
              │   Formspree    │
              │  (Free Tier)   │
              ├────────────────┤
              │ Beta Signups   │
              │ (50/month)     │
              └────────────────┘
```

## 📊 Cost Breakdown

| Service | Plan | Cost | What You Get |
|---------|------|------|--------------|
| **GitHub Pages** | Free | $0/month | Unlimited bandwidth, 100GB storage |
| **Render.com Web** | Free | $0/month | 512 MB RAM, 750 hours/month |
| **Render.com PostgreSQL** | Free | $0/month | 1 GB storage, 90 day retention |
| **Formspree** | Free | $0/month | 50 submissions/month |
| **OpenAI API** | Pay-as-you-go | ~$0.10-0.20/month | Semantic search embeddings |
| **TOTAL** | - | **$0-0.20/month** 🎉 | Production-ready deployment |

### When to Upgrade (Future)

| Service | Paid Plan | Cost | Why Upgrade |
|---------|-----------|------|-------------|
| **Render.com Web** | Starter | $7/month | Always-on (no spin down), 512 MB RAM |
| **Render.com PostgreSQL** | Starter | $7/month | 10 GB storage, automated backups |
| **Formspree** | Gold | $10/month | 1,000 submissions, custom branding |
| **OpenAI API** | - | $5-20/month | More usage as user base grows |
| **TOTAL (scaled)** | - | **$30-45/month** | For 100-500+ users |

## 🔄 CI/CD Pipeline

```
┌────────────────────────────────────────────────────────────┐
│                    DEVELOPER WORKFLOW                       │
└────────────────────────────────────────────────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  git push main   │
                  └─────────┬────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │ GitHub Actions   │
                  │ .github/workflows│
                  │ /deploy.yml      │
                  └─────────┬────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Setup Node   │ │ Install Deps │ │ Build React  │
    │   (Node 20)  │ │  npm ci      │ │  npm build   │
    └──────────────┘ └──────────────┘ └──────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  Prepare docs/   │
                  │  - Keep landing  │
                  │  - Copy app/ dir │
                  │  - Add .nojekyll │
                  └─────────┬────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │ Deploy to GitHub │
                  │ Pages (gh-pages  │
                  │ branch)          │
                  └─────────┬────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │   LIVE! 🎉       │
                  │ yourusername.    │
                  │ github.io/       │
                  │ secondbrain/     │
                  └──────────────────┘
```

## 🏃 Request Flow

### Landing Page Visit
```
User → github.io/secondbrain/
  ↓
GitHub Pages CDN
  ↓
docs/index.html + styles.css + script.js
  ↓
Browser renders landing page
  ↓
User fills beta form
  ↓
POST to Formspree OR localStorage
  ↓
Success message
```

### App Usage
```
User → github.io/secondbrain/app/
  ↓
GitHub Pages CDN
  ↓
docs/app/index.html (React SPA)
  ↓
JavaScript loads, app initializes
  ↓
User creates account
  ↓
POST https://your-app.onrender.com/api/auth/signup
  ↓
Backend validates, creates user in PostgreSQL
  ↓
Returns JWT token
  ↓
User creates note
  ↓
POST https://your-app.onrender.com/api/notes
  ↓
Backend generates embedding (OpenAI)
  ↓
Stores in PostgreSQL + ChromaDB
  ↓
User searches notes
  ↓
POST https://your-app.onrender.com/api/search
  ↓
Backend queries ChromaDB vector similarity
  ↓
Returns ranked results
  ↓
User views neural map
  ↓
GET https://your-app.onrender.com/api/map
  ↓
Backend calculates similarity graph
  ↓
Returns nodes + edges JSON
  ↓
Frontend renders 3D visualization (Three.js)
```

## 📦 Deployment Package Contents

### Landing Page (`docs/`)
```
docs/
├── index.html          # Hero, features, beta form
├── styles.css          # Responsive styling + animations
├── script.js           # Form handling, modal, smooth scroll
├── README.md           # Documentation
├── .nojekyll           # Bypass Jekyll (auto-generated)
└── app/                # Built React app (auto-generated)
    ├── index.html
    └── assets/
        ├── index-xxx.js
        └── index-xxx.css
```

### GitHub Actions (`.github/workflows/`)
```
.github/workflows/
└── deploy.yml          # Auto-deployment on push to main
```

### Documentation
```
DEPLOYMENT_GUIDE.md           # Complete step-by-step guide
DEPLOYMENT_CHECKLIST.md       # Quick reference
DEPLOYMENT_COMPLETE.md        # Package overview
GITHUB_PAGES_DEPLOYMENT.md    # GitHub Pages details
docs/README.md                # Landing page docs
```

## 🔐 Security

### Frontend (GitHub Pages)
- ✅ HTTPS enforced automatically
- ✅ No secrets in code (all public)
- ✅ API URL is public (expected)
- ✅ No localStorage for sensitive data

### Backend (Render.com)
- ✅ HTTPS enforced automatically
- ✅ Environment variables for secrets
- ✅ CORS configured for GitHub Pages only
- ✅ JWT authentication
- ✅ Password hashing (bcrypt)
- ✅ SQL injection protection (SQLAlchemy ORM)

### Database (PostgreSQL)
- ✅ Private network (not internet-accessible)
- ✅ Encrypted at rest
- ✅ Automated backups (paid tier)
- ✅ SSL connections

## 🚀 Performance

### GitHub Pages
- **CDN**: Distributed globally via GitHub's CDN
- **Caching**: Aggressive caching for static assets
- **Latency**: <50ms for most users worldwide
- **Bandwidth**: Unlimited on free tier
- **Uptime**: 99.9%+ SLA

### Render.com (Free Tier)
- **Cold Start**: 30-60 seconds after 15 min inactivity
- **Warm Response**: <100ms for API calls
- **Memory**: 512 MB RAM (sufficient for 10-50 concurrent users)
- **Storage**: 1 GB database (sufficient for 10,000+ notes)
- **Uptime**: 99%+ (spins down when idle)

### Optimizations Applied
- ✅ React code splitting
- ✅ Lazy loading for 3D visualization
- ✅ Gzip compression on assets
- ✅ Minimal external dependencies
- ✅ Vector search indexing
- ✅ Database query optimization

## 📈 Scaling Strategy

### 0-100 Users (Free Tier)
- Stay on free tiers
- Monitor Render.com usage (750 hours/month)
- Use Formspree for beta signups (50/month)
- Cost: **$0-0.20/month**

### 100-1,000 Users (Paid Tier)
- Upgrade Render.com to Starter ($7/month)
  - Always-on (no cold starts)
  - Better performance
- Upgrade PostgreSQL to Starter ($7/month)
  - Automated backups
  - More storage
- Cost: **$15-20/month**

### 1,000+ Users (Custom)
- Consider dedicated hosting
- Implement caching (Redis)
- CDN for API responses (Cloudflare)
- Load balancing
- Cost: **$100-500/month**

## 🎯 Next Steps

1. ✅ Deploy backend to Render.com
2. ✅ Deploy frontend to GitHub Pages
3. ✅ Configure beta signup form
4. ✅ Test everything works
5. ✅ Share landing page URL
6. ✅ Collect beta signups
7. ✅ Monitor performance
8. ✅ Iterate based on feedback

---

**Ready to deploy?** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for step-by-step instructions!
