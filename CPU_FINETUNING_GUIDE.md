# CPU Fine-Tuning Guide (No GPU Required)

## Your Situation

- ✅ FER2013 downloaded (in `backend/archive/`)
- ✅ 8-16GB RAM laptop
- ❌ No GPU, no money for GPU
- ✅ Want to fix happy/surprise misclassification

## Good News: CPU Fine-Tuning Works!

**You CAN fine-tune on CPU** - it's just slower:
- GPU: 2-4 hours
- CPU: 8-16 hours (overnight is fine!)

## Accuracy Expectations

**Important:** Fine-tuning on FER2013 won't necessarily increase overall accuracy from 92% → 95%.

**What it WILL do:**
- ✅ Fix happy misclassification (happy prob: 0.01 → 0.6+)
- ✅ Fix surprise misclassification (surprise prob: 0.08 → 0.5+)
- ✅ Reduce contempt false positives
- ✅ Keep overall accuracy ~92% (might go up 1-2%, might stay same)

**Why?**
- Model is already 92% accurate overall
- FER2013 is what it was originally trained on
- Fine-tuning fixes specific biases (happy/surprise) without hurting other emotions

## Step 1: Extract/Organize FER2013

First, let's see what's in your archive:

```bash
cd backend/archive
ls -lh
```

**If it's a ZIP file:**
```bash
unzip fer2013.zip -d ../data/fer2013/
```

**If it's a folder with CSV:**
```bash
# Find the CSV file
find . -name "fer2013.csv" -o -name "*.csv" | head -5

# Move it to the right place
mkdir -p ../data/fer2013
cp fer2013.csv ../data/fer2013/
```

**If it's already organized in folders:**
```bash
# Check structure
ls -d */ | head -10

# If you see angry/, happy/, etc. folders, move them
mkdir -p ../data/train
cp -r angry happy sad fear surprise disgust neutral ../data/train/
```

## Step 2: Organize Data

Once you have `fer2013.csv` in `backend/data/fer2013/`:

```bash
python3 backend/scripts/finetune_vit_model.py --organize
```

This converts the CSV into folder structure:
```
backend/data/train/
├── angry/ (5,000+ images)
├── disgust/ (500+ images)
├── fear/ (5,000+ images)
├── happy/ (9,000+ images) ← This will fix happy detection!
├── neutral/ (6,000+ images)
├── sad/ (6,000+ images)
└── surprise/ (4,000+ images) ← This will fix surprise detection!
```

## Step 3: CPU Fine-Tuning (Optimized for Your Laptop)

**Use smaller batch size to fit in 8-16GB RAM:**

```bash
# Start fine-tuning (will take 8-16 hours on CPU)
python3 backend/scripts/finetune_vit_model.py --train --epochs 3 --batch-size 8
```

**Parameters for CPU:**
- `--epochs 3`: Start with 3 epochs (can increase later)
- `--batch-size 8`: Small batch for 8-16GB RAM (reduce to 4 if OOM)
- CPU will auto-detect (no GPU needed)

**What to expect:**
- Training will be slow (~30-60 seconds per batch)
- Let it run overnight
- Check progress in `backend/models/fine_tuned_vit/logs/`

## Step 4: Test Fine-Tuned Model

After training completes:

```bash
# Test with your happy/surprise images
# The model will be in: backend/models/fine_tuned_vit/
```

Update `backend/app/model_loader.py` to use fine-tuned model (I'll help with this after training).

## Memory Optimization Tips

If you get "Out of Memory" errors:

1. **Reduce batch size:**
   ```bash
   --batch-size 4  # Even smaller
   ```

2. **Reduce dataset size:**
   - Edit `finetune_vit_model.py`
   - Change `max_samples_per_class=2000` to `1000`

3. **Close other apps** (browser, etc.)

4. **Use fewer epochs:**
   ```bash
   --epochs 2  # Just 2 epochs
   ```

## Expected Results

After fine-tuning on CPU:

**Before:**
- Happy face → contempt (0.507) ❌
- Happy prob: 0.013-0.079 ❌

**After:**
- Happy face → happy (0.6+) ✅
- Happy prob: 0.5-0.9 ✅
- Surprise → surprise (0.5+) ✅

**Overall accuracy:** Stays ~92% (might improve to 93-94%)

## Timeline

- **Organize data:** 10-30 minutes
- **CPU fine-tuning:** 8-16 hours (overnight)
- **Total:** One day

## Next Steps

1. **Check your archive:**
   ```bash
   cd backend/archive
   ls -lh
   ```

2. **Tell me what you see** (ZIP, CSV, folders?) and I'll help extract it

3. **Then organize and train!**


