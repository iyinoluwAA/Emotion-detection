# 🚀 Hugging Face Spaces - How to Add Your Code

## Important: How Hugging Face Spaces Works

**Hugging Face Spaces is NOT connected to GitHub like Render/Railway.**

Instead:
- The Space itself IS a Git repository (on HuggingFace)
- You clone the Space repo → add your code → push back to it
- OR upload files directly via web interface

---

## Option 1: Use Git (Recommended - Easier)

### Step 1: Clone the Space Repository

```bash
# Clone your Space (it's a Git repo on HuggingFace)
git clone https://huggingface.co/spaces/HimAJ/emotion-detection-api
cd emotion-detection-api
```

**When prompted for password**: Use your HuggingFace access token (not your password)
- Get token from: https://huggingface.co/settings/tokens
- Make sure it has **"Write"** permissions

### Step 2: Copy Your Backend Files

```bash
# From your Emotion-detection project
cd /home/iyino/projects/Emotion-detection

# Copy backend files to the Space repo
cp -r backend/* ~/emotion-detection-api/
```

Or manually copy:
- `backend/main.py` → `emotion-detection-api/main.py`
- `backend/requirements.txt` → `emotion-detection-api/requirements.txt`
- `backend/app/` → `emotion-detection-api/app/`
- `backend/scripts/entrypoint_hf.sh` → `emotion-detection-api/scripts/entrypoint.sh`
- `backend/Dockerfile.hf` → `emotion-detection-api/Dockerfile`
- Other backend files

### Step 3: Update Files for Hugging Face

1. **Rename Dockerfile**:
   ```bash
   mv Dockerfile.hf Dockerfile
   ```

2. **Rename entrypoint**:
   ```bash
   mv scripts/entrypoint_hf.sh scripts/entrypoint.sh
   chmod +x scripts/entrypoint.sh
   ```

### Step 4: Commit and Push

```bash
cd ~/emotion-detection-api

# Add all files
git add .

# Commit
git commit -m "Add Flask emotion detection API"

# Push to HuggingFace Space
git push
```

**When prompted for password**: Use your HuggingFace access token

---

## Option 2: Upload via Web Interface (Simpler)

### Step 1: Go to Your Space

1. Go to: https://huggingface.co/spaces/HimAJ/emotion-detection-api
2. Click **"Files and versions"** tab
3. Click **"Add file"** → **"Upload files"**

### Step 2: Upload Files

Upload these files from your `backend/` folder:

**Required files:**
- `main.py`
- `requirements.txt`
- `Dockerfile.hf` (rename to `Dockerfile` after upload)
- `app/` folder (upload entire folder)
- `scripts/entrypoint_hf.sh` (upload, then rename to `entrypoint.sh`)
- `vit_utils.py` (if exists)
- `model_loader.py` (if exists)

**How to upload:**
1. Click **"Add file"** → **"Upload files"**
2. Drag and drop files or click to browse
3. After upload, click on file name to rename if needed

### Step 3: Set Environment Variable

1. Go to **"Settings"** tab
2. Scroll to **"Environment variables"**
3. Add:
   - **Key**: `ASRIPA_MODEL_ID`
   - **Value**: `HimAJ/asripa-emotion-detection`
4. Click **"Save"**

---

## Which Option Should You Use?

**Option 1 (Git)**: Better for version control, easier updates later
**Option 2 (Web)**: Faster, simpler, no Git needed

**I recommend Option 2 (Web upload)** for your first time - it's simpler!

---

## Quick Steps (Web Upload - Easiest)

1. Go to: https://huggingface.co/spaces/HimAJ/emotion-detection-api
2. Click **"Files and versions"** tab
3. Click **"Add file"** → **"Upload files"**
4. Upload your backend files
5. Rename `Dockerfile.hf` to `Dockerfile`
6. Rename `entrypoint_hf.sh` to `entrypoint.sh`
7. Go to **"Settings"** → Add environment variable `ASRIPA_MODEL_ID=HimAJ/asripa-emotion-detection`
8. Wait for automatic build!

Let me know which option you want to use!

