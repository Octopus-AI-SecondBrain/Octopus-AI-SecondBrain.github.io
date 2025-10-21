# 🚀 Quick GitHub Pages Setup

## Option 1: Serve Directly from docs/ (EASIEST - No build needed!)

This is the fastest way to get your landing page live:

### Steps:
1. Go to: https://github.com/Octopus-AI-SecondBrain/Octopus-AI-SecondBrain.github.io/settings/pages

2. Under "Build and deployment":
   - **Source**: Deploy from a branch
   - **Branch**: `main`
   - **Folder**: `/docs`
   - Click **Save**

3. Wait 1-2 minutes

4. Your landing page will be live at:
   - **https://octopus-ai-secondbrain.github.io/**

### What happens:
- GitHub serves `docs/index.html` directly
- No build process needed
- Landing page is live instantly!
- React app won't be included (needs build step)

### This gives you:
✅ Landing page with hero section  
✅ Animated neural map  
✅ Beta signup button (links to Google Form)  
✅ Features showcase  
✅ Footer  

---

## Option 2: Use GitHub Actions (Full App + Landing)

If you want BOTH the landing page AND the built React app:

### Steps:
1. Go to: https://github.com/Octopus-AI-SecondBrain/Octopus-AI-SecondBrain.github.io/settings/pages

2. Under "Build and deployment":
   - **Source**: Deploy from a branch
   - **Branch**: `gh-pages` (will be created by Actions)
   - **Folder**: `/ (root)`
   - Click **Save**

3. Go to Actions tab: https://github.com/Octopus-AI-SecondBrain/Octopus-AI-SecondBrain.github.io/actions

4. Click "Deploy to GitHub Pages" workflow

5. Click "Run workflow" → Run workflow

6. Wait 5-7 minutes for build

7. Landing page + app will be live at:
   - Landing: **https://octopus-ai-secondbrain.github.io/**
   - App: **https://octopus-ai-secondbrain.github.io/app/**

### This gives you:
✅ Landing page  
✅ Full React app (built and deployed)  
✅ Both accessible from same domain  

---

## 🎯 My Recommendation: Option 1 First

**Do Option 1 NOW** to get your landing page live in 2 minutes:
- Go to Settings → Pages
- Source: Deploy from branch
- Branch: `main`, Folder: `/docs`
- Save

Then later, when you're ready to deploy the full app:
- Switch to Option 2
- Run GitHub Actions workflow
- Get both landing + app

---

## 🔍 How to Check What's Live

After enabling GitHub Pages, visit:
- https://octopus-ai-secondbrain.github.io/

You should see:
- Hero section with "Your Second Brain, Powered by AI"
- Animated neural map visualization
- Features cards
- "Join Beta" button (opens Google Form)

---

## 🐛 Troubleshooting

### "404 - Site not found"
- Wait 2-3 minutes after enabling Pages
- Check that `docs/index.html` exists in your repo
- Refresh the page

### "Settings → Pages shows no options"
- Make sure repository is public
- Or enable Pages for private repos in settings

### "Landing page shows but looks broken"
- Check that `docs/styles.css` and `docs/script.js` exist
- Clear browser cache and refresh

### "Want to see build logs"
- Go to Actions tab
- Click on latest workflow run
- Expand steps to see details

---

## ✅ Quick Start Command

```bash
# Just tell me when you've enabled Pages and I'll verify it's working!
curl -I https://octopus-ai-secondbrain.github.io/
```

---

**Ready to enable GitHub Pages? Choose Option 1 for instant landing page! 🚀**
