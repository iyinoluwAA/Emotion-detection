# Fine-Tuning Guide - Fix Happy/Surprise Misclassification

## The Problem

The HardlyHumans ViT model (92.2% accuracy) is misclassifying:
- **Happy** → contempt/neutral (happy prob: 0.013-0.079)
- **Surprise** → contempt (surprise prob: 0.083, contempt: 0.507)

## Solution: Fine-Tune on FER2013

Fine-tune the model on FER2013 dataset (35,685 images) to improve happy/surprise detection.

## Step-by-Step Guide

### Step 1: Download FER2013 Dataset

1. Go to: https://www.kaggle.com/datasets/msambare/fer2013
2. Download `fer2013.csv` (or the full dataset)
3. Place it in: `backend/data/fer2013/fer2013.csv`

**Or use the download script:**
```bash
python3 backend/scripts/download_fer2013.py
```

### Step 2: Organize Data

Convert FER2013 CSV into folder structure:
```bash
python3 backend/scripts/finetune_vit_model.py --organize
```

This creates:
```
backend/data/train/
├── angry/
├── disgust/
├── fear/
├── happy/
├── neutral/
├── sad/
└── surprise/
```

### Step 3: Check Data

Verify you have enough images:
```bash
python3 backend/scripts/finetune_vit_model.py --check-data
```

You should see:
- ~28,000 training images (80% split)
- ~3,500 validation images (20% split)
- Balanced across emotions

### Step 4: Fine-Tune Model

**Requirements:**
- GPU recommended (Google Colab Pro, AWS, etc.)
- 2-4 hours training time
- 8GB+ RAM

**Start fine-tuning:**
```bash
python3 backend/scripts/finetune_vit_model.py --train --epochs 5 --batch-size 32
```

**Parameters:**
- `--epochs 5`: Number of training epochs (start with 5, increase if needed)
- `--batch-size 32`: Batch size (reduce if out of memory)
- `--lr 2e-5`: Learning rate (default is good)

### Step 5: Use Fine-Tuned Model

After training, update `backend/app/model_loader.py` to load the fine-tuned model:

```python
# In model_loader.py, change:
model_id = "HardlyHumans/Facial-expression-detection"
# To:
model_id = str(models_dir / "fine_tuned_vit")  # Local fine-tuned model
```

## Expected Results

After fine-tuning:
- ✅ Better happy detection (should be >0.5 probability for clear happy faces)
- ✅ Better surprise detection (should be >0.4 probability for clear surprise)
- ✅ Reduced contempt misclassifications
- ✅ Overall accuracy should improve or stay similar (92%+)

## Troubleshooting

### Out of Memory
- Reduce `--batch-size` to 16 or 8
- Use gradient accumulation
- Train on CPU (slower but works)

### Not Enough Data
- Download full FER2013 dataset
- Add more images from other sources
- Use data augmentation

### Training Too Slow
- Use GPU (Google Colab Pro: $10/month)
- Reduce epochs (try 3 first)
- Reduce batch size

## Alternative: Quick Test with Different Model

If fine-tuning is too complex, try a different model first:

```python
# In model_loader.py, try:
model_id = "prithivMLmods/Facial-Emotion-Detection-SigLIP2"
```

This might have better happy/surprise detection without fine-tuning.

## Next Steps

1. **Download FER2013** (if not already)
2. **Organize data** (`--organize`)
3. **Fine-tune** (`--train`)
4. **Test** with your happy/surprise images
5. **Deploy** fine-tuned model

## Resources

- FER2013: https://www.kaggle.com/datasets/msambare/fer2013
- Fine-tuning guide: https://huggingface.co/docs/transformers/training
- GPU access: Google Colab Pro ($10/month)


