#!/usr/bin/env python3
"""
Move FER2013 data from archive/ to data/ for fine-tuning.

Your archive is already organized in train/ and test/ folders!
This script just moves it to the right location.
"""

import shutil
from pathlib import Path

def setup_fer2013():
    """Move archive/train and archive/test to data/"""
    repo_root = Path(__file__).parent.parent.parent
    archive_dir = repo_root / "backend" / "archive"
    data_dir = repo_root / "backend" / "data"
    
    archive_train = archive_dir / "train"
    archive_test = archive_dir / "test"
    
    data_train = data_dir / "train"
    data_test = data_dir / "test"
    
    if not archive_train.exists():
        print(f"❌ Archive train folder not found: {archive_train}")
        return False
    
    print(f"📁 Found archive:")
    print(f"   Train: {archive_train}")
    print(f"   Test: {archive_test}")
    
    # Check what emotions we have
    print(f"\n📊 Checking emotions in train folder...")
    emotions = [d.name for d in archive_train.iterdir() if d.is_dir()]
    for emotion in sorted(emotions):
        count = len(list((archive_train / emotion).glob("*.jpg")))
        print(f"   {emotion}: {count} images")
    
    # Create data directories
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy train data
    print(f"\n📦 Copying train data to {data_train}...")
    if data_train.exists():
        print(f"   ⚠️  {data_train} already exists. Skipping...")
    else:
        shutil.copytree(archive_train, data_train)
        print(f"   ✅ Copied {len(list(data_train.rglob('*.jpg')))} images")
    
    # Copy test data (optional, for validation)
    if archive_test.exists():
        print(f"\n📦 Copying test data to {data_test}...")
        if data_test.exists():
            print(f"   ⚠️  {data_test} already exists. Skipping...")
        else:
            shutil.copytree(archive_test, data_test)
            print(f"   ✅ Copied {len(list(data_test.rglob('*.jpg')))} images")
    
    print(f"\n✅ Setup complete!")
    print(f"   Train data: {data_train}")
    print(f"   Test data: {data_test}")
    print(f"\n🚀 Ready to fine-tune! Run:")
    print(f"   python3 backend/scripts/finetune_vit_model.py --train --epochs 3 --batch-size 8")
    
    return True

if __name__ == "__main__":
    setup_fer2013()


