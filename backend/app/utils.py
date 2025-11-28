# app/utils.py
import os
import cv2
import numpy as np
from typing import Optional, Tuple

def _calculate_brightness(gray: np.ndarray) -> float:
    """
    Calculate mean brightness of the image.
    Returns value between 0 (dark) and 255 (bright).
    """
    return float(np.mean(gray))


def _gamma_correction(image: np.ndarray, gamma: float) -> np.ndarray:
    """
    Apply gamma correction to adjust brightness.
    gamma < 1: brightens image
    gamma > 1: darkens image
    """
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)


def _enhance_for_detection(gray: np.ndarray) -> np.ndarray:
    """
    Apply adaptive preprocessing to improve face detection, especially in low light conditions.
    Uses brightness detection to apply appropriate enhancement:
    - Dark images: More aggressive CLAHE + gamma correction
    - Bright images: Standard CLAHE
    """
    brightness = _calculate_brightness(gray)
    
    # Determine if image is dark (threshold: 80/255)
    is_dark = brightness < 80
    is_very_dark = brightness < 50
    
    # Apply gamma correction for very dark images
    if is_very_dark:
        # Brighten significantly (gamma 0.5 = 2x brighter)
        enhanced = _gamma_correction(gray, 0.5)
    elif is_dark:
        # Moderate brightening (gamma 0.7)
        enhanced = _gamma_correction(gray, 0.7)
    else:
        enhanced = gray.copy()
    
    # Apply CLAHE with adaptive parameters
    if is_very_dark:
        # More aggressive CLAHE for very dark images
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    elif is_dark:
        # Moderate CLAHE for dark images
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    else:
        # Standard CLAHE for normal/bright images
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    
    enhanced = clahe.apply(enhanced)
    
    # Bilateral filtering to reduce noise while preserving edges
    # More aggressive for dark images (more noise)
    if is_dark:
        enhanced = cv2.bilateralFilter(enhanced, d=9, sigmaColor=75, sigmaSpace=75)
    else:
        enhanced = cv2.bilateralFilter(enhanced, d=5, sigmaColor=75, sigmaSpace=75)
    
    return enhanced


def preprocess_face(
    image_path: str,
    target_size: Tuple[int, int] = (48, 48),
    detect_max_dim: int = 800,
    pad_ratio: float = 0.15,
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

        # Cascade (built-in). Using standard frontal face cascade.
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        
        # Calculate brightness to adjust detection parameters
        brightness = _calculate_brightness(small_enh)
        is_dark = brightness < 80

        # Primary detection pass with standard parameters
        faces = face_cascade.detectMultiScale(
            small_enh,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

        # If nothing found, try a more permissive pass (helps blurry / odd-angle photos)
        if len(faces) == 0:
            faces = face_cascade.detectMultiScale(
                small_enh,
                scaleFactor=1.05,
                minNeighbors=3,
                minSize=(20, 20),
                flags=cv2.CASCADE_SCALE_IMAGE,
            )

        # For dark images, try even more permissive detection
        if len(faces) == 0 and is_dark:
            # Very permissive for low light conditions
            faces = face_cascade.detectMultiScale(
                small_enh,
                scaleFactor=1.03,  # Smaller scale factor = more scales checked
                minNeighbors=2,    # Lower threshold
                minSize=(15, 15),  # Smaller minimum size
                flags=cv2.CASCADE_SCALE_IMAGE,
            )
        
        # Try with original (non-enhanced) image if still nothing found
        if len(faces) == 0:
            faces = face_cascade.detectMultiScale(
                small,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(25, 25),
                flags=cv2.CASCADE_SCALE_IMAGE,
            )

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
        face_resized = cv2.resize(face_crop, (target_size[1], target_size[0]), interpolation=cv2.INTER_AREA)

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
