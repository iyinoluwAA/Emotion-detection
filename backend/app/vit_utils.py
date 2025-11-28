# app/vit_utils.py
"""
Utilities for Vision Transformer (ViT) model preprocessing and prediction.
"""
import cv2
import numpy as np
from PIL import Image
from typing import Optional, Tuple, Dict, Any
from app.utils import preprocess_face  # Reuse face detection

def preprocess_face_for_vit(
    image_path: str,
    detect_max_dim: int = 800,
    pad_ratio: float = 0.25,
) -> Tuple[Optional[Image.Image], Optional[str]]:
    """
    Preprocess face for Vision Transformer model.
    ViT needs RGB images at 224x224, not grayscale 48x48.
    
    Returns: (PIL Image, filename) or (None, None) if no face detected
    """
    # First detect and crop face (reuse existing detection logic)
    # But we'll keep it in RGB and resize to 224x224
    try:
        img = cv2.imread(image_path)
        if img is None:
            return None, None

        h0, w0 = img.shape[:2]
        # Keep RGB for ViT (not grayscale)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        gray_full = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Downscale for faster detection if image is huge
        scale = 1.0
        max_side = max(w0, h0)
        if max_side > detect_max_dim:
            scale = detect_max_dim / float(max_side)
            small = cv2.resize(gray_full, (int(w0 * scale), int(h0 * scale)), interpolation=cv2.INTER_LINEAR)
        else:
            small = gray_full.copy()

        # Enhance for detection
        from app.utils import _enhance_for_detection
        small_enh = _enhance_for_detection(small)

        # Try multiple cascade classifiers
        cascade_paths = [
            "haarcascade_frontalface_default.xml",
            "haarcascade_frontalface_alt.xml",
            "haarcascade_frontalface_alt2.xml",
        ]
        
        faces = []
        
        for cascade_name in cascade_paths:
            if len(faces) > 0:
                break
            try:
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascade_name)
                if face_cascade.empty():
                    continue
                
                # Multiple attempts with different parameters
                for scale_factor, min_neighbors, min_size in [
                    (1.1, 5, (30, 30)),
                    (1.05, 3, (20, 20)),
                    (1.03, 2, (15, 15)),
                ]:
                    faces = face_cascade.detectMultiScale(
                        small_enh,
                        scaleFactor=scale_factor,
                        minNeighbors=min_neighbors,
                        minSize=min_size,
                        flags=cv2.CASCADE_SCALE_IMAGE,
                    )
                    if len(faces) > 0:
                        break
            except Exception:
                continue
        
        if len(faces) == 0:
            return None, None

        # Choose largest face
        faces = sorted(faces, key=lambda r: r[2] * r[3], reverse=True)
        (x_s, y_s, w_s, h_s) = faces[0]

        # Map back to original scale
        x = int(x_s / scale)
        y = int(y_s / scale)
        w = int(w_s / scale)
        h = int(h_s / scale)

        # Pad bounding box
        pad_w = int(w * pad_ratio)
        pad_h = int(h * pad_ratio)
        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(w0, x + w + pad_w)
        y2 = min(h0, y + h + pad_h)

        # Crop face from RGB image (not grayscale)
        face_crop = img_rgb[y1:y2, x1:x2]

        # Convert to PIL Image and resize to 224x224 (ViT input size)
        face_pil = Image.fromarray(face_crop)
        face_pil = face_pil.resize((224, 224), Image.Resampling.BICUBIC)

        import os
        used_filename = os.path.basename(image_path) or "upload.jpg"
        return face_pil, used_filename

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception(f"Exception in preprocess_face_for_vit for {image_path}: {e}")
        return None, None

def predict_with_vit(
    model_dict: Dict[str, Any],
    image: Image.Image,
    labels: list
) -> Tuple[int, float, Dict[str, float]]:
    """
    Run prediction using Vision Transformer model.
    
    Args:
        model_dict: {'model': model, 'processor': processor, 'type': 'vit'}
        image: PIL Image (224x224 RGB)
        labels: List of emotion labels
    
    Returns:
        (predicted_index, confidence, all_probabilities_dict)
    """
    processor = model_dict['processor']
    model = model_dict['model']
    
    # Preprocess image for ViT
    inputs = processor(image, return_tensors="pt")
    
    # Run prediction (set model to eval mode, but don't use context manager)
    import torch
    import torch.nn.functional as F
    
    model.eval()
    with torch.no_grad():  # Disable gradient computation for inference
        outputs = model(**inputs)
        logits = outputs.logits
    
    # Get probabilities (softmax)
    probs = F.softmax(logits, dim=-1)
    probs_np = probs.detach().cpu().numpy()[0]  # Get first (and only) batch item
    
    # Get predicted class
    predicted_idx = int(torch.argmax(logits, dim=-1).item())
    confidence = float(probs_np[predicted_idx])
    
    # Create probabilities dict - use model's id2label directly to ensure correct mapping
    all_probs = {}
    model = model_dict['model']
    for i, prob in enumerate(probs_np):
        # Use model's id2label for accurate label mapping
        if hasattr(model, 'config') and hasattr(model.config, 'id2label'):
            raw_label = model.config.id2label.get(i, f"class_{i}")
            # Normalize label name
            label_map = {
                'anger': 'angry',
                'disgust': 'disgust',
                'fear': 'fear',
                'happy': 'happy',
                'neutral': 'neutral',
                'sad': 'sad',
                'surprise': 'surprise',
                'contempt': 'contempt'
            }
            normalized_label = label_map.get(raw_label.lower(), raw_label.lower())
            all_probs[normalized_label] = float(prob)
        elif i < len(labels):
            all_probs[labels[i]] = float(prob)
        else:
            all_probs[f"class_{i}"] = float(prob)
    
    print(f"[VIT] Predicted index: {predicted_idx}, Raw label from model: {model.config.id2label.get(predicted_idx, 'unknown')}")
    
    return predicted_idx, confidence, all_probs

