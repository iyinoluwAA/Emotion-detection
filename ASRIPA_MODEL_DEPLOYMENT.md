# Deploying Asripa Model (Fine-Tuned) - Complete Guide

## 🎯 Model Name: "Asripa"
**Meaning**: "The coming of a new age" - Perfect name for your improved model!

## 📊 Model Details
- **Name**: Asripa
- **Size**: ~328MB
- **Accuracy**: 78.26% on FER2013 validation
- **Performance**: Significantly better than base model for happy/surprise detection
- **Location**: `backend/models/fine_tuned_vit/`

## 🚀 Deployment Options (Ranked Best to Worst)

### Option 1: HuggingFace Hub ⭐ BEST FOR ML MODELS

**Why**: Built specifically for ML models, free, fast CDN, versioning

**Steps**:

1. **Install HuggingFace CLI**:
   ```bash
   pip install huggingface_hub
   ```

2. **Login to HuggingFace**:
   ```bash
   huggingface-cli login
   # Enter your token from https://huggingface.co/settings/tokens
   ```

3. **Create a model repository**:
   - Go to https://huggingface.co/new
   - Create repository: `your-username/asripa-emotion-detection`
   - Set to **Public** (free) or **Private** (if you want)

4. **Upload the model**:
   ```bash
   cd backend/models
   huggingface-cli upload your-username/asripa-emotion-detection fine_tuned_vit/ .
   ```

5. **Update entrypoint.sh to download Asripa**:
   ```bash
   # Add download logic for Asripa model
   ASRIPA_MODEL_DIR="/app/models/fine_tuned_vit"
   if [ ! -f "$ASRIPA_MODEL_DIR/model.safetensors" ]; then
     echo "Downloading Asripa model from HuggingFace..."
     huggingface-cli download your-username/asripa-emotion-detection --local-dir "$ASRIPA_MODEL_DIR"
   fi
   ```

**Pros**:
- ✅ Free
- ✅ Fast CDN
- ✅ Version control
- ✅ Easy to update
- ✅ Industry standard for ML models

**Cons**:
- ⚠️ Requires HuggingFace account (free)

---

### Option 2: GitHub Releases ⭐ EASY & FREE

**Why**: Free, integrated with your repo, easy to download

**Steps**:

1. **Create a release**:
   ```bash
   # Compress the model
   cd backend/models
   tar -czf asripa-model.tar.gz fine_tuned_vit/
   ```

2. **Upload to GitHub Releases**:
   - Go to your GitHub repo
   - Click "Releases" → "Create a new release"
   - Tag: `v1.0.0-asripa`
   - Upload `asripa-model.tar.gz`
   - Publish release

3. **Update entrypoint.sh**:
   ```bash
   ASRIPA_MODEL_DIR="/app/models/fine_tuned_vit"
   ASRIPA_MODEL_URL="https://github.com/iyinoluwAA/Emotion-detection/releases/download/v1.0.0-asripa/asripa-model.tar.gz"
   
   if [ ! -f "$ASRIPA_MODEL_DIR/model.safetensors" ]; then
     echo "Downloading Asripa model from GitHub Releases..."
     mkdir -p "$ASRIPA_MODEL_DIR"
     curl -L "$ASRIPA_MODEL_URL" -o /tmp/asripa-model.tar.gz
     tar -xzf /tmp/asripa-model.tar.gz -C "$ASRIPA_MODEL_DIR" --strip-components=1
     rm /tmp/asripa-model.tar.gz
   fi
   ```

**Pros**:
- ✅ Free
- ✅ Integrated with your repo
- ✅ Version control
- ✅ Easy to update

**Cons**:
- ⚠️ GitHub has 2GB file size limit per file
- ⚠️ Slower download than CDN

---

### Option 3: Railway Persistent Volume (If Available)

**Why**: Direct storage, no download needed

**Steps**:

1. **Check if Railway supports volumes**:
   - Railway may have persistent storage in paid plans
   - Check Railway dashboard → Your service → Settings → Volumes

2. **If available**:
   - Create a volume in Railway
   - Mount it to `/app/models/fine_tuned_vit`
   - Upload model files via Railway CLI or dashboard

**Pros**:
- ✅ Fast (no download)
- ✅ Persistent across deployments

