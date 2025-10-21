# Landing Page

This folder contains the landing page for Second Brain, deployed via GitHub Pages.

## 📁 Structure

```
docs/
├── index.html              # Landing page HTML
├── demo.html               # Simple app demo
├── demo-app.html           # Complete app demo with notes
├── demo-neural-map.html    # 🆕 Full 3D/2D Neural Map demo
├── styles.css              # Complete styling with animations
├── script.js               # Form handling, modal, smooth scrolling
├── demo_notes.js           # Demo notes data
├── NEURAL_MAP_DEMO.md      # 🆕 Neural Map documentation
├── .nojekyll              # Bypass Jekyll processing (auto-generated)
├── 404.html               # Redirect to landing page (auto-generated)
└── app/                   # Built React app (auto-generated)
    └── index.html
    └── assets/
```

## 🎨 Features

### Hero Section
- Animated neural map visualization (pure CSS/SVG)
- Call-to-action buttons: 
  - **"🧠 Try 3D Neural Map"** (New!) - Full interactive visualization
  - **"📝 Try App Demo"** - Complete app experience
  - **"Join Beta"** - Sign up for early access
- Stats display: 10K+ notes, 500+ users, 99.9% uptime

### Demo Pages

#### 1. **demo-neural-map.html** 🆕 (New!)
Full-featured 3D/2D Neural Map visualization:
- Real 3D graphics with Three.js
- Interactive node manipulation
- Multiple layout algorithms (Force, Radial, Tree)
- Color-coded nodes by connection strength
- Smooth animations and transitions
- Detailed node information panels
- Live demo: [View Neural Map](https://octopus-ai-secondbrain.github.io/demo-neural-map.html)

#### 2. **demo-app.html**
Complete app interface with:
- Notes management (view, search, filter)
- Simplified neural map
- Dashboard with stats
- Tag cloud

#### 3. **demo.html**
Simple landing page demo

### Features Grid
6 feature cards highlighting:
1. AI-Powered Search
2. 3D Neural Map
3. Automatic Linking
4. Bulk Import
5. Smart Tags
6. Lightning Fast

### Demo Section
- Video placeholder (ready for YouTube embed)
- "Try Demo" button opens app in modal

### Beta Signup Form
- Email (required)
- Name (optional)
- Use Case (optional)
- Success message after submission
- Duplicate detection (localStorage)

### Footer
- Quick links (Features, Demo, Beta, GitHub)
- Social media (placeholder links)
- Tech stack showcase

## 🚀 Deployment

### Automatic (GitHub Actions)
1. Push to `main` branch
2. GitHub Actions builds frontend
3. Copies to `docs/app/`
4. Deploys `docs/` to GitHub Pages
5. Live at: `https://yourusername.github.io/secondbrain/`

### Manual (for testing)
```bash
# Build frontend
cd frontend
npm run build

# Copy to docs/app/
mkdir -p ../docs/app
cp -r dist/* ../docs/app/

# Test locally
cd ../docs
python3 -m http.server 8000
# Open: http://localhost:8000
```

## 🔧 Configuration

### Update Demo URL
Edit `index.html` line 186:
```html
<a href="https://your-username.github.io/secondbrain/app/">
```

### Configure Beta Form

#### Option 1: Formspree (Recommended)
1. Sign up at [formspree.io](https://formspree.io)
2. Create form, get ID (e.g., `xvgopqrs`)
3. Update `script.js` line 42:
   ```javascript
   const response = await fetch('https://formspree.io/f/xvgopqrs', {
   ```

#### Option 2: Backend Endpoint
1. Create `/api/beta-signup` endpoint in FastAPI
2. Update `script.js` line 49 with backend URL

#### Option 3: LocalStorage (Current)
- Stores signups in browser localStorage
- Run `exportBetaSignups()` in console to download CSV
- Good for initial testing

### Add Demo Video
1. Upload video to YouTube
2. Get video ID from URL: `youtube.com/watch?v=VIDEO_ID`
3. Update `index.html` line 147:
   ```html
   <iframe src="https://www.youtube.com/embed/VIDEO_ID"></iframe>
   ```

### Customize Colors
Edit CSS custom properties in `styles.css`:
```css
:root {
  --primary: #F24D80;      /* Pink */
  --secondary: #A855F7;    /* Purple */
  --accent: #FF8F3C;       /* Orange */
  --text-dark: #1F2937;    /* Dark gray */
  --text-light: #6B7280;   /* Medium gray */
  --bg-light: #F9FAFB;     /* Off-white */
}
```

## 📊 Analytics

### Add Google Analytics
Add to `index.html` before `</head>`:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### Track Events
Beta form submission already tracks via `gtag('event', 'beta_signup')` (if GA is configured).

## 🐛 Debugging

### View Beta Signups
Open browser console on landing page:
```javascript
// View all signups
JSON.parse(localStorage.getItem('betaSignups'))

// Export as CSV
exportBetaSignups()
```

### Test Form Submission
1. Open landing page
2. Fill form with test data
3. Open browser console → Network tab
4. Submit form
5. Check for POST request and response

### Check Build
```bash
# Check if app directory exists
ls -la docs/app/

# Should show:
# index.html
# assets/
# vite.svg
```

## 🎨 Customization

### Update Hero Text
Edit `index.html` lines 40-45:
```html
<h1 class="hero-title">
  Your Second Brain,<br>
  <span class="gradient-text">Powered by AI</span>
</h1>
```

### Add More Features
Add feature card in `index.html` after line 110:
```html
<div class="feature-card">
  <div class="feature-icon">🎯</div>
  <h3>Feature Name</h3>
  <p>Feature description here.</p>
</div>
```

### Change Animation Speed
Edit `styles.css` animation durations:
```css
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}
/* Change animation-duration in .neural-map-container */
```

## 📱 Mobile Responsive

Landing page is fully responsive with breakpoints:
- Desktop: 1024px+
- Tablet: 768px - 1023px
- Mobile: < 768px

Test on different devices:
```bash
# Open in browser
# Right-click → Inspect → Toggle device toolbar
# Test on iPhone, iPad, Android
```

## 🔐 Security

### No Secrets in Frontend
- Never commit API keys to `docs/` folder
- Backend URL is public (expected)
- Form submissions go to Formspree or backend

### HTTPS Enforced
- GitHub Pages automatically uses HTTPS
- No mixed content warnings

## 📈 Performance

### Optimization
- All CSS in single file (styles.css)
- All JS in single file (script.js)
- Minimal external dependencies
- No heavy images (SVG animations only)

### Lighthouse Scores (Target)
- Performance: 95+
- Accessibility: 100
- Best Practices: 100
- SEO: 95+

## 🎉 Launch Checklist

Before going live:
- [ ] Update demo URL
- [ ] Configure beta form
- [ ] Add demo video (optional)
- [ ] Add Google Analytics (optional)
- [ ] Test on mobile devices
- [ ] Test form submission
- [ ] Check all links
- [ ] Verify 3D animation works
- [ ] Run Lighthouse audit
- [ ] Test with slow 3G connection

## 📞 Support

Issues? Check:
1. Browser console for errors
2. Network tab for failed requests
3. GitHub Actions logs for build errors
4. Render dashboard for backend errors

---

**Live URL**: https://yourusername.github.io/secondbrain/  
**Repository**: https://github.com/yourusername/secondbrain  
**Documentation**: See DEPLOYMENT_GUIDE.md
