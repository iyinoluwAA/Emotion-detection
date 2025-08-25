    #!/usr/bin/env bash
    set -euo pipefail

    # Usage:
    #   ./scripts/download_model.sh [DEST_PATH]
    # or:
    #   DEST=backend/models/emotion_model.keras ./scripts/download_model.sh
    #
    # Defaults to backend/models/emotion_model.keras

    DEFAULT_DEST="backend/models/emotion_model.keras"
    MODEL_URL="https://github.com/iyinoluwAA/Emotion-detection/releases/download/v1.0.0/emotion_model.keras"

    DEST="${DEST:-${1:-$DEFAULT_DEST}}"
    DEST_DIR="$(dirname "$DEST")"

    echo "Target model path: $DEST"
    echo "Model URL: $MODEL_URL"

    if [ -f "$DEST" ]; then
    echo "Model already exists at $DEST — skipping download."
    exit 0
    fi

    # create parent dir
    mkdir -p "$DEST_DIR"

    echo "Downloading model to $DEST_DIR ..."
    if command -v curl >/dev/null 2>&1; then
    curl -L --fail --retry 3 --retry-delay 2 "$MODEL_URL" -o "$DEST.part"
    elif command -v wget >/dev/null 2>&1; then
    wget -O "$DEST.part" "$MODEL_URL"
    else
    echo "Error: neither curl nor wget is installed." >&2
    exit 2
    fi

    # move into final name (only if download completed)
    mv "$DEST.part" "$DEST"
    echo "Download complete: $DEST"

    # quick sanity check (file size > 0)
    if [ ! -s "$DEST" ]; then
    echo "Error: downloaded file is empty." >&2
    exit 3
    fi

    echo "Done."
