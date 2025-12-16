# Railway Quick Start (No Credit Card Required!)

## ✅ Railway - Best Free Option (No Credit Card)

**Why Railway:**
- ❌ **NO credit card required** for free tier
- ✅ **$5 free credit monthly** (more than enough)
- ✅ **Better memory management** than Render
- ✅ **Easy GitHub integration**
- ✅ **Can handle ViT model** (better resource allocation)

## Quick Setup (5 minutes)

### Step 1: Sign Up
1. Go to https://railway.app
2. Click "Start a New Project"
3. Sign up with **GitHub** (easiest)

### Step 2: Deploy Your App
1. Click "New Project"
2. Select **"Deploy from GitHub repo"**
3. Choose your `Emotion-detection` repository
4. Railway will auto-detect it's a Docker project

### Step 3: Configure Service
1. Railway will create a service automatically
2. If not, click **"+ New"** → **"Service"** → **"GitHub Repo"**
3. Select your repo
4. Railway will detect `backend/Dockerfile`

### Step 4: Set Environment Variables (if needed)
- Railway auto-detects PORT, but you can set:
  - `PORT=5000` (usually auto-set)

### Step 5: Deploy!
- Railway will automatically:
  - Build your Docker image
  - Deploy it
  - Give you a URL like: `https://your-app-name.up.railway.app`

### Step 6: Get Your URL
1. Click on your service
2. Go to **"Settings"** tab
3. Find **"Generate Domain"** or use the default one
4. Copy the URL (e.g., `https://emotion-detection-production.up.railway.app`)

### Step 7: Update Frontend
Edit `frontend/src/api/config.ts`:
```typescript
// Production default: Railway backend
return "https://your-railway-url.up.railway.app";
```

## Verify ViT Model is Loading

Check Railway logs:
1. Click on your service
2. Go to **"Deployments"** tab
3. Click on latest deployment
4. View logs

You should see:
```
[MODEL] Loading Vision Transformer: HardlyHumans/Facial-expression-detection
[MODEL] ✅ ViT model loaded successfully!
[APP] Model loaded: type=vit, version=hardlyhumans-vit-92.2%, labels=8
```

## Cost
- **Free tier**: $5 credit/month (plenty for this app)
- **No credit card**: Required for free tier
- **Auto-scales**: Only charges if you exceed free tier

## Troubleshooting

### If build fails:
- Check logs in Railway dashboard
- Make sure Dockerfile path is correct: `backend/Dockerfile`

### If model doesn't load:
- Check memory usage in Railway dashboard
- Railway free tier should handle it, but if not, you can upgrade

### If you need help:
- Railway has great docs: https://docs.railway.app
- Support: support@railway.app

## That's It!

Railway is the easiest, truly free (no credit card) option that can handle your ViT model! 🚀


