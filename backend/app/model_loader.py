import os
from pathlib import Path
from tensorflow.keras.models import load_model

# Predefined emotion labels (must match training order)
EMOTION_LABELS = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']


def load_emotion_model(model_filename='emotion_model.keras'):
    """
    Loads the trained Keras model using an absolute path and returns model + labels.
    """
    # Determine base project directory (parent of 'app')
    base_dir = Path(__file__).resolve().parent.parent
    model_path = base_dir / 'models' / model_filename

    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    model = load_model(str(model_path))
    return model, EMOTION_LABELS