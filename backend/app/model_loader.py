import os
import json
from tensorflow.keras.models import load_model

# Predefined emotion labels (must match training order)
DEFAULT_LABELS = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']


def load_emotion_model():
    """
    Returns: (model, labels, model_version)
    -model: Keras model or None
    -labels: list or dict mapping indices
    -model_version: string
    """
    models_dir = os.path.join(os.getcwd(), "models")
    # try .keras then .h5
    model_paths = [
        os.path.join(models_dir, "emotion_model.keras"),
        os.path.join(models_dir, "emotion_model.h5"),
        os.path.join(models_dir, "emotion_model.hdf5")
    ]
    model_path = None
    for p in model_paths:
        if os.path.exists(p):
            model_path = p
            break
    
    if model_path is None:
        raise FileNotFoundError("No model file found in models/. please add emotion_model.keras or emotion_model.h5")

    model = load_model(model_path)
    
    # load labels.json if present
    labels_path = os.path.join(models_dir, "labels.json")
    labels = DEFAULT_LABELS
    if os.path.exists(labels_path):
        try:
            with open(labels_path, "r", encoding="utf-8") as f:
                labels = json.load(f)
        except Exception:
            pass
    
    # model version metadata
    version_path = os.path.join(models_dir, "MODEL_VERSION.txt")
    version = "v_unknown"
    if os.path.exists(version_path):
        try:
            with open(version_path, "r", encoding="uft-8") as f:
                version = f.read().strip()
        except Exception:
            pass
    
    return model, labels, version
    