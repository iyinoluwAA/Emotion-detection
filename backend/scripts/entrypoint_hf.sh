#!/bin/sh
set -eu

# Where the app expects the model inside the container
MODEL_PATH="/app/models/emotion_model.keras"

# Public release URL (change if you host elsewhere)
MODEL_URL="https://github.com/iyinoluwAA/Emotion-detection/releases/download/v1.0.0/emotion_model.keras"

# Ensure models dir exists
mkdir -p "$(dirname "$MODEL_PATH")"

if [ ! -f "$MODEL_PATH" ]; then
  echo "Model not found at $MODEL_PATH — attempting download from $MODEL_URL"
  if command -v curl >/dev/null 2>&1; then
    curl -fSL "$MODEL_URL" -o "$MODEL_PATH" || {
      echo "curl failed to download model"; ls -la "$(dirname "$MODEL_PATH")"; exit 1;
    }
  elif command -v wget >/dev/null 2>&1; then
    wget -O "$MODEL_PATH" "$MODEL_URL" || {
      echo "wget failed to download model"; ls -la "$(dirname "$MODEL_PATH")"; exit 1;
    }
  else
    echo "No curl or wget available in the image. Install one in Dockerfile."; exit 1
  fi
else
  echo "Model already present at $MODEL_PATH"
fi

# ensure readable
chmod a+r "$MODEL_PATH" || true

# Download Asripa model (fine-tuned) if not present
ASRIPA_MODEL_DIR="/app/models/fine_tuned_vit"
ASRIPA_MODEL_ID="${ASRIPA_MODEL_ID:-HimAJ/asripa-emotion-detection}"

if [ -n "$ASRIPA_MODEL_ID" ] && [ ! -f "$ASRIPA_MODEL_DIR/model.safetensors" ]; then
  echo "📥 Downloading Asripa model from HuggingFace..."
  echo "   Model ID: $ASRIPA_MODEL_ID"
  mkdir -p "$ASRIPA_MODEL_DIR"
  
  # Use Python to download (huggingface_hub is in requirements)
  python3 -c "
from huggingface_hub import snapshot_download
import os
import sys
try:
    snapshot_download(
        repo_id='$ASRIPA_MODEL_ID',
        local_dir='$ASRIPA_MODEL_DIR',
        local_dir_use_symlinks=False
    )
    print('✅ Asripa model downloaded successfully!')
except Exception as e:
    print(f'⚠️  Failed to download Asripa model: {e}')
    print('   App will use base model only')
    import shutil
    if os.path.exists('$ASRIPA_MODEL_DIR'):
        shutil.rmtree('$ASRIPA_MODEL_DIR')
    sys.exit(0)  # Exit gracefully, not an error
" || {
    echo "⚠️  Asripa model download skipped"
    echo "   App will use base model only"
    rm -rf "$ASRIPA_MODEL_DIR" 2>/dev/null || true
  }
elif [ -f "$ASRIPA_MODEL_DIR/model.safetensors" ]; then
  echo "✅ Asripa model already present"
elif [ -z "$ASRIPA_MODEL_ID" ]; then
  echo "ℹ️  ASRIPA_MODEL_ID not set - skipping Asripa model download"
fi

# Hugging Face Spaces uses port 7860 by default
# But we'll use PORT env var if set, otherwise default to 7860
PORT="${PORT:-7860}"
echo "Starting gunicorn on 0.0.0.0:${PORT}"
# Suppress protobuf warnings
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
exec gunicorn main:app --bind 0.0.0.0:"${PORT}" --workers 1 --threads 1 --timeout 120 --worker-class gthread

