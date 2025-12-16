# Vercel Environment Variable Setup

## The Problem
Frontend says "backend is offline" because the environment variable is missing `https://` protocol.

## Fix in Vercel Dashboard

### Step 1: Go to Vercel Project Settings
1. Open your Vercel project dashboard
2. Go to **Settings** → **Environment Variables**

### Step 2: Update VITE_API_URL
**Current (WRONG):**
```
VITE_API_URL = emotion-backend-production-3d90.up.railway.app
```

**Should be (CORRECT):**
```
VITE_API_URL = https://emotion-backend-production-3d90.up.railway.app
```

### Step 3: Save and Redeploy
1. Click **Save**
2. Vercel will automatically redeploy with the new environment variable
3. Wait for deployment to complete (~1-2 minutes)

## Verify It Works

After redeploy, check:
1. Frontend should show "Backend Online" (green badge)
2. You can upload images and get predictions
3. The surprise image should classify correctly as "surprise" (not neutral/fear)

## Railway Environment Variables

**You DON'T need to set anything in Railway** - the backend is already configured correctly. The issue is only in Vercel's environment variable.

## Troubleshooting

If still offline after fixing:
1. Check browser console for CORS errors
2. Verify Railway backend is running (check Railway logs)
3. Make sure the URL in Vercel has `https://` (not `http://`)


