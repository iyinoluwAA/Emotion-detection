#!/usr/bin/env bash
set -eu

MODEL_DIR="/app/backend/models"
MODEL_FILE="${MODEL_DIR}/emotion_model.keras"
MODEL_URL="https://github.com/iyinoluwAA/Emotion-detection/releases/download/v1.0.0/emotion_model.keras"
RETRIES=6
SLEEP=5

mkdir -p "$MODEL_DIR"

if [ -f "$MODEL_FILE" ]; then
  echo "Model already exists at $MODEL_FILE — skipping download."
  exit 0
fi

echo "Downloading model to $MODEL_DIR from $MODEL_URL"

download_with_curl() {
  curl --fail --location --retry $RETRIES --retry-delay $SLEEP --retry-connrefused --show-error -o "$MODEL_FILE" "$MODEL_URL"
}

download_with_wget() {
  wget --tries=$RETRIES --wait=$SLEEP --output-document="$MODEL_FILE" "$MODEL_URL"
}

if command -v curl >/dev/null 2>&1; then
  download_with_curl || { echo "curl download failed"; rm -f "$MODEL_FILE"; exit 1; }
elif command -v wget >/dev/null 2>&1; then
  download_with_wget || { echo "wget download failed"; rm -f "$MODEL_FILE"; exit 1; }
else
  echo "Error: neither curl nor wget is available."
  exit 1
fi

echo "Download succeeded."
