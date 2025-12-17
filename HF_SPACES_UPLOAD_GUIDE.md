# 🚀 Hugging Face Spaces - Upload Guide

## Step 1: Fill Out the Form ✅

Fill the form with:
- **Short description**: `AI-powered emotion detection API with Vision Transformer models. Detects 8 emotions from facial images with high accuracy.`
- **Space SDK**: **Docker**
- **Docker template**: **Blank**
- **Hardware**: **Free** (already selected)
- **Dev Mode**: Leave unchecked
- **Visibility**: **Public**

Click **"Create Space"**!

---

## Step 2: After Space is Created

Once your Space is created, you'll see a page with:
- Files tab
- Settings tab
- Logs tab

### Option A: Upload via Web Interface (Easier)

1. Go to **"Files and versions"** tab
2. Click **"Add file"** → **"Upload files"**
3. Upload these files from your `backend/` folder:
   - `main.py`
   - `requirements.txt`
   - `Dockerfile.hf` (rename to `Dockerfile` after upload)
   - `app/` folder (entire folder)
   - `scripts/entrypoint_hf.sh` (rename to `scripts/entrypoint.sh` after upload)
   - `vit_utils.py` (if in backend root)
   - `model_loader.py` (if in backend root)

### Option B: Use Git (Recommended - Easier)

1. In your Space, go to **"Files and versions"** tab
2. Click **"Use the CLI"** button
3. You'll see commands like:
   ```bash
   git clone https://huggingface.co/spaces/HimAJ/emotion-detection-api
   cd emotion-detection-api
   ```
4. Copy your backend files into this folder
5. Commit and push:
   ```bash
   git add .
   git commit -m "Add Flask API"
   git push
   ```

---

## Step 3: Set Environment Variable

1. Go to **"Settings"** tab
2. Scroll to **"Environment variables"**
3. Click **"Add variable"**
4. Add:
   - **Key**: `ASRIPA_MODEL_ID`
   - **Value**: `HimAJ/asripa-emotion-detection`
5. Click **"Save"**

---

## Step 4: Wait for Build

1. Go to **"Logs"** tab
2. Watch the build progress
3. First build takes ~10-15 minutes (downloading models)
4. You'll see:
   - Docker build logs
   - Model downloads
   - App startup

---

## Step 5: Test Your API

Once deployed, your API will be at:
```
https://huggingface.co/spaces/HimAJ/emotion-detection-api
```

Test endpoints:
- `https://huggingface.co/spaces/HimAJ/emotion-detection-api/health`
- `https://huggingface.co/spaces/HimAJ/emotion-detection-api/detect`

---

## Important Notes

### Port Configuration
- Hugging Face Spaces uses port **7860**
- The entrypoint script handles this automatically
- Your app will work on port 7860

### Files You Need
Make sure these files are in the Space root:
- `Dockerfile` (use `Dockerfile.hf` and rename it)
- `requirements.txt`
- `main.py`
- `app/` folder
- `scripts/entrypoint.sh` (use `entrypoint_hf.sh` and rename it)

### Database
- SQLite will work, but may reset on restart
- Consider this when testing

---

## Troubleshooting

### Build Fails
- Check **"Logs"** tab for errors
- Make sure all files are uploaded
- Verify `Dockerfile` is correct

### App Won't Start
- Check port is 7860
- Verify environment variables are set
- Check logs for errors

### Models Not Loading
- Check `ASRIPA_MODEL_ID` is set correctly
- Verify model exists on HuggingFace
- Check logs for download errors

---

## Next Steps After Deployment

1. **Update Frontend**: Point to Hugging Face URL
2. **Test API**: Try `/health` and `/detect` endpoints
3. **Monitor Logs**: Check for any errors

Let me know when you've created the Space and I'll help you upload the files!

