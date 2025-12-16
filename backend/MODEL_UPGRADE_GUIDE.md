# Model Upgrade Guide

## The Problem

Your current model is misclassifying emotions because it was trained with insufficient or poor-quality data. You've lost the original training dataset.

## Solution Options

### Option 1: Use a Better Pre-trained Model (RECOMMENDED - Fastest)

**Why this is best:**
- ✅ **Fast** - No training needed (5-10 minutes)
- ✅ **Better accuracy** - Trained on large, quality datasets
- ✅ **Production-ready** - Already tested and optimized

**Steps:**

1. **Install dependencies:**
   ```bash
   cd backend
   source .venv/bin/activate
   pip install huggingface_hub
   ```

2. **Download better model:**
   ```bash
   python3 scripts/download_pretrained_model.py
   ```
   Choose option 1 (Emo0.1) - it's VGG16-based and more accurate.

3. **Test it:**
   ```bash
   python3 main.py
   ```
   Then test with your images. Accuracy should be much better.

**Models available:**
- **Emo0.1** (HuggingFace) - VGG16-based, ~70-80% accuracy
- **GitHub models** - Various pre-trained models

---

### Option 2: Download FER2013 Dataset and Retrain (Better Long-term)

**Why this is good:**
- ✅ **Full control** - You can fine-tune for your specific use case
- ✅ **Latest data** - FER2013 is the gold standard (35,887 images)
- ✅ **Learning experience** - Understand the training process

**Steps:**

1. **Set up Kaggle API:**
   - Create account at https://www.kaggle.com (free)
   - Go to Settings → API → Create New Token
   - Save `kaggle.json` to `~/.kaggle/`
   - Run: `chmod 600 ~/.kaggle/kaggle.json`

2. **Install Kaggle:**
   ```bash
   pip install kaggle pandas pillow
   ```

3. **Download and organize FER2013:**
   ```bash
   python3 scripts/download_fer2013.py
   ```
   This will:
   - Download ~90MB dataset from Kaggle
   - Organize into `data/train/` and `data/validation/`
   - Show you dataset statistics

4. **Train the model:**
   ```bash
   python3 models/train_model.py
   ```
   **Note:** This takes **several hours** (2-6 hours depending on CPU/GPU)

5. **Test:**
   ```bash
   python3 scripts/batch_test.py --folder test_faces
   ```

---

### Option 3: Hybrid Approach (Best of Both)

1. **Start with pre-trained model** (Option 1) - Get it working quickly
2. **Download FER2013** (Option 2) - For future improvements
3. **Fine-tune pre-trained model** on FER2013 - Best accuracy

---

## Comparison

| Approach | Time | Accuracy | Difficulty |
|----------|------|----------|------------|
| Pre-trained model | 5-10 min | 70-80% | Easy ⭐ |
| Retrain on FER2013 | 2-6 hours | 60-70% | Medium ⭐⭐ |
| Fine-tune pre-trained | 1-3 hours | 75-85% | Medium ⭐⭐ |

---

## My Recommendation

**Start with Option 1 (Pre-trained model):**
1. It's the fastest way to fix your accuracy issues
2. You can always retrain later if needed
3. Emo0.1 is well-tested and production-ready

**Then consider Option 2 if:**
- You need even better accuracy
- You want to customize for specific use cases
- You have time to wait for training

---

## Quick Start (Pre-trained Model)

```bash
cd backend
source .venv/bin/activate
pip install huggingface_hub
python3 scripts/download_pretrained_model.py
# Choose option 1
python3 main.py
```

Test with your images - accuracy should be much better!

---

## Troubleshooting

### "Kaggle API not found"
- Install: `pip install kaggle`
- Set up credentials (see Option 2, step 1)

### "huggingface_hub not found"
- Install: `pip install huggingface_hub`

### Model still misclassifying
- Try a different pre-trained model
- Consider retraining with FER2013
- Check if label order matches (should be same 7 emotions)

### Training takes too long
- Use GPU if available (much faster)
- Reduce epochs (but lower accuracy)
- Use pre-trained model instead

---

## Next Steps After Upgrading

1. **Test thoroughly** - Try various images, especially the ones that were misclassified
2. **Monitor accuracy** - Check if surprise is now correctly detected
3. **Fine-tune if needed** - If still not perfect, fine-tune on FER2013
4. **Deploy** - Once satisfied, push to production


