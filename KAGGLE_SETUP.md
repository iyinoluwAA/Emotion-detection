# Kaggle API Setup - Download FER2013

## Quick Setup (3 Steps)

### Step 1: Install Kaggle CLI

```bash
pip3 install --user kaggle
```

If you get "command not found" after install, add to PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Step 2: Set Up Authentication

You already have a Legacy API Key. Here's how to use it:

**Option A: Use Existing Legacy API Key**
1. Go to: https://www.kaggle.com/settings
2. Find your "Legacy Api Key" section
3. Click "Download" or copy the credentials
4. Create `~/.kaggle/kaggle.json`:

```bash
mkdir -p ~/.kaggle
cat > ~/.kaggle/kaggle.json << EOF
{
  "username": "YOUR_USERNAME",
  "key": "YOUR_API_KEY"
}
EOF
chmod 600 ~/.kaggle/kaggle.json
```

**Option B: Create New Token (Recommended)**
1. Go to: https://www.kaggle.com/settings
2. Click "Create New Token" (under API Tokens)
3. Download `kaggle.json`
4. Move it:

```bash
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### Step 3: Download FER2013

**Easy way (using script):**
```bash
cd /home/iyino/projects/Emotion-detection
./backend/scripts/download_fer2013_kaggle.sh
```

**Manual way:**
```bash
kaggle datasets download msambare/fer2013 -p backend/data/fer2013_download
cd backend/data/fer2013_download
unzip fer2013.zip
```

## Verify Authentication

Test if it works:
```bash
kaggle datasets list -s fer2013
```

You should see FER2013 in the results.

## What You'll Get

After download, you'll have:
- `fer2013.csv` (or `train/` and `test/` folders)
- ~35,000 images total
- All 7 emotions (angry, disgust, fear, happy, neutral, sad, surprise)

## Next Steps After Download

1. **If you got CSV:**
   ```bash
   python3 backend/scripts/finetune_vit_model.py --organize
   ```

2. **If you got train/test folders:**
   ```bash
   python3 backend/scripts/setup_fer2013_from_archive.py
   ```

3. **Then fine-tune:**
   ```bash
   python3 backend/scripts/finetune_vit_model.py --train --epochs 3 --batch-size 8
   ```

## Troubleshooting

### "kaggle: command not found"
```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or use full path
~/.local/bin/kaggle datasets download msambare/fer2013
```

### "403 - Forbidden" or "401 - Unauthorized"
- Check `~/.kaggle/kaggle.json` exists
- Check permissions: `chmod 600 ~/.kaggle/kaggle.json`
- Verify username/key are correct

### "Dataset not found"
- Make sure you accepted the dataset rules on Kaggle website
- Visit: https://www.kaggle.com/datasets/msambare/fer2013
- Click "Download" button (even if you don't download, this accepts rules)

## Ready?

Run the download script:
```bash
./backend/scripts/download_fer2013_kaggle.sh
```


