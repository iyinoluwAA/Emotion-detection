# app/model_loader.py
import os
import json
from pathlib import Path
from typing import Tuple, Any, Optional, Dict

DEFAULT_LABELS = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
# HardlyHumans model uses 8 emotions (adds contempt)
HARDLYHUMANS_LABELS = ['anger', 'contempt', 'sad', 'happy', 'neutral', 'disgust', 'fear', 'surprise']

def load_emotion_model():
    """
    Load emotion detection model. Supports both Keras and Vision Transformer models.
    
    Returns: (model_dict, labels, model_version, model_type)
    model_dict: For ViT: {'model': model, 'processor': processor, 'type': 'vit'}
                For Keras: model object
    model_type: 'keras' or 'vit' (Vision Transformer)
    """
    this_dir = Path(__file__).resolve().parent  # app/
    repo_root = this_dir.parent                 # project root (/app in container)
    models_dir = repo_root / "models"

    # Try to load HardlyHumans ViT model first (best accuracy - 92.2%)
    # Always try to load from HuggingFace - it will download and cache if needed
    try:
        from transformers import AutoImageProcessor, AutoModelForImageClassification
        
        model_id = "HardlyHumans/Facial-expression-detection"
        print(f"[MODEL] Loading Vision Transformer: {model_id}")
        print(f"[MODEL] Accuracy: 92.2% - BEST MODEL!")
        print(f"[MODEL] Downloading from HuggingFace if not cached...")
        
        # Load from HuggingFace - will download and cache automatically
        # Use low_cpu_mem_usage to reduce memory footprint during loading
        processor = AutoImageProcessor.from_pretrained(
            model_id, 
            cache_dir=str(models_dir),
            local_files_only=False  # Allow download if not cached
        )
        model = AutoModelForImageClassification.from_pretrained(
            model_id, 
            cache_dir=str(models_dir),
            local_files_only=False,  # Allow download if not cached
            low_cpu_mem_usage=True,  # Reduce memory usage during loading
            torch_dtype="float32"    # Use float32 instead of float16 to avoid conversion overhead
        )
        
        # Get labels from model config
        raw_labels = [model.config.id2label[i] for i in range(len(model.config.id2label))]
        print(f"[MODEL] Raw labels from model config: {raw_labels}")
        print(f"[MODEL] Label mapping (id2label): {model.config.id2label}")
        
        # Normalize label names to match our format (lowercase, standardize)
        label_map = {
            'anger': 'angry',
            'disgust': 'disgust',
            'fear': 'fear',
            'happy': 'happy',
            'neutral': 'neutral',
            'sad': 'sad',
            'surprise': 'surprise',
            'contempt': 'contempt'  # New emotion in this model
        }
        labels = [label_map.get(label.lower(), label.lower()) for label in raw_labels]
        print(f"[MODEL] Normalized labels: {labels}")
        
        print(f"[MODEL] ✅ ViT model loaded successfully!")
        return {
            'model': model,
            'processor': processor,
            'type': 'vit'
        }, labels, "hardlyhumans-vit-92.2%", 'vit'
    except ImportError:
        print("[MODEL] transformers library not installed. Install with: pip install transformers")
        print("[MODEL] Falling back to Keras model...")
    except Exception as e:
        print(f"[MODEL] Failed to load ViT model: {e}")
        print(f"[MODEL] Error details: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"[MODEL] Traceback: {traceback.format_exc()}")
        print("[MODEL] Falling back to Keras model...")

    # Fall back to Keras models
    try:
        from tensorflow.keras.models import load_model
    except ImportError:
        raise ImportError("Neither transformers nor tensorflow.keras available. Install one of them.")

    candidate_names = ["emotion_model.keras", "emotion_model.h5", "emotion_model.hdf5"]
    model_path = None
    for name in candidate_names:
        p = models_dir / name
        if p.exists():
            model_path = str(p)
            break

    if model_path is None:
        raise FileNotFoundError(f"No model file found in {models_dir}. Please add emotion_model.keras or emotion_model.h5")

    print(f"[MODEL] Loading Keras model: {model_path}")
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

    return model, labels, version, 'keras'
