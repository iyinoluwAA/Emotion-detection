# 🚀 Quick Start: Deploy Asripa Model

## Step 1: Upload Asripa to HuggingFace (5 minutes)

```bash
# Install HuggingFace CLI
pip install huggingface_hub

# Login
huggingface-cli login
# Get token from: https://huggingface.co/settings/tokens

# Upload model
python3 backend/scripts/upload_asripa_to_huggingface.py
```

Or manually:
```bash
cd backend/models
huggingface-cli upload your-username/asripa-emotion-detection fine_tuned_vit/ .
```

## Step 2: Set Environment Variable in Railway

1. Go to Railway dashboard
2. Select your service
3. Go to **Variables** tab
4. Add:
   - **Name**: `ASRIPA_MODEL_ID`
   - **Value**: `your-username/asripa-emotion-detection`
5. Save

## Step 3: Deploy

Railway will automatically:
- Download Asripa model on startup
- Make it available alongside base model
- Users can select "Asripa" from dropdown

## ✅ Verify

Check Railway logs - you should see:
```
📥 Downloading Asripa model from HuggingFace...
✅ Asripa model downloaded successfully!
[MODEL] 🎯 Loading Asripa model (FER2013 Enhanced)
[MODEL] Accuracy: 78.26% (fine-tuned on FER2013)
[APP] Asripa model loaded: type=vit, version=asripa-vit-78.26%
```

## 🎯 That's It!

Asripa will be available in the frontend dropdown as "Asripa" (no percentages shown to users, but backend logs show accuracy).

