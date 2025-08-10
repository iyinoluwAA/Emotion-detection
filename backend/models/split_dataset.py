import os
import shutil
import random
from pathlib import Path

# Paths
base_path = Path(__file__).resolve().parent.parent
train_dir = base_path / "data" / "train"
val_dir = base_path / "data" / "validation"
split_ratio = 0.2  # 20% validation

# Create validation directory
val_dir.mkdir(parents=True, exist_ok=True)

for class_name in os.listdir(train_dir):
    class_train_dir = train_dir / class_name
    class_val_dir = val_dir / class_name

    if not class_train_dir.is_dir():
        continue

    class_val_dir.mkdir(parents=True, exist_ok=True)

    images = os.listdir(class_train_dir)
    random.shuffle(images)

    split_count = int(len(images) * split_ratio)
    val_images = images[:split_count]

    for img in val_images:
        src_path = class_train_dir / img
        dst_path = class_val_dir / img
        shutil.move(str(src_path), str(dst_path))

print("✅ Split complete: validation set created.")
