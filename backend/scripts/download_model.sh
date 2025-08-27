#!/bin/sh
set -eu

# default target - if running inside the image with workdir /app this will be /app/models/...
TARGET="${1:-backend/models/emotion_model.keras}"
URL="${2:-https://github.com/iyinoluwAA/Emotion-detection/releases/download/v1.0.0/emotion_model.keras}"

mkdir -p "$(dirname "$TARGET")"

echo "Target model path: $TARGET"
echo "Model URL: $URL"

if command -v curl >/dev/null 2>&1; then
  curl -fSL "$URL" -o "$TARGET"
elif command -v wget >/dev/null 2>&1; then
  wget -O "$TARGET" "$URL"
else
  echo "Error: neither curl nor wget is installed." >&2
  exit 2
fi

echo "Downloaded model to $(realpath "$TARGET")"
