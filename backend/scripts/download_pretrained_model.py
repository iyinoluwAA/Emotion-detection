#!/usr/bin/env python3
"""
Download a better pre-trained emotion detection model.

Options:
1. Emo0.1 (HuggingFace) - VGG16-based, better accuracy
2. Other pre-trained models from GitHub

This is faster than retraining from scratch.
"""
import os
import sys
import shutil
import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"

def download_emo01():
    """Try alternative HuggingFace repositories."""
    print("📥 Trying alternative pre-trained models...")
    
    # Try different HuggingFace repos
    repos = [
        ("shivampr1001/Emo0.1", "emotion_model.h5"),
        ("pysentimiento/robertuito-emotion-analysis", "pytorch_model.bin"),  # Different format
    ]
    
    try:
        from huggingface_hub import hf_hub_download, list_repo_files
        
        for repo_id, filename in repos:
            try:
                print(f"   Trying {repo_id}...")
                # Check what files are available
                files = list_repo_files(repo_id, repo_type="model")
                print(f"   Available files: {files[:5]}...")  # Show first 5
                
                # Try to download the model file
                model_path = hf_hub_download(
                    repo_id=repo_id,
                    filename=filename,
                    local_dir=str(MODELS_DIR),
                )
                
                if Path(model_path).exists():
                    target_path = MODELS_DIR / "emotion_model.keras"
                    # Copy instead of move in case it's in a subdirectory
                    shutil.copy2(model_path, target_path)
                    print(f"✅ Model downloaded to: {target_path}")
                    return True
            except Exception as e:
                print(f"   ❌ {repo_id} failed: {e}")
                continue
        
        return False
    except ImportError:
        print("❌ huggingface_hub not installed.")
        print("\nInstall it with:")
        print("  pip install huggingface_hub")
        return False
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def download_github_model():
    """Download pre-trained model from GitHub."""
    print("📥 Downloading pre-trained FER2013 model from GitHub...")
    
    # Try multiple sources
    urls = [
        "https://github.com/justinshenk/fer/releases/download/v1.0.0/fer2013_model.h5",
        "https://github.com/atulapra/Emotion-detection/raw/master/model.h5",
    ]
    
    target_path = MODELS_DIR / "emotion_model.keras"
    temp_path = MODELS_DIR / "model_temp.h5"
    
    for i, url in enumerate(urls, 1):
        try:
            print(f"   Trying source {i}/{len(urls)}...")
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            if total_size > 0:
                print(f"   Downloading {total_size / (1024*1024):.1f} MB...")
            else:
                print(f"   Downloading...")
            
            with open(temp_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r   Progress: {percent:.1f}%", end='', flush=True)
            
            # Move to final location
            if temp_path.exists():
                shutil.move(str(temp_path), str(target_path))
                print(f"\n✅ Model downloaded to: {target_path}")
                return True
        except Exception as e:
            print(f"\n   ❌ Failed: {e}")
            if temp_path.exists():
                temp_path.unlink()
            continue
    
    print("\n❌ All download sources failed.")
    return False

def download_emopy_model():
    """Try to get model info from EmoPy (requires installation)."""
    print("📥 EmoPy is a library, not a direct model download.")
    print("   You would need to: pip install emopy")
    print("   Then use their API to load the model.")
    print("\n   This is more complex - let's try other options first.")
    return False

def main():
    print("="*60)
    print("Pre-trained Model Downloader")
    print("="*60)
    print("\nOptions:")
    print("1. GitHub model (justinshenk/fer) - RECOMMENDED")
    print("2. Try HuggingFace alternatives")
    print("\nWhich model would you like to download?")
    print("(Enter 1 or 2, or press Enter to use option 1)")
    
    choice = input().strip() or "1"
    
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    if choice == "1":
        if download_github_model():
            print("\n✅ Model ready!")
            print("\nNote: This model uses the same 7 emotions:")
            print("  angry, disgust, fear, happy, neutral, sad, surprise")
            print("\nThe model should work with your current code.")
            print("\n⚠️  If the model format is .h5, TensorFlow should load it.")
            print("   If you get errors, we may need to convert it.")
    elif choice == "2":
        if download_emo01():
            print("\n✅ Model ready!")
        else:
            print("\n❌ HuggingFace models not available.")
            print("   Try option 1 (GitHub model) instead.")
    else:
        print("Invalid choice. Please run again and select 1 or 2.")

if __name__ == "__main__":
    main()

