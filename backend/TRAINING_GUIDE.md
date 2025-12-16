# Model Training Guide

## The Problem

Your current model is misclassifying emotions because:
1. **Insufficient training data** - The model needs hundreds/thousands of images per emotion
2. **Poor data quality** - Images need to be diverse (different people, lighting, angles)
3. **Label order mismatch** - The model might have been trained with different label order

## Finding Your Training Data

You mentioned you had a lot of images organized by emotion. Let's find them:

### Option 1: Search Your System
```bash
# Search for folders named after emotions
find ~ -type d -name "angry" -o -name "happy" -o -name "sad" 2>/dev/null | head -20

# Search for common dataset names
find ~ -type d -iname "*fer*" -o -iname "*emotion*" -o -iname "*face*" 2>/dev/null | head -20
```

### Option 2: Check Downloads/Desktop
The training data might be in:
- `~/Downloads/`
- `~/Desktop/`
- `~/Documents/`
- External drives

### Option 3: Check Where You Downloaded the Model
You said you got `test_faces` when downloading the model. The training data might be:
- In the same location as the model download
- In a separate archive/zip file
- In a parent directory

## Required Data Structure

Your training data should look like this:

```
your_dataset/
├── angry/
│   ├── img001.jpg
│   ├── img002.jpg
│   └── ... (hundreds of images)
├── disgust/
│   ├── img001.jpg
│   └── ...
├── fear/
├── happy/
├── neutral/
├── sad/
└── surprise/
```

**Minimum recommended:**
- **At least 500-1000 images per emotion** for decent accuracy
- **More is better** - 2000+ per emotion for production quality
- **Diverse images** - different people, lighting, expressions, angles

## Organizing Your Data

Once you find your data, use the organization script:

```bash
cd backend
python3 scripts/organize_training_data.py --source /path/to/your/emotion/folders
```

This will:
1. Copy images into `backend/data/train/` with proper structure
2. Show you how many images per emotion
3. Prepare for training

## Training the Model

### Step 1: Organize Data
```bash
python3 scripts/organize_training_data.py --source /path/to/your/data
```

### Step 2: Split into Train/Validation
```bash
python3 models/split_dataset.py
```
This creates `data/validation/` with 20% of your data.

### Step 3: Train
```bash
python3 models/train_model.py
```

**Training will:**
- Take 20 epochs (can take hours depending on data size)
- Save model to `models/emotion_model.keras`
- Show training/validation accuracy

### Step 4: Test
```bash
python3 scripts/batch_test.py --folder test_faces
```

## Improving Model Accuracy

### 1. More Data
- **Get more images** - Use datasets like FER2013, AffectNet, or collect your own
- **Balance classes** - Ensure similar number of images per emotion

### 2. Data Augmentation
Modify `models/train_model.py` to add augmentation:
```python
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True,
    zoom_range=0.2
)
```

### 3. Better Model Architecture
Consider:
- Deeper networks (more layers)
- Transfer learning (use pre-trained models)
- Larger input size (64x64 or 96x96 instead of 48x48)

### 4. Longer Training
- Increase epochs (30-50 instead of 20)
- Use learning rate scheduling
- Add early stopping

## Quick Check: Do You Have Enough Data?

Run this to check your current data:
```bash
python3 scripts/organize_training_data.py --scan
```

If it finds folders, it will show you how many images per emotion.

## Common Datasets

If you don't have enough data, consider:

1. **FER2013** - 35,887 grayscale 48x48 images
   - Download from: https://www.kaggle.com/datasets/msambare/fer2013

2. **AffectNet** - Large dataset (requires registration)
   - https:// AffectNet.org

3. **CK+** - Extended Cohn-Kanade Dataset
   - https://www.kaggle.com/datasets/shawon10/ckplus

## Next Steps

1. **Find your training data** - Search your system
2. **Organize it** - Use the script
3. **Check quantity** - Ensure 500+ images per emotion
4. **Retrain** - Run training script
5. **Test** - Verify accuracy improved


