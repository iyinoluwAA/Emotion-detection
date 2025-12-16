# app/utils.py
import os
import cv2
import numpy as np
from typing import Optional, Tuple

def _enhance_for_detection(gray: np.ndarray) -> np.ndarray:
    """
    Apply light preprocessing to improve face detection on low-contrast or slightly blurry images.
    Uses CLAHE (adaptive histogram equalization) and a mild bilateral filter.
    """
    # CLAHE for contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Mild bilateral filtering to reduce noise while preserving edges (helps detection on some images)
    enhanced = cv2.bilateralFilter(enhanced, d=5, sigmaColor=75, sigmaSpace=75)
    return enhanced


def preprocess_face(
    image_path: str,
    target_size: Tuple[int, int] = (48, 48),
    detect_max_dim: int = 800,
    pad_ratio: float = 0.25,  # Increased from 0.15 to 0.25 to preserve more context (eyes, eyebrows, mouth area)
) -> Tuple[Optional[np.ndarray], Optional[str]]:
    """
    Load an image at image_path, detect a face and return a preprocessed array:
      - shape: (1, H, W, 1)
      - dtype: np.float32
      - values scaled to [0,1]

    If no face detected or on error, returns (None, None).

    Parameters:
    - target_size: size expected by the model (height, width).
    - detect_max_dim: maximum size (longest side) used for the detection pass to speed up detection.
    - pad_ratio: fraction of face box to pad on each side (helps avoid tight crops).

    Returns:
    - (face_array, used_filename)
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return None, None

        h0, w0 = img.shape[:2]
        # grayscale copy for detection
        gray_full = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Downscale for faster detection if image is huge
        scale = 1.0
        max_side = max(w0, h0)
        if max_side > detect_max_dim:
            scale = detect_max_dim / float(max_side)
            small = cv2.resize(gray_full, (int(w0 * scale), int(h0 * scale)), interpolation=cv2.INTER_LINEAR)
        else:
            small = gray_full.copy()

        # Try to enhance small image for better detection on blurry photos
        small_enh = _enhance_for_detection(small)

        # Try multiple cascade classifiers for better detection
        cascade_paths = [
            "haarcascade_frontalface_default.xml",
            "haarcascade_frontalface_alt.xml",
            "haarcascade_frontalface_alt2.xml",
        ]
        
        faces = []
        
        # Try each cascade with progressively more permissive parameters
        for cascade_name in cascade_paths:
            if len(faces) > 0:
                break
                
            try:
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascade_name)
                if face_cascade.empty():
                    continue
                
                # Attempt 1: Standard detection
                faces = face_cascade.detectMultiScale(
                    small_enh,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30),
                    flags=cv2.CASCADE_SCALE_IMAGE,
                )
                
                # Attempt 2: More permissive (helps blurry / odd-angle photos)
                if len(faces) == 0:
                    faces = face_cascade.detectMultiScale(
                        small_enh,
                        scaleFactor=1.05,
                        minNeighbors=3,
                        minSize=(20, 20),
                        flags=cv2.CASCADE_SCALE_IMAGE,
                    )
                
                # Attempt 3: Even more permissive (for challenging conditions)
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
        
        # If still nothing, try on original (non-enhanced) image
        if len(faces) == 0:
            try:
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
                if not face_cascade.empty():
                    # Sometimes enhancement hurts detection, try original
                    faces = face_cascade.detectMultiScale(
                        small,
                        scaleFactor=1.05,
                        minNeighbors=3,
                        minSize=(20, 20),
                        flags=cv2.CASCADE_SCALE_IMAGE,
                    )
            except Exception:
                pass

        if len(faces) == 0:
            return None, None

        # Choose the largest detected face (usually the main subject)
        faces = sorted(faces, key=lambda r: r[2] * r[3], reverse=True)
        (x_s, y_s, w_s, h_s) = faces[0]

        # Map coordinates back to original image scale
        x = int(x_s / scale)
        y = int(y_s / scale)
        w = int(w_s / scale)
        h = int(h_s / scale)

        # Pad bounding box slightly (pad_ratio of face size)
        pad_w = int(w * pad_ratio)
        pad_h = int(h * pad_ratio)
        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(w0, x + w + pad_w)
        y2 = min(h0, y + h + pad_h)

        face_crop = gray_full[y1:y2, x1:x2]

        # final resize to model input
        # Use INTER_CUBIC for better quality when upscaling small faces (preserves more detail for emotion recognition)
        face_resized = cv2.resize(face_crop, (target_size[1], target_size[0]), interpolation=cv2.INTER_CUBIC)

        # ensure numeric ndarray and float32 dtype
        face_arr = np.asarray(face_resized, dtype=np.float32)

        # normalize
        face_arr = face_arr / 255.0

        # channel & batch dims -> (1, H, W, 1)
        if face_arr.ndim == 2:
            face_arr = np.expand_dims(face_arr, axis=-1)
        face_arr = np.expand_dims(face_arr, axis=0)

        # final sanity checks
        if face_arr.dtype != np.float32:
            face_arr = face_arr.astype(np.float32)
        if not np.isfinite(face_arr).all():
            return None, None

        used_filename = os.path.basename(image_path) or "upload.jpg"
        return face_arr, used_filename

    except Exception:
        # don't leak internals to caller; let app log exceptions if needed
        return None, None
