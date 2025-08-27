# app/model_loader.py
import os
import json
from tensorflow.keras.models import load_model
from pathlib import Path

# Predefined emotion labels (must match training order)
DEFAULT_LABELS = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']


def load_emotion_model():
    """
    Returns: (model, labels, model_version)
    - model: Keras model or raises if missing
    - labels: list or dict mapping indices
    - model_version: string
    """
    # Locate repo/app root (based on this file's location)
    this_dir = Path(__file__).resolve().parent  # app/
    repo_root = this_dir.parent                  # project root (where Dockerfile resides at /app)
    models_dir = repo_root / "models"

    # try .keras then .h5 variants
    candidate_names = ["emotion_model.keras", "emotion_model.h5", "emotion_model.hdf5"]
    model_path = None
    for name in candidate_names:
        p = models_dir / name
        if p.exists():
            model_path = str(p)
            break

    if model_path is None:
        # keep behavior consistent: raise so caller knows model failed to load
        raise FileNotFoundError(f"No model file found in {models_dir}. Please add emotion_model.keras or emotion_model.h5")

    # actually load the Keras model
    model = load_model(model_path)

    # load labels.json if present
    labels_path = models_dir / "labels.json"
    labels = DEFAULT_LABELS
    if labels_path.exists():
        try:
            with labels_path.open("r", encoding="utf-8") as f:
                labels = json.load(f)
        except Exception:
            # fallback to default labels if parsing fails
            labels = DEFAULT_LABELS

    # model version metadata
    version_path = models_dir / "MODEL_VERSION.txt"
    version = "v_unknown"
    if version_path.exists():
        try:
            with version_path.open("r", encoding="utf-8") as f:
                version = f.read().strip()
        except Exception:
            # ignore errors, keep v_unknown
            pass

    return model, labels, version
