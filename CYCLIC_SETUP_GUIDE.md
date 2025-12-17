# 🚀 Complete Cyclic.sh Setup Guide

## What is Cyclic.sh?

Cyclic.sh is a serverless platform that automatically deploys your Python/Flask apps from GitHub. It's perfect for your emotion detection API because:
- ✅ 1GB RAM (enough for both models)
- ✅ Always-on (no sleep)
- ✅ Free tier (10k requests/month)
- ✅ No credit card required
- ✅ Easy GitHub integration

---

## Step-by-Step Setup

### Step 1: Sign Up for Cyclic.sh

1. **Go to**: https://cyclic.sh
2. **Click**: "Sign Up" or "Get Started"
3. **Choose**: "Sign up with GitHub" (easiest)
4. **Authorize**: Allow Cyclic to access your GitHub repos
5. **Complete**: Basic profile setup

**Time**: 2 minutes

---

### Step 2: Create New App

1. **In Cyclic Dashboard**: Click "New App" or "+ Create App"
2. **Connect Repository**:
   - Select your GitHub account
   - Find and select: `Emotion-detection`
   - Click "Connect" or "Select"

3. **Configure App**:
   - **App Name**: `emotion-detection-api` (or your choice)
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (Cyclic will auto-detect)
   - **Framework**: Cyclic will auto-detect "Python/Flask"

4. **Click**: "Create App" or "Deploy"

**Time**: 1 minute

---

### Step 3: Configure Environment Variables

After the app is created:

1. **Go to**: Your app dashboard in Cyclic
2. **Click**: "Environment Variables" or "Env" tab
3. **Add Variables**:
   - Click "Add Variable"
   - **Name**: `ASRIPA_MODEL_ID`
   - **Value**: `HimAJ/asripa-emotion-detection`
   - Click "Save"

4. **Optional Variables** (Cyclic usually auto-sets these):
   - `PORT=5000` (usually auto-set)
   - `PYTHONUNBUFFERED=1` (for better logs)

**Time**: 1 minute

---

### Step 4: Configure Build Settings (If Needed)

Cyclic usually auto-detects, but check:

1. **Go to**: "Settings" or "Build" tab
2. **Verify**:
   - **Build Command**: Usually auto-detected (leave empty or `pip install -r requirements.txt`)
   - **Start Command**: Usually auto-detected (should be `gunicorn main:app` or similar)

3. **Root Directory** (if needed):
   - If your backend is in `backend/` folder, set root directory to `backend`
   - Otherwise, leave empty

**Time**: 1 minute

---

### Step 5: Deploy!

1. **Cyclic will automatically**:
   - Clone your repo
   - Install dependencies from `requirements.txt`
   - Build your app
   - Deploy it

2. **Watch the logs**:
   - You'll see build progress
   - Wait for "Deployment successful"

3. **Get your URL**:
   - Cyclic will give you: `https://your-app-name.cyclic.app`
   - Copy this URL!

**Time**: 3-5 minutes (first deploy)

---

### Step 6: Test Your Deployment

1. **Test Health Endpoint**:
   ```
   https://your-app-name.cyclic.app/health
   ```
   Should return JSON with model info

2. **Test Main Endpoint**:
   ```
   https://your-app-name.cyclic.app/
   ```
   Should return: `{"status": "ok", "message": "Flask backend running"}`

3. **Check Logs**:
   - In Cyclic dashboard, go to "Logs" tab
   - You should see model loading messages

---

### Step 7: Update Frontend

1. **Go to Vercel Dashboard**:
   - Your frontend project
   - Settings → Environment Variables

2. **Update `VITE_API_URL`**:
   - **Old**: `https://emotion-detection-1-8avi.onrender.com`
   - **New**: `https://your-app-name.cyclic.app`
   - Save and redeploy

3. **Or Update Code**:
   - Edit `frontend/src/api/config.ts`
   - Change production URL to your Cyclic URL
   - Push to GitHub (Vercel will auto-deploy)

---

## 🎯 What Happens During Deployment

1. **Cyclic clones your repo**
2. **Installs Python dependencies** from `requirements.txt`
3. **Downloads models**:
   - Base model from HuggingFace (automatic)
   - Asripa model from HuggingFace (if `ASRIPA_MODEL_ID` is set)
4. **Starts your Flask app** with Gunicorn
5. **Your API is live!**

---

## ⚠️ Important Notes

### File Structure
Cyclic expects your Flask app to be accessible. If your structure is:
```
Emotion-detection/
  backend/
    main.py
    app/
    requirements.txt
```

You may need to:
- Set **Root Directory** to `backend` in Cyclic settings, OR
- Move `main.py` to project root (not recommended)

### Database & Storage
- **SQLite**: Works, but data may reset on redeploy (ephemeral)
- **File Storage**: 1GB included, but also ephemeral
- For persistent storage, consider Cyclic's storage options (paid)

### Model Download
- Models download on first startup
- Takes 2-5 minutes for first request
- Subsequent requests are fast

---

## 🔧 Troubleshooting

### Issue: "Module not found"
**Fix**: Make sure `requirements.txt` has all dependencies

### Issue: "Port already in use"
**Fix**: Cyclic sets PORT automatically, don't hardcode it

### Issue: "Model download fails"
**Fix**: Check `ASRIPA_MODEL_ID` environment variable is set correctly

### Issue: "App crashes on startup"
**Fix**: Check logs in Cyclic dashboard for error messages

---

## ✅ Success Checklist

- [ ] Signed up for Cyclic.sh
- [ ] Connected GitHub repo
- [ ] Created app
- [ ] Set `ASRIPA_MODEL_ID` environment variable
- [ ] Deployment successful
- [ ] Health endpoint works: `/health`
- [ ] Updated frontend to use Cyclic URL
- [ ] Tested emotion detection from frontend

---

## 🎉 You're Done!

Your emotion detection API is now live on Cyclic.sh with:
- ✅ Both models (Base + Asripa)
- ✅ Full API endpoints
- ✅ Always-on (no sleep)
- ✅ Free tier (10k requests/month)

**Your URL**: `https://your-app-name.cyclic.app`

---

## 📚 Next Steps

1. **Monitor**: Check Cyclic dashboard for usage
2. **Logs**: View logs if issues occur
3. **Upgrade** (if needed): If you exceed 10k requests/month

---

## 💡 Pro Tips

1. **Custom Domain**: Cyclic supports custom domains (paid feature)
2. **Auto-Deploy**: Every push to `main` auto-deploys
3. **Rollback**: Can rollback to previous deployments
4. **Environment**: Separate staging/production environments available

---

**Need help?** Check Cyclic docs: https://docs.cyclic.sh