**Cons**:
- ⚠️ May require paid plan
- ⚠️ Not available on free tier

---

### Option 4: Cloud Storage (S3, Google Cloud, etc.)

**Why**: Scalable, reliable, but requires setup

**Steps** (using Google Cloud Storage as example):

1. **Create bucket**:
   ```bash
   gsutil mb gs://your-bucket-name
   ```

2. **Upload model**:
   ```bash
   cd backend/models
   gsutil -m cp -r fine_tuned_vit/ gs://your-bucket-name/asripa/
   ```

3. **Update entrypoint.sh** to download from GCS

**Pros**:
- ✅ Scalable
- ✅ Reliable
- ✅ Fast CDN

**Cons**:
- ⚠️ Requires cloud account
- ⚠️ May have costs
- ⚠️ More complex setup

---

### Option 5: Railway CLI Direct Upload

**Why**: Direct upload to Railway service

**Steps**:

1. **Install Railway CLI**:
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Upload model files**:
   ```bash
   railway link  # Link to your project
   railway run --service your-service-name -- sh -c "mkdir -p /app/models/fine_tuned_vit"
   # Then use Railway's file upload feature or SCP
   ```

**Pros**:
- ✅ Direct to Railway
- ✅ No external dependencies

**Cons**:
- ⚠️ Complex
- ⚠️ May not persist across deployments

---

## 🎯 RECOMMENDED: HuggingFace Hub

**Best option because**:
1. Built for ML models
2. Free and fast
3. Industry standard
4. Easy versioning
5. No file size limits (within reason)

## 📝 Implementation Steps

### Step 1: Upload to HuggingFace

```bash
# Install CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Upload model
cd backend/models
huggingface-cli upload your-username/asripa-emotion-detection fine_tuned_vit/ .
```

### Step 2: Update entrypoint.sh

Add this to `backend/scripts/entrypoint.sh` before starting gunicorn:

```bash
# Download Asripa model if not present
ASRIPA_MODEL_DIR="/app/models/fine_tuned_vit"
ASRIPA_MODEL_ID="your-username/asripa-emotion-detection"

if [ ! -f "$ASRIPA_MODEL_DIR/model.safetensors" ]; then
  echo "📥 Downloading Asripa model from HuggingFace..."
  mkdir -p "$ASRIPA_MODEL_DIR"
  
  # Use Python to download (huggingface_hub is already in requirements)
  python3 -c "
from huggingface_hub import snapshot_download
import os
snapshot_download(
    repo_id='$ASRIPA_MODEL_ID',
    local_dir='$ASRIPA_MODEL_DIR',
    local_dir_use_symlinks=False
)
print('✅ Asripa model downloaded successfully!')
" || {
    echo "⚠️  Failed to download Asripa model, will use base model only"
    rm -rf "$ASRIPA_MODEL_DIR"
  }
else
  echo "✅ Asripa model already present"
fi
```

### Step 3: Update requirements.txt

Ensure `huggingface_hub` is in `backend/requirements.txt` (it should already be there if you have `transformers`)

### Step 4: Deploy

Push code and Railway will:
1. Build Docker image
2. Run entrypoint.sh
3. Download Asripa model from HuggingFace
4. Start app with both models available

## ✅ Verification

After deployment, check Railway logs:
```
[MODEL] 🎯 Loading Asripa model (FER2013 Enhanced): /app/models/fine_tuned_vit
[MODEL] Accuracy: 78.26% (fine-tuned on FER2013)
[MODEL] ✅ Fine-tuned ViT model loaded successfully!
[APP] Fine-tuned model loaded: type=vit, version=asripa-vit-78.26%
```

## 🔄 Updating the Model

When you improve Asripa:
1. Upload new version to HuggingFace (with new tag)
2. Update `ASRIPA_MODEL_ID` in entrypoint.sh
3. Redeploy - Railway will download the new version

## 💡 Alternative: Keep Model in Git (NOT RECOMMENDED)

You could use Git LFS, but:
- ❌ Slows down git operations
- ❌ Requires Git LFS setup
- ❌ Repository becomes huge
- ❌ Not ideal for deployment

**Better**: Use HuggingFace or GitHub Releases

