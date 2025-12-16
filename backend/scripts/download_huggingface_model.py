#!/usr/bin/env python3
"""
Download emotion detection model from HuggingFace.

Found models:
1. FelaKuti/Emotion-detection - 82.3% accuracy, MobileNetV2, 7 emotions
2. abhilash88/fer2013-enhanced - Enhanced FER2013 dataset

Usage:
    python3 scripts/download_huggingface_model.py
"""
import sys
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"

def download_felakuti_model():
    """Download FelaKuti/Emotion-detection model from HuggingFace."""
    print("📥 Downloading FelaKuti/Emotion-detection from HuggingFace...")
    print("   Accuracy: 82.3%")
    print("   Architecture: MobileNetV2")
    print("   Emotions: anger, happiness, sadness, fear, surprise, disgust, neutral")
    
    try:
        from huggingface_hub import hf_hub_download, list_repo_files
        
        repo_id = "FelaKuti/Emotion-detection"
        
        # Check what files are available
        print("\n   Checking available files...")
        files = list_repo_files(repo_id, repo_type="model")
        print(f"   Found files: {files}")
        
        # Try to find model file
        model_file = None
        for f in files:
            if f.endswith(('.h5', '.keras', '.pth', '.pt', '.pkl', 'model.ckpt')):
                model_file = f
                break
        
        if not model_file:
            # Try common names
            for name in ['model.h5', 'emotion_model.h5', 'best_model.h5', 'model.keras']:
                if name in files:
                    model_file = name
                    break
        
        if not model_file:
            print("   ⚠️  No model file found. Available files:")
            for f in files:
                print(f"      - {f}")
            print("\n   You may need to load this model differently.")
            print("   Check the model card on HuggingFace for usage instructions.")
            return False
        
        print(f"   Downloading: {model_file}")
        
        # Download model
        model_path = hf_hub_download(
            repo_id=repo_id,
            filename=model_file,
            local_dir=str(MODELS_DIR),
        )
        
        # Copy to standard location
        target_path = MODELS_DIR / "emotion_model.keras"
        
        # Handle different file formats
        if model_path.endswith('.h5'):
            # Try to copy as .keras (TensorFlow can load .h5 as .keras)
            shutil.copy2(model_path, target_path)
        else:
            # For other formats, we might need conversion
            shutil.copy2(model_path, target_path)
        
        print(f"\n✅ Model downloaded to: {target_path}")
        print("\n⚠️  Note: This model uses MobileNetV2 architecture.")
        print("   You may need to adjust model_loader.py to load it correctly.")
        print("   Check the model card: https://huggingface.co/FelaKuti/Emotion-detection")
        
        return True
        
    except ImportError:
        print("❌ huggingface_hub not installed.")
        print("\nInstall it with:")
        print("  pip install huggingface_hub")
        return False
    except Exception as e:
        print(f"❌ Download failed: {e}")
        print("\n💡 Alternative: Download manually from:")
        print("   https://huggingface.co/FelaKuti/Emotion-detection")
        return False

def download_clip_fer2013():
    """Download CLIP model fine-tuned on FER2013."""
    print("📥 Downloading tanganke/clip-vit-base-patch32_fer2013 from HuggingFace...")
    print("   Accuracy: 71.6% (fine-tuned)")
    print("   Architecture: CLIP ViT-Base")
    print("   Dataset: FER2013")
    print("   ⚠️  This is a CLIP model - may need different loading approach")
    
    try:
        from huggingface_hub import hf_hub_download, list_repo_files
        
        repo_id = "tanganke/clip-vit-base-patch32_fer2013"
        
        print("\n   Checking available files...")
        files = list_repo_files(repo_id, repo_type="model")
        print(f"   Found {len(files)} files")
        
        # CLIP models usually have model files in safetensors or pytorch format
        # We'll need to handle this differently - CLIP is not a simple Keras model
        print("\n   ⚠️  CLIP models require special handling.")
        print("   This model may not work directly with your current code.")
        print("   Consider using FER2013 training instead for compatibility.")
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("="*60)
    print("HuggingFace Model Downloader")
    print("="*60)
    print("\nAvailable Models:")
    print("\n1. FelaKuti/Emotion-detection")
    print("   - 82.3% accuracy")
    print("   - MobileNetV2 architecture")
    print("   - 7 emotions")
    print("\n2. tanganke/clip-vit-base-patch32_fer2013")
    print("   - 71.6% accuracy")
    print("   - CLIP ViT-Base (different architecture)")
    print("   - Trained on FER2013")
    print("\n" + "="*60)
    print("⚠️  IMPORTANT: Most HuggingFace 'emotion detection' models are")
    print("   TEXT-based, not IMAGE-based. You need FACIAL emotion detection.")
    print("="*60)
    
    choice = input("\nWhich model? (1 or 2, or Enter for 1): ").strip() or "1"
    
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    if choice == "1":
        if download_felakuti_model():
            print("\n✅ Model ready!")
            print("\n⚠️  IMPORTANT: This model uses MobileNetV2, not the same architecture")
            print("   as your current model. You may need to update model_loader.py")
            print("   to load it correctly.")
            print("\n   Check the model card for usage instructions:")
            print("   https://huggingface.co/FelaKuti/Emotion-detection")
        else:
            print("\n❌ Download failed.")
            print("\n💡 Recommendation: Train on FER2013 instead.")
            print("   It's more reliable and compatible with your code.")
    elif choice == "2":
        if download_clip_fer2013():
            print("\n✅ Model ready!")
        else:
            print("\n❌ CLIP model requires special handling.")
            print("\n💡 Recommendation: Train on FER2013 instead.")
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()

