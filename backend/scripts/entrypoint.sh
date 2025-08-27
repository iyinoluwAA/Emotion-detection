#!/usr/bin/env bash
set -euo pipefail

MODEL_DIR=/app/models
MODEL_FILE="${MODEL_DIR}/emotion_model.keras"
MODEL_URL="https://github.com/iyinoluwAA/Emotion-detection/releases/download/v1.0.0/emotion_model.keras"

mkdir -p "${MODEL_DIR}"

if [ -s "${MODEL_FILE}" ]; then
  echo "Model already present: ${MODEL_FILE}"
else
  echo "Model not found, attempting download to ${MODEL_FILE}"
  # use curl with resume support and retries
  if command -v curl >/dev/null 2>&1; then
    curl --fail --location --retry 5 --retry-delay 2 --retry-max-time 60 --continue-at - -o "${MODEL_FILE}" "${MODEL_URL}" || {
      echo "curl download failed"
      exit 1
    }
  elif command -v wget >/dev/null 2>&1; then
    wget -c -O "${MODEL_FILE}" "${MODEL_URL}" || { echo "wget download failed"; exit 1; }
  else
    echo "Error: neither curl nor wget are available in the container"
    exit 1
  fi
  echo "Model downloaded."
fi

# Exec the provided command (usually gunicorn)
exec "$@"
