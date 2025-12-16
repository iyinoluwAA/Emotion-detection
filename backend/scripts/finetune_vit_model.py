#!/usr/bin/env python3
"""
Fine-tune HardlyHumans ViT model on FER2013 dataset to improve happy/surprise detection.

This script:
1. Downloads FER2013 dataset (if not present)
2. Organizes it into emotion folders
3. Fine-tunes the ViT model
4. Saves fine-tuned model
"""

import os
import sys
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def check_fer2013_data():
    """Check if FER2013 data exists."""
    repo_root = Path(__file__).parent.parent.parent
    fer2013_dir = repo_root / "backend" / "data" / "fer2013"
    csv_path = fer2013_dir / "fer2013.csv"
    
    if csv_path.exists():
        print(f"✅ FER2013 CSV found: {csv_path}")
        return True
    else:
        print(f"❌ FER2013 CSV not found: {csv_path}")
        print("\n📥 To download FER2013:")
        print("   1. Go to: https://www.kaggle.com/datasets/msambare/fer2013")
        print("   2. Download fer2013.csv")
        print("   3. Place it in: backend/data/fer2013/fer2013.csv")
        return False

def organize_fer2013():
    """Organize FER2013 CSV into folder structure for fine-tuning."""
    from backend.scripts.download_fer2013 import organize_fer2013 as org_func
    return org_func()

