#!/usr/bin/env python3
"""
Organize training data from emotion-labeled folders into the structure needed for training.

This script helps you:
1. Find emotion-labeled folders in your project
2. Organize them into data/train/ structure
3. Prepare for model retraining

Usage:
    python scripts/organize_training_data.py --source <path_to_emotion_folders>
    python scripts/organize_training_data.py --scan  # Just scan for existing folders
"""
import os
import sys
import shutil
import argparse
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAIN_DIR = PROJECT_ROOT / "data" / "train"
VAL_DIR = PROJECT_ROOT / "data" / "validation"

# Expected emotion labels (must match DEFAULT_LABELS in model_loader.py)
EXPECTED_EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

def scan_for_emotion_folders(root_path):
    """Scan for folders that might contain emotion-labeled images."""
    found = defaultdict(list)
    
    root = Path(root_path)
    if not root.exists():
        return found
    
    # Look for folders named after emotions
    for emotion in EXPECTED_EMOTIONS:
        # Check if there's a folder with this emotion name
        for path in root.rglob(emotion):
            if path.is_dir():
                image_count = len(list(path.glob("*.jpg")) + list(path.glob("*.jpeg")) + list(path.glob("*.png")))
                if image_count > 0:
                    found[emotion].append((str(path), image_count))
    
    # Also check for common dataset structures
    for path in root.rglob("*"):
        if path.is_dir():
            dir_name = path.name.lower()
            if any(emotion in dir_name for emotion in EXPECTED_EMOTIONS):
                image_count = len(list(path.glob("*.jpg")) + list(path.glob("*.jpeg")) + list(path.glob("*.png")))
                if image_count > 0:
                    for emotion in EXPECTED_EMOTIONS:
                        if emotion in dir_name:
                            found[emotion].append((str(path), image_count))
                            break
    
    return found

def organize_data(source_dir, target_train_dir, copy=True):
    """Organize source directory into train/ structure."""
    source = Path(source_dir)
    target = Path(target_train_dir)
    
    if not source.exists():
        print(f"❌ Source directory not found: {source}")
        return False
    
    target.mkdir(parents=True, exist_ok=True)
    
    organized = defaultdict(int)
    
    # Method 1: Source has emotion-named subdirectories
    for emotion in EXPECTED_EMOTIONS:
        emotion_source = source / emotion
        if emotion_source.exists() and emotion_source.is_dir():
            emotion_target = target / emotion
            emotion_target.mkdir(parents=True, exist_ok=True)
            
            # Copy/move images
            for img_file in emotion_source.glob("*.jpg"):
                if copy:
                    shutil.copy2(img_file, emotion_target / img_file.name)
                else:
                    shutil.move(str(img_file), str(emotion_target / img_file.name))
                organized[emotion] += 1
            
            for img_file in emotion_source.glob("*.jpeg"):
                if copy:
                    shutil.copy2(img_file, emotion_target / img_file.name)
                else:
                    shutil.move(str(img_file), str(emotion_target / img_file.name))
                organized[emotion] += 1
            
            for img_file in emotion_source.glob("*.png"):
                if copy:
                    shutil.copy2(img_file, emotion_target / img_file.name)
                else:
                    shutil.move(str(img_file), str(emotion_target / img_file.name))
                organized[emotion] += 1
    
    # Method 2: Source is a flat directory with emotion in filenames
    if sum(organized.values()) == 0:
        print("📁 No emotion subdirectories found. Checking for emotion-named files...")
        for img_file in source.glob("*.jpg"):
            for emotion in EXPECTED_EMOTIONS:
                if emotion.lower() in img_file.name.lower():
                    emotion_target = target / emotion
                    emotion_target.mkdir(parents=True, exist_ok=True)
                    if copy:
                        shutil.copy2(img_file, emotion_target / img_file.name)
                    else:
                        shutil.move(str(img_file), str(emotion_target / img_file.name))
                    organized[emotion] += 1
                    break
    
    # Print summary
    print("\n" + "="*60)
    print("ORGANIZATION SUMMARY")
    print("="*60)
    total = 0
    for emotion in EXPECTED_EMOTIONS:
        count = organized.get(emotion, 0)
        total += count
        status = "✅" if count > 0 else "❌"
        print(f"{status} {emotion:12s}: {count:4d} images")
    
    print(f"\nTotal images organized: {total}")
    
    if total == 0:
        print("\n⚠️  No images found. Check:")
        print("   1. Source directory path is correct")
        print("   2. Images are in emotion-named subfolders (angry/, happy/, etc.)")
        print("   3. Images have .jpg, .jpeg, or .png extensions")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Organize training data for emotion detection model")
    parser.add_argument("--source", type=str, help="Source directory with emotion-labeled folders")
    parser.add_argument("--scan", action="store_true", help="Just scan for emotion folders")
    parser.add_argument("--move", action="store_true", help="Move files instead of copying (default: copy)")
    
    args = parser.parse_args()
    
    if args.scan:
        print("🔍 Scanning for emotion-labeled folders...")
        print(f"Searching in: {PROJECT_ROOT}")
        found = scan_for_emotion_folders(PROJECT_ROOT)
        
        if not found:
            print("\n❌ No emotion-labeled folders found.")
            print("\n💡 Tips:")
            print("   - Your training data should be in folders named: angry/, happy/, sad/, etc.")
            print("   - Or provide --source <path> to specify where your data is")
            return
        
        print("\n📁 Found emotion folders:")
        for emotion, paths in found.items():
            print(f"\n{emotion.upper()}:")
            for path, count in paths:
                print(f"  - {path} ({count} images)")
    elif args.source:
        print(f"📦 Organizing data from: {args.source}")
        print(f"   To: {TRAIN_DIR}")
        success = organize_data(args.source, TRAIN_DIR, copy=not args.move)
        
        if success:
            print("\n✅ Data organized successfully!")
            print(f"\nNext steps:")
            print(f"1. Run: python models/split_dataset.py  # Create validation set")
            print(f"2. Run: python models/train_model.py     # Train the model")
        else:
            print("\n❌ Failed to organize data. Check the source directory structure.")
    else:
        parser.print_help()
        print("\n💡 Quick start:")
        print("   python scripts/organize_training_data.py --scan")
        print("   python scripts/organize_training_data.py --source /path/to/your/emotion/folders")

if __name__ == "__main__":
    main()


