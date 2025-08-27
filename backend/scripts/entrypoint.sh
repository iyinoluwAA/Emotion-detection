#!/usr/bin/env bash
set -euxo pipefail

# allow override: if an env var SKIP_MODEL_DOWNLOAD is set, skip it
if [ "${SKIP_MODEL_DOWNLOAD:-0}" != "1" ]; then
  # run downloader; tolerate failure a limited number of times
  /app/scripts/download_model.sh || {
    echo "Warning: model download failed. Will attempt again at runtime (predict endpoints will fail until model exists)."
  }
else
  echo "SKIP_MODEL_DOWNLOAD=1, skipping download script."
fi

# exec the container's CMD (e.g. gunicorn main:app ...)
# Using exec ensures signals are forwarded correctly.
exec "$@"
