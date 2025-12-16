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
    pad_ratio: float = 0.35,  # Increased to 0.35 to include more facial context - helps with happy detection (smile needs more context)
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

        # Optimized face detection: 2 cascades × 2 param sets = 4 attempts (fast)
        # Then fallback to 3rd cascade if needed = +2 attempts (total 6 max)
        # This balances speed (4 attempts) with reliability (6 attempts if needed)
        cascade_paths_primary = [
            "haarcascade_frontalface_default.xml",  # Most reliable
            "haarcascade_frontalface_alt.xml",      # Good fallback
        ]
        
        cascade_paths_fallback = [
            "haarcascade_frontalface_alt2.xml",     # Last resort
        ]
        
        faces = []
        
        # Primary: Try 2 cascades with 2 param sets each (4 attempts, fast path)
        for cascade_name in cascade_paths_primary:
            if len(faces) > 0:
                break
            try:
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascade_name)
                if face_cascade.empty():
                    continue
                
                # Attempt 1: Most common successful params (catches 90%+ of faces)
                faces = face_cascade.detectMultiScale(
                    small_enh,
                    scaleFactor=1.05,
                    minNeighbors=3,
                    minSize=(20, 20),
                    flags=cv2.CASCADE_SCALE_IMAGE,
                )
                
                # Attempt 2: More permissive (catches challenging cases)
                if len(faces) == 0:
                    faces = face_cascade.detectMultiScale(
                        small_enh,
                        scaleFactor=1.03,
                        minNeighbors=2,
                        minSize=(15, 15),
                        flags=cv2.CASCADE_SCALE_IMAGE,
                    )
                    
            except Exception:
                continue
        
        # Fallback: Only try 3rd cascade if primary failed (adds 2 more attempts)
        if len(faces) == 0:
            for cascade_name in cascade_paths_fallback:
                if len(faces) > 0:
                    break
                try:
                    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascade_name)
                    if face_cascade.empty():
                        continue
                    
                    # Try with permissive params
                    for scale_factor, min_neighbors, min_size in [
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
        
        # Fallback 1: Try on original (non-enhanced) image if enhanced failed
        # Only try once with best params (don't waste time on multiple attempts)
        if len(faces) == 0:
            try:
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
                if not face_cascade.empty():
                    # Single attempt with most successful params (faster than trying multiple)
                    faces = face_cascade.detectMultiScale(
                        small,  # Use original, not enhanced
                        scaleFactor=1.05,
                        minNeighbors=3,
                        minSize=(20, 20),
                        flags=cv2.CASCADE_SCALE_IMAGE,
                    )
            except Exception:
                pass
        
        # Fallback 2: Try on full-size image ONLY if:
        # 1. Still no face found
        # 2. Image was actually downscaled (max_side > 800)
        # 3. Scale is significantly reduced (scale < 0.5, meaning image is 2x+ larger)
        # This prevents slow full-size detection on images that are only slightly over 800px
        if len(faces) == 0 and max_side > detect_max_dim and scale < 0.5:
            try:
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
                if not face_cascade.empty():
                    # Single attempt with permissive params (full-size is slow, so only try once)
                    faces = face_cascade.detectMultiScale(
                        gray_full,
                        scaleFactor=1.05,
                        minNeighbors=2,
                        minSize=(30, 30),  # Larger min size for full-res
                        flags=cv2.CASCADE_SCALE_IMAGE,
                    )
            except Exception:
                pass
        
        if len(faces) == 0:
            return None, None

        # Choose largest face
        faces = sorted(faces, key=lambda r: r[2] * r[3], reverse=True)
        (x_s, y_s, w_s, h_s) = faces[0]

        # Map back to original scale (only if we used downscaled detection)
        # If we detected on full-size image, coordinates are already correct
        if max_side > detect_max_dim and scale < 1.0:
            # Detection was on downscaled image
            x = int(x_s / scale)
            y = int(y_s / scale)
            w = int(w_s / scale)
            h = int(h_s / scale)
        else:
            # Detection was on full-size or original scale
            x = x_s
            y = y_s
            w = w_s
            h = h_s

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
        # Use BICUBIC for best quality (emotion recognition needs detail)
        # Note: ViT processor handles normalization, so we don't apply CLAHE here
        # CLAHE can interfere with the model's expected input distribution
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
    Enhanced for better accuracy with image preprocessing.
    
    Args:
        model_dict: {'model': model, 'processor': processor, 'type': 'vit'}
        image: PIL Image (224x224 RGB)
        labels: List of emotion labels
    
    Returns:
        (predicted_index, confidence, all_probabilities_dict)
    """
    processor = model_dict['processor']
    model = model_dict['model']
    
    # Ensure image is RGB (some images might be RGBA or grayscale)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Preprocess image for ViT (processor handles normalization)
    inputs = processor(image, return_tensors="pt")
    
    # Run prediction - optimized for speed
    import torch
    import torch.nn.functional as F
    
    model.eval()
    # Use inference_mode() instead of no_grad() - faster for inference-only
    with torch.inference_mode():  # Faster than no_grad() for pure inference
        outputs = model(**inputs)
        logits = outputs.logits
    
    # Get probabilities (softmax) - optimized conversion
    probs = F.softmax(logits, dim=-1)
    probs_np = probs[0].cpu().numpy()  # Direct indexing, no detach needed in inference_mode
    
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
    
    # Post-processing: If happy probability is reasonable (>0.05) but contempt/neutral is high,
    # and happy is in top 3, boost happy probability (model has known happy/contempt confusion)
    happy_prob = all_probs.get('happy', 0.0)
    contempt_prob = all_probs.get('contempt', 0.0)
    neutral_prob = all_probs.get('neutral', 0.0)
    
    # If happy is in top 3 probabilities and contempt/neutral is suspiciously high
    sorted_probs = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)
    top_3_emotions = [e[0] for e in sorted_probs[:3]]
    
    if 'happy' in top_3_emotions and happy_prob > 0.05:
        # If contempt or neutral is highest but happy is close, boost happy
        if (contempt_prob > 0.4 or neutral_prob > 0.4) and happy_prob > 0.05:
            # Boost happy by 30% (helps correct misclassifications)
            boost_factor = 1.3
            boosted_happy = min(1.0, happy_prob * boost_factor)
            
            # Reduce contempt/neutral proportionally to maintain probability sum
            reduction = (boosted_happy - happy_prob) / 2
            new_contempt = max(0.0, contempt_prob - reduction)
            new_neutral = max(0.0, neutral_prob - reduction)
            
            # Update probabilities
            all_probs['happy'] = boosted_happy
            all_probs['contempt'] = new_contempt
            all_probs['neutral'] = new_neutral
            
            # Re-normalize to ensure sum is ~1.0
            total = sum(all_probs.values())
            if total > 0:
                all_probs = {k: v / total for k, v in all_probs.items()}
            
            # Recalculate predicted class after boosting - find emotion with highest prob
            new_top_emotion = max(all_probs.items(), key=lambda x: x[1])[0]
            
            # Find index in labels list
            if new_top_emotion in labels:
                predicted_idx = labels.index(new_top_emotion)
                confidence = all_probs[new_top_emotion]
                print(f"[VIT] Post-processing: Boosted happy from {happy_prob:.3f} to {all_probs.get('happy', 0.0):.3f}, new prediction: {new_top_emotion}")
            else:
                # Fallback to original prediction if label not found
                print(f"[VIT] Post-processing: Boosted happy but couldn't find label {new_top_emotion} in labels list")
    
    print(f"[VIT] Predicted index: {predicted_idx}, Raw label from model: {model.config.id2label.get(predicted_idx, 'unknown')}")
    
    return predicted_idx, confidence, all_probs

