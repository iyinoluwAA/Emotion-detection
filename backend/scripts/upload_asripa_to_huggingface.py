#!/usr/bin/env python3
"""
Upload Asripa model to HuggingFace Hub.

Usage:
    python3 backend/scripts/upload_asripa_to_huggingface.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def upload_asripa():
    """Upload Asripa model to HuggingFace Hub."""
    try:
        from huggingface_hub import HfApi, create_repo
        import os
    except ImportError:
        print("❌ Missing huggingface_hub. Install with:")
        print("   pip install huggingface_hub")
        return False
    
    repo_root = Path(__file__).parent.parent.parent
    model_dir = repo_root / "backend" / "models" / "fine_tuned_vit"
    
    if not (model_dir / "model.safetensors").exists():
        print(f"❌ Asripa model not found at: {model_dir}")
        print("   Make sure fine-tuning completed successfully")
        return False
    
    print("🚀 Uploading Asripa model to HuggingFace Hub...")
    print(f"   Model directory: {model_dir}")
    
    # Get model ID from user
    print("\n📝 HuggingFace Model Repository Setup:")
    print("   1. Go to https://huggingface.co/new")
    print("   2. Create a new model repository")
    print("   3. Name it: your-username/asripa-emotion-detection")
    print("   4. Set visibility: Public (free) or Private")
    print()
    
    model_id = input("Enter your HuggingFace model ID (e.g., username/asripa-emotion-detection): ").strip()
    
    if not model_id:
        print("❌ Model ID required")
        return False
    
    if "/" not in model_id:
        print("❌ Model ID must be in format: username/model-name")
        return False
    
    # Check if logged in
    api = HfApi()
    try:
        whoami = api.whoami()
        print(f"✅ Logged in as: {whoami['name']}")
    except Exception:
        print("❌ Not logged in to HuggingFace")
        print("   Run: huggingface-cli login")
        return False
    
    # Create repo if it doesn't exist
    try:
        create_repo(model_id, exist_ok=True, repo_type="model")
        print(f"✅ Repository ready: {model_id}")
    except Exception as e:
        print(f"⚠️  Could not create repo (may already exist): {e}")
    
    # Upload model
    print(f"\n📤 Uploading model files...")
    print("   This may take a few minutes (328MB)...")
    
    try:
        api.upload_folder(
            folder_path=str(model_dir),
            repo_id=model_id,
            repo_type="model",
            ignore_patterns=["*.log", "__pycache__", "*.pyc"]
        )
        print(f"\n✅ Asripa model uploaded successfully!")
        print(f"   Model URL: https://huggingface.co/{model_id}")
        print(f"\n📝 Next steps:")
        print(f"   1. Set environment variable in Railway:")
        print(f"      ASRIPA_MODEL_ID={model_id}")
        print(f"   2. Redeploy your Railway service")
        print(f"   3. Asripa model will download automatically on startup")
        return True
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = upload_asripa()
    sys.exit(0 if success else 1)