def fine_tune_model(epochs=5, batch_size=32, learning_rate=2e-5):
    """
    Fine-tune the ViT model on FER2013 data.
    
    Args:
        epochs: Number of training epochs
        batch_size: Batch size for training
        learning_rate: Learning rate for fine-tuning
    """
    try:
        import torch
        from torch.utils.data import DataLoader, Dataset
        from transformers import AutoImageProcessor, AutoModelForImageClassification, TrainingArguments, Trainer
        from PIL import Image
        import pandas as pd
        import numpy as np
        from pathlib import Path
        from sklearn.model_selection import train_test_split
        import accelerate  # Required for Trainer
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip install torch transformers scikit-learn pandas pillow accelerate")
        return False
    
    repo_root = Path(__file__).parent.parent.parent
    train_dir = repo_root / "backend" / "data" / "train"
    
    if not train_dir.exists():
        print(f"❌ Training data not found: {train_dir}")
        print("Run: python3 backend/scripts/download_fer2013.py --organize")
        return False
    
    # Check if we have enough data
    emotion_counts = {}
    for emotion_dir in train_dir.iterdir():
        if emotion_dir.is_dir():
            count = len(list(emotion_dir.glob("*.jpg")))
            emotion_counts[emotion_dir.name] = count
            print(f"  {emotion_dir.name}: {count} images")
    
    total_images = sum(emotion_counts.values())
    if total_images < 1000:
        print(f"⚠️  Warning: Only {total_images} images found. Need at least 1000 for fine-tuning.")
        return False
    
    print(f"\n✅ Found {total_images} training images")
    
    # Load model and processor
    model_id = "HardlyHumans/Facial-expression-detection"
    print(f"\n📥 Loading model: {model_id}")
    
    processor = AutoImageProcessor.from_pretrained(model_id)
    model = AutoModelForImageClassification.from_pretrained(model_id)
    
    # Create dataset class
    class EmotionDataset(Dataset):
        def __init__(self, data_dir, processor, max_samples_per_class=2000):
            self.processor = processor
            self.images = []
            self.labels = []
            
            # Map emotion names to model's label IDs
            emotion_to_id = {
                'angry': 0,
                'contempt': 1,  # Model has contempt, FER2013 doesn't - we'll skip or map
                'disgust': 2,
                'fear': 3,
                'happy': 4,
                'neutral': 5,
                'sad': 6,
                'surprise': 7
            }
            
            # FER2013 emotions: angry, disgust, fear, happy, neutral, sad, surprise
            # Model emotions: anger, contempt, disgust, fear, happy, neutral, sad, surprise
            fer_to_model = {
                'angry': 'anger',  # Model uses 'anger', not 'angry'
                'disgust': 'disgust',
                'fear': 'fear',
                'happy': 'happy',
                'neutral': 'neutral',
                'sad': 'sad',
                'surprise': 'surprise'
            }
            
            # Get model's label mapping
            model_labels = [model.config.id2label[i] for i in range(len(model.config.id2label))]
            print(f"Model labels: {model_labels}")
            
            # Build dataset
            for emotion_name in ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']:
                emotion_dir = data_dir / emotion_name
                if not emotion_dir.exists():
                    continue
                
                # Map FER2013 emotion to model emotion
                model_emotion = fer_to_model.get(emotion_name, emotion_name)
                
                # Find label ID in model
                label_id = None
                for i, label in enumerate(model_labels):
                    if label.lower() == model_emotion.lower() or \
                       (model_emotion == 'anger' and 'anger' in label.lower()):
                        label_id = i
                        break
                
                if label_id is None:
                    print(f"⚠️  Warning: Could not map {emotion_name} to model label")
                    continue
                
                # Collect images
                image_files = list(emotion_dir.glob("*.jpg"))[:max_samples_per_class]
                for img_file in image_files:
                    self.images.append(str(img_file))
                    self.labels.append(label_id)
            
            print(f"\n📊 Dataset: {len(self.images)} images, {len(set(self.labels))} classes")
        
        def __len__(self):
            return len(self.images)
        
        def __getitem__(self, idx):
            image = Image.open(self.images[idx]).convert('RGB')
            inputs = self.processor(image, return_tensors="pt")
            return {
                'pixel_values': inputs['pixel_values'].squeeze(),
                'labels': torch.tensor(self.labels[idx], dtype=torch.long)
            }
    
    # Create datasets
    print("\n📁 Creating datasets...")
    full_dataset = EmotionDataset(train_dir, processor)
    
    # Split train/val
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        full_dataset, [train_size, val_size]
    )
    
    print(f"  Train: {len(train_dataset)} images")
    print(f"  Val: {len(val_dataset)} images")
    
    # Training arguments
    output_dir = repo_root / "backend" / "models" / "fine_tuned_vit"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check for existing checkpoints to resume
    checkpoints = sorted([d for d in output_dir.iterdir() if d.is_dir() and d.name.startswith("checkpoint-")])
    resume_from_checkpoint = None
    if checkpoints:
        resume_from_checkpoint = str(checkpoints[-1])  # Resume from latest checkpoint
        print(f"📂 Found checkpoint: {checkpoints[-1].name}")
        print(f"   Resuming training from epoch {len(checkpoints)}...")
    
    # Compute metrics function for accuracy
    import numpy as np
    from sklearn.metrics import accuracy_score
    
    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        accuracy = accuracy_score(labels, predictions)
        return {"accuracy": accuracy}
    
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        weight_decay=0.01,
        logging_dir=str(output_dir / "logs"),
        logging_steps=100,
        eval_strategy="epoch",  # Evaluate at end of each epoch
        save_strategy="steps",  # Save checkpoints more frequently (every N steps)
        save_steps=200,  # Save checkpoint every 200 steps (~2-3 hours of progress)
        save_total_limit=3,  # Keep only last 3 checkpoints to save disk space
        load_best_model_at_end=False,  # Can't use with mismatched save/eval strategies, but we save frequently anyway
        metric_for_best_model="eval_accuracy",  # For reference (even if not loading best)
        greater_is_better=True,
        # CPU optimization - reduce memory usage
        dataloader_num_workers=0,  # Disable multiprocessing on CPU
        fp16=False,  # No mixed precision on CPU
        no_cuda=True,  # Force CPU (if no GPU available)
    )
    
    # Trainer
    from transformers import Trainer, TrainingArguments
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,  # Add accuracy computation
    )
    
    print(f"\n🚀 Starting fine-tuning for {epochs} epochs...")
    print(f"   Batch size: {batch_size}")
    print(f"   Learning rate: {learning_rate}")
    print(f"   Output: {output_dir}")
    if resume_from_checkpoint:
        print(f"   Resuming from: {resume_from_checkpoint}")
    
    trainer.train(resume_from_checkpoint=resume_from_checkpoint)
    
    # Save model
    print(f"\n💾 Saving fine-tuned model...")
    model.save_pretrained(str(output_dir))
    processor.save_pretrained(str(output_dir))
    
    print(f"\n✅ Fine-tuning complete!")
    print(f"   Model saved to: {output_dir}")
    print(f"\n📝 To use the fine-tuned model:")
    print(f"   Update model_loader.py to load from: {output_dir}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Fine-tune ViT model on FER2013")
    parser.add_argument("--check-data", action="store_true", help="Check if FER2013 data exists")
    parser.add_argument("--organize", action="store_true", help="Organize FER2013 CSV into folders")
    parser.add_argument("--train", action="store_true", help="Start fine-tuning")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate")
    
    args = parser.parse_args()
    
    if args.check_data:
        check_fer2013_data()
    elif args.organize:
        if not check_fer2013_data():
            return
        organize_fer2013()
    elif args.train:
        fine_tune_model(epochs=args.epochs, batch_size=args.batch_size, learning_rate=args.lr)
    else:
        print("Usage:")
        print("  python3 backend/scripts/finetune_vit_model.py --check-data")
        print("  python3 backend/scripts/finetune_vit_model.py --organize")
        print("  python3 backend/scripts/finetune_vit_model.py --train --epochs 5")

if __name__ == "__main__":
    main()

