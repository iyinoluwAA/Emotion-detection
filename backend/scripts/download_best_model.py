#!/usr/bin/env python3
"""
Download the BEST emotion detection models found in deep research.

Top models:
1. HardlyHumans/Facial-expression-detection - 92.2% accuracy ⭐ BEST
2. prithivMLmods/Facial-Emotion-Detection-SigLIP2 - 86.65% accuracy
3. FelaKuti/Emotion-detection - 82.3% accuracy (already downloaded)

Usage:
    python3 scripts/download_best_model.py
"""
import sys
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"

def download_hardlyhumans_model():
    """Download HardlyHumans/Facial-expression-detection - 92.2% accuracy!"""
    print("📥 Downloading HardlyHumans/Facial-expression-detection...")
    print("   ⭐ Accuracy: 92.2% (BEST FOUND!)")
    print("   Architecture: Vision Transformer (ViT)")
    print("   Training: FER2013 + AffectNet")
    print("   Link: https://huggingface.co/HardlyHumans/Facial-expression-detection")
    
    try:
        from huggingface_hub import hf_hub_download, list_repo_files
        
        repo_id = "HardlyHumans/Facial-expression-detection"
        
        print("\n   Checking available files...")
        files = list_repo_files(repo_id, repo_type="model")
        print(f"   Found {len(files)} files")
        if len(files) <= 10:
            for f in files:
                print(f"      - {f}")
        
        # Look for model files
        model_file = None
        for f in files:
            if f.endswith(('.h5', '.keras', '.pth', '.pt', '.safetensors', '.bin', '.ckpt')):
                model_file = f
                break
        
        if not model_file:
            # Try common names
            for name in ['model.h5', 'pytorch_model.bin', 'model.safetensors', 'model.keras']:
                if name in files:
                    model_file = name
                    break
        
        if not model_file:
            print("   ⚠️  No standard model file found.")
            print("   Available files:")
            for f in files[:10]:
                print(f"      - {f}")
            print("\n   This is a Vision Transformer model.")
            print("   It may need to be loaded using transformers library.")
            print("   Check the model card for usage instructions.")
            return False
        
        print(f"   Downloading: {model_file}")
        
        # Download model
        model_path = hf_hub_download(
            repo_id=repo_id,
            filename=model_file,
            local_dir=str(MODELS_DIR / "hardlyhumans"),
        )
        
        print(f"\n✅ Model downloaded to: {model_path}")
        print("\n⚠️  IMPORTANT: This is a Vision Transformer model.")
        print("   It may require different loading code.")
        print("   Check: https://huggingface.co/HardlyHumans/Facial-expression-detection")
        print("   for usage examples.")
        
        return True
        
    except ImportError:
        print("❌ huggingface_hub not installed.")
        print("\nInstall it with:")
        print("  pip install huggingface_hub")
        return False
    except Exception as e:
        print(f"❌ Download failed: {e}")
        print("\n💡 This model may require transformers library:")
        print("   pip install transformers")
        return False

def download_siglip_model():
    """Download SigLIP2 model - 86.65% accuracy."""
    print("📥 Downloading prithivMLmods/Facial-Emotion-Detection-SigLIP2...")
    print("   Accuracy: 86.65%")
    print("   Architecture: SigLIP2 (Google)")
    
    try:
        from huggingface_hub import hf_hub_download, list_repo_files
        
        repo_id = "prithivMLmods/Facial-Emotion-Detection-SigLIP2"
        
        print("\n   Checking available files...")
        files = list_repo_files(repo_id, repo_type="model")
        
        # Look for model files
        model_file = None
        for f in files:
            if f.endswith(('.safetensors', '.bin', '.h5', '.keras')):
                model_file = f
                break
        
        if not model_file:
            print("   ⚠️  No standard model file found.")
            return False
        
        print(f"   Downloading: {model_file}")
        
        model_path = hf_hub_download(
            repo_id=repo_id,
            filename=model_file,
            local_dir=str(MODELS_DIR / "siglip2"),
        )
        
        print(f"\n✅ Model downloaded to: {model_path}")
        print("\n⚠️  This is a SigLIP2 model - may need special loading.")
        
        return True
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def main():
    print("="*70)
    print("BEST Emotion Detection Models - Deep Research Results")
    print("="*70)
    print("\n🏆 Top Models Found:")
    print("\n1. HardlyHumans/Facial-expression-detection")
    print("   ⭐ Accuracy: 92.2% (BEST!)")
    print("   Architecture: Vision Transformer")
    print("   Trained on: FER2013 + AffectNet")
    print("\n2. prithivMLmods/Facial-Emotion-Detection-SigLIP2")
    print("   Accuracy: 86.65%")
    print("   Architecture: SigLIP2")
    print("\n3. FelaKuti/Emotion-detection")
    print("   Accuracy: 82.3%")
    print("   Status: ✅ Already downloaded")
    print("\n" + "="*70)
    print("⚠️  Note: Higher accuracy models may need different loading code")
    print("   (Vision Transformers, SigLIP, etc.)")
    print("="*70)
    
    choice = input("\nWhich model to download? (1, 2, or Enter for 1): ").strip() or "1"
    
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    if choice == "1":
        if download_hardlyhumans_model():
            print("\n✅ HardlyHumans model ready!")
            print("\n💡 Next steps:")
            print("   1. Check model card for usage: https://huggingface.co/HardlyHumans/Facial-expression-detection")
            print("   2. May need: pip install transformers")
            print("   3. Update model_loader.py if needed")
            print("   4. Test with your surprised image!")
    elif choice == "2":
        if download_siglip_model():
            print("\n✅ SigLIP2 model ready!")
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()


