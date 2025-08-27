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

# Start gunicorn bound to Render-provided $PORT (fallback to 5000 locally)
PORT="${PORT:-5000}"
echo "Starting gunicorn on 0.0.0.0:${PORT}"
exec gunicorn main:app --bind 0.0.0.0:"${PORT}" --workers 2 --threads 2 --timeout 60
