# 🌐 Organization GitHub Pages Setup

## Your Site Will Be At:
**https://octopus-ai-secondbrain.github.io** (root domain, no `/octopus`)

---

## ✅ Step-by-Step Setup

### Step 1: Rename Repository (CRITICAL!)

For organization/user Pages, the repo MUST be named: `username.github.io`

1. Go to: **https://github.com/Octopus-AI-SecondBrain/Octopus-AI-SecondBrain/settings**
2. Scroll to **"Danger Zone"** section
3. Click **"Rename repository"**
4. Change name to: `Octopus-AI-SecondBrain.github.io`
5. Click **"I understand, rename this repository"**

GitHub will automatically redirect the old URL, but this is required for root domain hosting.

### Step 2: Update Local Repository Remote (Done ✅)

I've already updated your local git remote to:
```
https://github.com/Octopus-AI-SecondBrain/Octopus-AI-SecondBrain.github.io.git
```

### Step 3: Enable GitHub Pages

1. Go to: **https://github.com/Octopus-AI-SecondBrain/Octopus-AI-SecondBrain.github.io/settings/pages**
2. Under **"Build and deployment"**:
   - Source: **GitHub Actions**
3. Auto-saves!

### Step 4: Push Changes

```bash
cd /Users/noel.thomas/secondbrain
git add -A
git commit -m "Update for organization Pages deployment"
git push origin main
```

### Step 5: Wait & Visit

- Monitor: https://github.com/Octopus-AI-SecondBrain/Octopus-AI-SecondBrain.github.io/actions
- Wait for ✅ green checkmark (2-3 minutes)
- Visit: **https://octopus-ai-secondbrain.github.io**

---

## 🔧 What Changed

### Before (Project Page):
- URL: `https://octopus-ai-secondbrain.github.io/octopus`
- Repo: `octopus`
- Path-based routing

### After (Organization Page):
- URL: `https://octopus-ai-secondbrain.github.io`
- Repo: `Octopus-AI-SecondBrain.github.io`
- Root domain routing

---

## 🎯 Update Backend CORS

After renaming and deploying, update Render environment variable:

**Go to:** https://dashboard.render.com → Your Service → Environment

Update:
```bash
CORS_ORIGINS=https://octopus-ai-secondbrain.github.io
```

(Remove `/octopus` from the end)

Click **Save Changes** (triggers redeploy)

---

## 📊 Final URLs

| Service | URL |
|---------|-----|
| **Frontend** | https://octopus-ai-secondbrain.github.io |
| **Backend** | https://octopus-fa0y.onrender.com |
| **GitHub Repo** | https://github.com/Octopus-AI-SecondBrain/Octopus-AI-SecondBrain.github.io |
| **GitHub Pages Settings** | https://github.com/Octopus-AI-SecondBrain/Octopus-AI-SecondBrain.github.io/settings/pages |
| **Render Dashboard** | https://dashboard.render.com |

---

## ✅ Checklist

- [ ] Rename repo to `Octopus-AI-SecondBrain.github.io` on GitHub
- [ ] Local git remote updated (already done ✅)
- [ ] Frontend config updated (already done ✅)
- [ ] Push changes to GitHub
- [ ] Enable GitHub Pages (source: GitHub Actions)
- [ ] Wait for workflow to complete
- [ ] Update CORS_ORIGINS in Render to remove `/octopus`
- [ ] Visit https://octopus-ai-secondbrain.github.io
- [ ] Test signup and login

---

**Ready to push? Run the commands in Step 4!**
