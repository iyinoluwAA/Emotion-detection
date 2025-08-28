# app/model_loader.py
import os
import json
from tensorflow.keras.models import load_model
from pathlib import Path

DEFAULT_LABELS = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

def load_emotion_model():
    """
    Returns: (model, labels, model_version)
    """
    this_dir = Path(__file__).resolve().parent  # app/
    repo_root = this_dir.parent                 # project root (/app in container)
    models_dir = repo_root / "models"

    candidate_names = ["emotion_model.keras", "emotion_model.h5", "emotion_model.hdf5"]
    model_path = None
    for name in candidate_names:
        p = models_dir / name
        if p.exists():
            model_path = str(p)
            break

    if model_path is None:
        raise FileNotFoundError(f"No model file found in {models_dir}. Please add emotion_model.keras or emotion_model.h5")

    model = load_model(model_path)

    # Load labels if available
    labels_path = models_dir / "labels.json"
    labels = DEFAULT_LABELS
    if labels_path.exists():
        try:
            with labels_path.open("r", encoding="utf-8") as f:
                labels = json.load(f)
        except Exception:
            labels = DEFAULT_LABELS

    # Model version
    version_path = models_dir / "MODEL_VERSION.txt"
    version = "v_unknown"
    if os.path.exists(version_path):
        try:
            with open(version_path, "r", encoding="utf-8") as f:
                version = f.read().strip()
        except Exception:
            pass

    # ✅ always return
    return model, labels, version
