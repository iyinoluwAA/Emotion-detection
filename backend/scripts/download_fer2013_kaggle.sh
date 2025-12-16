#!/bin/bash
# Download FER2013 dataset using Kaggle API

set -e

echo "📥 Downloading FER2013 dataset from Kaggle..."

# Check if kaggle is installed
if ! command -v kaggle &> /dev/null; then
    echo "❌ Kaggle CLI not found. Installing..."
    pip3 install --user kaggle
    echo "✅ Kaggle CLI installed"
    echo ""
    echo "⚠️  IMPORTANT: You need to set up authentication:"
    echo "   1. Download kaggle.json from: https://www.kaggle.com/settings -> API -> Create New Token"
    echo "   2. Place it in: ~/.kaggle/kaggle.json"
    echo "   3. Run: chmod 600 ~/.kaggle/kaggle.json"
    echo ""
    exit 1
fi

# Check if kaggle.json exists
if [ ! -f ~/.kaggle/kaggle.json ]; then
    echo "❌ Kaggle authentication not found!"
    echo ""
    echo "📝 Setup steps:"
    echo "   1. Go to: https://www.kaggle.com/settings"
    echo "   2. Click 'Create New Token' (or use existing Legacy API Key)"
    echo "   3. Download kaggle.json"
    echo "   4. Run these commands:"
    echo "      mkdir -p ~/.kaggle"
    echo "      mv ~/Downloads/kaggle.json ~/.kaggle/"
    echo "      chmod 600 ~/.kaggle/kaggle.json"
    echo ""
    exit 1
fi

# Set permissions
chmod 600 ~/.kaggle/kaggle.json 2>/dev/null || true

# Create download directory
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DOWNLOAD_DIR="$REPO_ROOT/backend/data/fer2013_download"
mkdir -p "$DOWNLOAD_DIR"

echo "📦 Downloading to: $DOWNLOAD_DIR"
cd "$DOWNLOAD_DIR"

# Download dataset
echo "⏳ Downloading FER2013 dataset (this may take a few minutes)..."
kaggle datasets download msambare/fer2013 -p "$DOWNLOAD_DIR"

# Check what was downloaded
echo ""
echo "📁 Files downloaded:"
ls -lh "$DOWNLOAD_DIR"

# Extract if it's a zip file
if [ -f "$DOWNLOAD_DIR/fer2013.zip" ]; then
    echo ""
    echo "📦 Extracting fer2013.zip..."
    unzip -q "$DOWNLOAD_DIR/fer2013.zip" -d "$DOWNLOAD_DIR"
    echo "✅ Extracted!"
fi

# Check for CSV file
if [ -f "$DOWNLOAD_DIR/fer2013.csv" ]; then
    echo ""
    echo "✅ Found fer2013.csv!"
    echo "   Size: $(du -h "$DOWNLOAD_DIR/fer2013.csv" | cut -f1)"
    echo ""
    echo "📝 Next step: Organize the data"
    echo "   python3 backend/scripts/finetune_vit_model.py --organize"
fi

# Check for train/test folders
if [ -d "$DOWNLOAD_DIR/train" ]; then
    echo ""
    echo "✅ Found train/ folder!"
    echo "   Checking emotions..."
    cd "$DOWNLOAD_DIR/train"
    for dir in */; do
        count=$(find "$dir" -type f 2>/dev/null | wc -l)
        echo "   ${dir%/}: $count images"
    done
    echo ""
    echo "📝 Next step: Move to data folder"
    echo "   python3 backend/scripts/setup_fer2013_from_archive.py"
fi

echo ""
echo "✅ Download complete!"
echo "   Location: $DOWNLOAD_DIR"


