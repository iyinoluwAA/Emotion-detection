# Install Dependencies for Fine-Tuning

## The Problem

PyTorch and other dependencies need to be installed for fine-tuning, but the automated installation isn't working.

## Manual Installation Steps

### Step 1: Install PyTorch (CPU version - smaller, faster)

Run this command in your terminal:

```bash
cd /home/iyino/projects/Emotion-detection
python3 -m pip install --user --break-system-packages torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**This will:**
- Install CPU-only PyTorch (smaller, ~500MB vs 2GB)
- Take 5-10 minutes
- Work fine for CPU fine-tuning

### Step 2: Install Other Dependencies

```bash
python3 -m pip install --user --break-system-packages transformers scikit-learn pandas
```

### Step 3: Verify Installation

```bash
python3 -c "import torch; print('✅ PyTorch:', torch.__version__)"
python3 -c "import transformers; print('✅ Transformers:', transformers.__version__)"
```

### Step 4: Start Fine-Tuning

Once all dependencies are installed:

```bash
python3 backend/scripts/finetune_vit_model.py --train --epochs 3 --batch-size 8
```

## Alternative: Use Docker/Backend Environment

If your backend already has torch installed (for the ViT model), we could:
1. Run fine-tuning inside the Docker container
2. Or use the backend's Python environment

Let me know which approach you prefer!

## Troubleshooting

**If installation fails:**
- Check internet connection
- Try: `pip3 install --upgrade pip`
- Try: `python3 -m pip install --user torch` (without --break-system-packages)

**If "externally-managed-environment" error:**
- Use `--break-system-packages` flag (already in commands above)
- Or create a virtual environment


