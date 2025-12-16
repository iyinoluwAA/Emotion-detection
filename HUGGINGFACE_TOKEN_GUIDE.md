# HuggingFace Token Setup for Asripa Model Upload

## Required Permissions

For uploading the Asripa model to HuggingFace Hub, you need:

### ✅ Minimum Required:
1. **Repositories** → **Write access** to contents/settings of repos under your personal namespace
   - This allows you to upload model files to your HuggingFace account

### ✅ Recommended (for easier management):
2. **Repositories** → **Read access** to contents of all repos under your personal namespace
   - Helps with managing and viewing your models

### ❌ NOT Required:
- Inference permissions (only needed if you want to use HuggingFace Inference API)
- Webhooks (only if you want webhook notifications)
- Collections (only if you want to organize models in collections)
- Billing (only if you're using paid features)
- Jobs (only if you want to run training jobs on HuggingFace)

## Step-by-Step Token Creation

1. Go to: https://huggingface.co/settings/tokens
2. Click **"New token"**
3. **Name**: `asripa-deployment` (or any name you prefer)
4. **Type**: Select **"Write"** (this gives write access to your repos)
5. **Expiration**: Choose your preference (or "No expiration" for permanent)
6. Click **"Generate token"**
7. **IMPORTANT**: Copy the token immediately (you won't see it again!)

## Token Permissions Summary

For **model upload only**, you need:
- ✅ **Write** access to your personal namespace repositories

That's it! The token will allow you to:
- Upload the Asripa model files
- Create new model repositories
- Update existing model repositories

## Next Steps

After creating the token:
1. Run: `python3 backend/scripts/hf_login.py`
2. Paste your token when prompted
3. Then run: `python3 backend/scripts/upload_asripa_to_huggingface.py`

