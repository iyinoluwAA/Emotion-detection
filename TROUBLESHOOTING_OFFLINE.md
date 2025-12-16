# Troubleshooting: Frontend Shows "Backend Offline"

## Quick Checks

### 1. Verify Vercel Environment Variable
**In Vercel Dashboard:**
- Go to Settings → Environment Variables
- Check `VITE_API_URL` value
- **Must be:** `https://emotion-backend-production-3d90.up.railway.app`
- **NOT:** `emotion-backend-production-3d90.up.railway.app` (missing https://)
- **NOT:** `https://emotion-backend-production-3d90.up.railway.` (truncated)

### 2. Verify Railway Backend is Running
**Check Railway Dashboard:**
- Go to your Railway project
- Check "Deployments" tab
- Should show "Active" status
- Check logs - should see: `[APP] Model loaded: type=vit`

### 3. Test Backend Directly
Open in browser:
```
https://emotion-backend-production-3d90.up.railway.app/health
```

Should return JSON:
```json
{
  "ok": true,
  "model_loaded": true,
  "model_version": "hardlyhumans-vit-92.2%",
  "model_type": "vit"
}
```

### 4. Check Browser Console
**Open browser DevTools (F12):**
- Go to Console tab
- Look for errors like:
  - `CORS error`
  - `Failed to fetch`
  - `Network error`
- Go to Network tab
- Try to upload an image
- Check if `/health` request is being made
- Check the request URL (should include `https://`)

### 5. Common Issues

#### Issue: CORS Error
**Symptom:** Browser console shows "CORS policy" error
**Fix:** Backend CORS is set to `*` (allows all), so this shouldn't happen. If it does, check Railway logs.

#### Issue: Timeout
**Symptom:** Request times out after 5 seconds
**Fix:** Railway might be slow to start. Wait 30 seconds and refresh.

#### Issue: Wrong URL
**Symptom:** 404 or connection refused
**Fix:** Double-check the Railway URL in Vercel environment variable

#### Issue: Environment Variable Not Applied
**Symptom:** Frontend still uses old URL
**Fix:** 
1. Save environment variable in Vercel
2. **Redeploy** (Vercel should auto-redeploy, but you can trigger manually)
3. Wait for deployment to complete
4. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)

### 6. Debug Steps

**Step 1: Check what URL frontend is using**
- Open browser DevTools → Console
- Type: `import.meta.env.VITE_API_URL`
- Should show: `https://emotion-backend-production-3d90.up.railway.app`

**Step 2: Test health endpoint manually**
- Open browser
- Go to: `https://emotion-backend-production-3d90.up.railway.app/health`
- Should return JSON (not error page)

**Step 3: Check Railway logs**
- Railway Dashboard → Your service → Logs
- Should see recent activity
- Should see: `[APP] Model loaded: type=vit`

**Step 4: Force frontend to use Railway URL**
If environment variable isn't working, you can temporarily hardcode it in `frontend/src/api/config.ts`:
```typescript
return "https://emotion-backend-production-3d90.up.railway.app";
```

### 7. Still Not Working?

1. **Clear browser cache** (hard refresh: Ctrl+Shift+R)
2. **Check Railway service is running** (not sleeping)
3. **Verify Railway URL** (copy from Railway dashboard)
4. **Check Vercel deployment logs** for build errors
5. **Try incognito/private window** to rule out cache issues


