#!/usr/bin/env python3
"""
Download and organize FER2013 dataset from Kaggle.

FER2013 is the most popular emotion detection dataset:
- 35,887 grayscale 48x48 images
- 7 emotions: angry, disgust, fear, happy, neutral, sad, surprise
- Already split into train/test sets

Requirements:
1. Kaggle account (free)
2. Kaggle API token (kaggle.json in ~/.kaggle/)
   - Get from: https://www.kaggle.com/settings -> API -> Create New Token

Usage:
    python scripts/download_fer2013.py
"""
import os
import sys
import json
import zipfile
import shutil
from pathlib import Path
import pandas as pd
import numpy as np
from PIL import Image
import io

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
TRAIN_DIR = DATA_DIR / "train"
VAL_DIR = DATA_DIR / "validation"
FER2013_DIR = DATA_DIR / "fer2013"

# Emotion mapping (FER2013 uses 0-6, we use emotion names)
EMOTION_MAP = {
    0: 'angry',
    1: 'disgust',
    2: 'fear',
    3: 'happy',
    4: 'neutral',
    5: 'sad',
    6: 'surprise'
}

def check_kaggle():
    """Check if Kaggle API is available."""
    try:
        import kaggle
        return True
    except ImportError:
        print("❌ Kaggle API not installed.")
        print("\nInstall it with:")
        print("  pip install kaggle")
        return False

def check_kaggle_credentials():
    """Check if Kaggle credentials are set up."""
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_json = kaggle_dir / "kaggle.json"
    
    if not kaggle_json.exists():
        print("❌ Kaggle credentials not found.")
        print(f"\nExpected location: {kaggle_json}")
        print("\nTo set up:")
        print("1. Go to https://www.kaggle.com/settings")
        print("2. Scroll to 'API' section")
        print("3. Click 'Create New Token'")
        print("4. Save kaggle.json to ~/.kaggle/")
        print("5. Run: chmod 600 ~/.kaggle/kaggle.json")
        return False
    
    return True

def download_fer2013():
    """Download FER2013 dataset from Kaggle."""
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        
        print("📥 Downloading FER2013 dataset from Kaggle...")
        print("   This may take a few minutes (~90MB)...")
        
        # Download dataset
        api.dataset_download_files(
            'msambare/fer2013',
            path=str(FER2013_DIR),
            unzip=True
        )
        
        print("✅ Download complete!")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        print("\nAlternative: Download manually from:")
        print("  https://www.kaggle.com/datasets/msambare/fer2013")
        print("  Then extract to: backend/data/fer2013/")
        return False

def organize_fer2013():
    """Organize FER2013 CSV into folder structure."""
    csv_path = FER2013_DIR / "fer2013.csv"
    
    if not csv_path.exists():
        print(f"❌ FER2013 CSV not found: {csv_path}")
        print("\nThe dataset should contain fer2013.csv")
        return False
    
    print("📁 Organizing FER2013 data into folder structure...")
    
    # Create emotion directories
    for emotion in EMOTION_MAP.values():
        (TRAIN_DIR / emotion).mkdir(parents=True, exist_ok=True)
        (VAL_DIR / emotion).mkdir(parents=True, exist_ok=True)
    
    # Read CSV
    df = pd.read_csv(csv_path)
    
    # Process each row
    train_count = {emotion: 0 for emotion in EMOTION_MAP.values()}
    val_count = {emotion: 0 for emotion in EMOTION_MAP.values()}
    
    for idx, row in df.iterrows():
        emotion_id = int(row['emotion'])
        emotion_name = EMOTION_MAP[emotion_id]
        usage = row['Usage']  # 'Training', 'PublicTest', 'PrivateTest'
        pixels = row['pixels']
        
        # Convert pixel string to image
        pixel_array = np.array([int(p) for p in pixels.split()], dtype=np.uint8)
        pixel_array = pixel_array.reshape(48, 48)
        image = Image.fromarray(pixel_array, mode='L')
        
        # Determine destination
        if usage == 'Training':
            dest_dir = TRAIN_DIR / emotion_name
            train_count[emotion_name] += 1
            filename = f"train_{train_count[emotion_name]:06d}.jpg"
        else:  # PublicTest or PrivateTest -> validation
            dest_dir = VAL_DIR / emotion_name
            val_count[emotion_name] += 1
            filename = f"val_{val_count[emotion_name]:06d}.jpg"
        
        # Save image
        image.save(dest_dir / filename)
        
        if (idx + 1) % 5000 == 0:
            print(f"  Processed {idx + 1}/{len(df)} images...")
    
    print("\n✅ Organization complete!")
    print("\n📊 Dataset Summary:")
    print("\nTraining set:")
    for emotion, count in train_count.items():
        print(f"  {emotion:12s}: {count:5d} images")
    
    print("\nValidation set:")
    for emotion, count in val_count.items():
        print(f"  {emotion:12s}: {count:5d} images")
    
    total_train = sum(train_count.values())
    total_val = sum(val_count.values())
    print(f"\nTotal: {total_train + total_val:,} images")
    
    return True

def main():
    print("="*60)
    print("FER2013 Dataset Downloader")
    print("="*60)
    
    # Check prerequisites
    if not check_kaggle():
        return
    
    if not check_kaggle_credentials():
        return
    
    # Download
    if not download_fer2013():
        # Check if already downloaded
        csv_path = FER2013_DIR / "fer2013.csv"
        if not csv_path.exists():
            print("\n💡 You can download manually and place fer2013.csv in:")
            print(f"   {FER2013_DIR}/")
            return
    
    # Organize
    if organize_fer2013():
        print("\n✅ FER2013 dataset ready for training!")
        print("\nNext steps:")
        print("1. Review the dataset summary above")
        print("2. Run: python models/train_model.py")
        print("\nNote: Training will take several hours. Consider using GPU if available.")

if __name__ == "__main__":
    main()


