# 🆓 Free Hosting Options (No Credit Card Required)

Since your Railway trial expired and the model is on HuggingFace, here are **FREE** alternatives:

## ✅ Best Options (No Credit Card)

### 1. **Render** ⭐ RECOMMENDED (You mentioned it)
- **Free Tier**: ✅ Yes
- **Credit Card**: ❌ NOT REQUIRED
- **Memory**: 512MB (enough since model downloads from HuggingFace)
- **Sleeps**: After 15 min inactivity (wakes on request)
- **Docker**: ✅ Supported
- **Setup**: https://render.com

**Quick Setup:**
1. Sign up at https://render.com (GitHub login)
2. New → Web Service
3. Connect your GitHub repo
4. Settings:
   - **Build Command**: (auto-detected)
   - **Start Command**: (auto-detected)
   - **Dockerfile Path**: `backend/Dockerfile`
5. Add Environment Variable:
   - `ASRIPA_MODEL_ID=HimAJ/asripa-emotion-detection`
6. Deploy!

**Note**: Since model downloads from HuggingFace at runtime, 512MB is enough!

---

### 2. **Koyeb** ⭐ GOOD ALTERNATIVE
- **Free Tier**: ✅ Yes
- **Credit Card**: ❌ NOT REQUIRED
- **Memory**: 512MB
- **Docker**: ✅ Supported
- **Setup**: https://www.koyeb.com

**Quick Setup:**
1. Sign up at https://www.koyeb.com
2. Create App → Docker
3. Connect GitHub repo
4. Set Dockerfile: `backend/Dockerfile`
5. Add env var: `ASRIPA_MODEL_ID=HimAJ/asripa-emotion-detection`
6. Deploy!

---

### 3. **Fly.io** (Requires Credit Card)
- ❌ Requires credit card (even for free tier)
- Skip this if you don't have one

---

### 4. **Replit** (Alternative)
- **Free Tier**: ✅ Yes
- **Credit Card**: ❌ NOT REQUIRED
- **Limitations**: Slower, but works
- **Setup**: https://replit.com

---

## 🚀 Recommended: Render

Since you already know about Render and it's free:

### Step-by-Step Render Setup

1. **Sign Up**: https://render.com (use GitHub)

2. **Create Web Service**:
   - Dashboard → New → Web Service
   - Connect GitHub repository: `Emotion-detection`
   - Select the repo

3. **Configure**:
   - **Name**: `emotion-backend` (or your choice)
   - **Region**: Choose closest to you
   - **Branch**: `main` (or your default)
   - **Root Directory**: Leave empty (or `backend` if needed)
   - **Environment**: `Docker`
   - **Dockerfile Path**: `backend/Dockerfile`
   - **Docker Context**: `.` (project root)

4. **Environment Variables**:
   - Click "Advanced" → "Environment Variables"
   - Add:
     - `ASRIPA_MODEL_ID` = `HimAJ/asripa-emotion-detection`
     - `PORT` = `5000` (usually auto-set)

5. **Deploy**:
   - Click "Create Web Service"
   - Wait for build (~5-10 minutes)
   - Get your URL: `https://your-app.onrender.com`

6. **Update Frontend**:
   - Edit `frontend/src/api/config.ts`
   - Change production URL to your Render URL
   - Deploy frontend to Vercel (still free)

---

## ⚠️ Important Notes

### Render Free Tier Limitations:
- **Sleeps after 15 min** of inactivity
- **Cold start**: First request after sleep takes ~30-60 seconds
- **Memory**: 512MB (enough for HuggingFace downloads)
- **Bandwidth**: 100GB/month (plenty)

### Since Model is on HuggingFace:
- ✅ No need to store 328MB model files
- ✅ Downloads at runtime (entrypoint.sh handles it)
- ✅ 512MB memory is enough!
- ✅ Render free tier will work fine

---

## 🔄 Migration from Railway

1. **Export Railway env vars** (if any):
   - Copy `ASRIPA_MODEL_ID` value

2. **Deploy to Render**:
   - Follow steps above

3. **Update Frontend**:
   - Change `VITE_API_URL` in Vercel to Render URL

4. **Test**:
   - First request will be slow (cold start + model download)
   - Subsequent requests will be fast

---

## 💡 Pro Tips

1. **Keep Render awake**: Use a free service like UptimeRobot to ping your app every 10 minutes
2. **Monitor**: Render dashboard shows logs and metrics
3. **Free forever**: Render free tier doesn't expire (unlike Railway trial)

---

## ✅ Quick Checklist

- [ ] Sign up at Render.com
- [ ] Create Web Service
- [ ] Connect GitHub repo
- [ ] Set Dockerfile path: `backend/Dockerfile`
- [ ] Add env var: `ASRIPA_MODEL_ID=HimAJ/asripa-emotion-detection`
- [ ] Deploy
- [ ] Update frontend URL
- [ ] Test!

