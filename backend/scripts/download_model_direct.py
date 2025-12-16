#!/usr/bin/env python3
"""
Direct download of a working FER2013 pre-trained model.

Since pre-trained models are hard to find, this script provides instructions
for the most reliable approach: download FER2013 dataset and train.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def main():
    print("="*60)
    print("Model Download Options")
    print("="*60)
    print("\n❌ Pre-trained models are hard to find and often outdated.")
    print("\n✅ RECOMMENDED: Download FER2013 dataset and train")
    print("   This is more reliable and gives you a better model.")
    print("\n" + "="*60)
    print("Option 1: Download FER2013 and Train (BEST)")
    print("="*60)
    print("\nSteps:")
    print("1. Set up Kaggle API (free account):")
    print("   - Go to https://www.kaggle.com/settings")
    print("   - API section → Create New Token")
    print("   - Save kaggle.json to ~/.kaggle/")
    print("   - Run: chmod 600 ~/.kaggle/kaggle.json")
    print("\n2. Install dependencies:")
    print("   pip install kaggle pandas pillow")
    print("\n3. Download and organize:")
    print("   python3 scripts/download_fer2013.py")
    print("\n4. Train (takes 2-6 hours):")
    print("   python3 models/train_model.py")
    print("\n" + "="*60)
    print("Option 2: Use Current Model (Quick Test)")
    print("="*60)
    print("\nYour current model might work better with the improvements we made:")
    print("- Lower confidence threshold (0.35)")
    print("- Better face detection")
    print("- More padding for emotion features")
    print("\nTest it first - it might be acceptable now.")
    print("\n" + "="*60)
    print("Option 3: Manual Model Search")
    print("="*60)
    print("\nIf you want to find a pre-trained model manually:")
    print("1. Search GitHub for 'FER2013 model keras'")
    print("2. Look for repositories with releases")
    print("3. Download .h5 or .keras files")
    print("4. Place in backend/models/emotion_model.keras")
    print("\n" + "="*60)
    
    print("\n💡 My recommendation:")
    print("   Start with Option 1 (FER2013 + train)")
    print("   It's the most reliable way to get a good model.")
    print("\n   While training, you can test Option 2 (current model)")
    print("   to see if improvements help.")

if __name__ == "__main__":
    main()


