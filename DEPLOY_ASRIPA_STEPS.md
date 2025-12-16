# 🚀 Deploy Asripa Model to HuggingFace & Railway

## Step 1: Get HuggingFace Token

1. Go to: https://huggingface.co/settings/tokens
2. Click **"New token"**
3. Name it: `asripa-deployment`
4. Select **"Write"** permissions
5. Click **"Generate token"**
6. **Copy the token** (you'll need it next)

## Step 2: Login to HuggingFace

Run from project root:
```bash
python3 backend/scripts/hf_login.py
```
Paste your token when prompted.

## Step 3: Create Model Repository

1. Go to: https://huggingface.co/new
2. Select **"Model"**
3. Repository name: `asripa-emotion-detection` (or your choice)
4. Visibility: **Public** (free) or Private
5. Click **"Create repository"**

## Step 4: Upload Asripa Model

Run from project root:
```bash
python3 backend/scripts/upload_asripa_to_huggingface.py
```

When prompted, enter your model ID:
- Format: `your-username/asripa-emotion-detection`
- Example: `iyinoluwAA/asripa-emotion-detection`

This will upload ~328MB (takes a few minutes).

## Step 5: Set Environment Variable in Railway

1. Go to your Railway project dashboard
2. Select your backend service
3. Go to **"Variables"** tab
4. Add new variable:
   - **Name**: `ASRIPA_MODEL_ID`
   - **Value**: `your-username/asripa-emotion-detection` (same as Step 4)
5. Click **"Add"**

## Step 6: Redeploy

Railway will automatically redeploy. On startup, it will:
- Download Asripa from HuggingFace
- Make it available alongside the base model
- Users can select "Asripa" from the frontend dropdown

## ✅ Verification

After deployment, check Railway logs for:
```
✅ Asripa model downloaded successfully!
```

Then test on frontend - select "Asripa" from dropdown and upload an image.

---

**Note**: The Dockerfile doesn't need changes - it already has `huggingface_hub` in requirements.txt and `entrypoint.sh` handles the download automatically.

