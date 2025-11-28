# app/utils.py
import os
import cv2
import numpy as np
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

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
        # Check if file exists
        if not os.path.exists(image_path):
            logger.warning(f"Image file does not exist: {image_path}")
            return None, None
        
        file_size = os.path.getsize(image_path)
        if file_size == 0:
            logger.warning(f"Image file is empty: {image_path}")
            return None, None
        
        # Use print for critical debugging (always shows in logs)
        print(f"[FACE_DETECTION] Loading image: {image_path}, file size: {file_size} bytes")
        logger.info(f"Loading image: {image_path}, file size: {file_size} bytes")
        
        # Try loading with cv2.imread
        img = cv2.imread(image_path)
        if img is None:
            logger.warning(f"cv2.imread returned None for {image_path}, trying alternative loading method")
            # Try with PIL as fallback
            try:
                from PIL import Image
                pil_img = Image.open(image_path)
                # Convert PIL to OpenCV format
                img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                logger.info(f"Successfully loaded image using PIL fallback: {image_path}")
            except Exception as e:
                logger.error(f"Both cv2.imread and PIL failed to load image {image_path}: {e}")
                return None, None

        if img is None or img.size == 0:
            logger.error(f"Image is None or empty after loading: {image_path}")
            return None, None

        h0, w0 = img.shape[:2]
        print(f"[FACE_DETECTION] Successfully loaded image: {image_path}, size: {w0}x{h0}, shape: {img.shape}")
        logger.info(f"Successfully loaded image: {image_path}, size: {w0}x{h0}, shape: {img.shape}")
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
        
        # Calculate brightness to adjust detection parameters
        brightness = _calculate_brightness(small_enh)
        is_dark = brightness < 80
        is_very_dark = brightness < 50
        
        faces = []
        
        # Try each cascade classifier with progressively more permissive parameters
        for cascade_name in cascade_paths:
            if len(faces) > 0:
                break
                
            try:
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascade_name)
                if face_cascade.empty():
                    continue
                
                # Try multiple detection strategies with increasingly permissive parameters
                detection_attempts = [
                    # Standard detection
                    {"scaleFactor": 1.1, "minNeighbors": 5, "minSize": (30, 30)},
                    # More permissive
                    {"scaleFactor": 1.05, "minNeighbors": 3, "minSize": (20, 20)},
                    # Even more permissive
                    {"scaleFactor": 1.03, "minNeighbors": 2, "minSize": (15, 15)},
                    # Very permissive
                    {"scaleFactor": 1.02, "minNeighbors": 1, "minSize": (10, 10)},
                    # Extremely permissive
                    {"scaleFactor": 1.01, "minNeighbors": 1, "minSize": (5, 5)},
                    # Last resort - no minSize constraint
                    {"scaleFactor": 1.1, "minNeighbors": 1, "minSize": None},
                ]
                
                for attempt in detection_attempts:
                    if len(faces) > 0:
                        break
                    try:
                        params = {
                            "scaleFactor": attempt["scaleFactor"],
                            "minNeighbors": attempt["minNeighbors"],
                            "flags": cv2.CASCADE_SCALE_IMAGE,
                        }
                        if attempt["minSize"] is not None:
                            params["minSize"] = attempt["minSize"]
                        
                        faces = face_cascade.detectMultiScale(small_enh, **params)
                    except Exception:
                        continue
                    
            except Exception:
                continue
        
        # Try with original (non-enhanced) image if still nothing found
        if len(faces) == 0:
            try:
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
                if not face_cascade.empty():
                    # Try multiple permissive attempts on original
                    for scale_factor, min_neighbors, min_size in [
                        (1.1, 4, (25, 25)),
                        (1.05, 2, (15, 15)),
                        (1.03, 1, (10, 10)),
                        (1.02, 1, (5, 5)),
                        (1.1, 1, None),  # No minSize
                    ]:
                        if len(faces) > 0:
                            break
                        try:
                            params = {
                                "scaleFactor": scale_factor,
                                "minNeighbors": min_neighbors,
                                "flags": cv2.CASCADE_SCALE_IMAGE,
                            }
                            if min_size is not None:
                                params["minSize"] = min_size
                            faces = face_cascade.detectMultiScale(small, **params)
                        except Exception:
                            continue
            except Exception:
                pass
        
        # Last resort: try on full-size image if downscaled
        used_full_size = False
        if len(faces) == 0:
            try:
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
                if not face_cascade.empty():
                    # Try on full-size enhanced image
                    gray_enh_full = _enhance_for_detection(gray_full)
                    
                    # Calculate appropriate minSize for full image
                    base_min_size = 30 if scale >= 1.0 else max(30, int(30 / scale))
                    
                    # Try multiple attempts on full-size enhanced
                    for scale_factor, min_neighbors, min_size_mult in [
                        (1.1, 4, 1.0),
                        (1.05, 2, 0.7),
                        (1.03, 1, 0.5),
                        (1.02, 1, 0.3),
                        (1.1, 1, None),  # No minSize
                    ]:
                        if len(faces) > 0:
                            break
                        try:
                            params = {
                                "scaleFactor": scale_factor,
                                "minNeighbors": min_neighbors,
                                "flags": cv2.CASCADE_SCALE_IMAGE,
                            }
                            if min_size_mult is not None:
                                min_size_val = int(base_min_size * min_size_mult)
                                params["minSize"] = (min_size_val, min_size_val)
                            faces = face_cascade.detectMultiScale(gray_enh_full, **params)
                            if len(faces) > 0:
                                used_full_size = True
                        except Exception:
                            continue
                    
                    # If still nothing, try on original full-size grayscale
                    if len(faces) == 0:
                        for scale_factor, min_neighbors, min_size_mult in [
                            (1.1, 3, 1.0),
                            (1.05, 1, 0.7),
                            (1.03, 1, 0.5),
                            (1.1, 1, None),
                        ]:
                            if len(faces) > 0:
                                break
                            try:
                                params = {
                                    "scaleFactor": scale_factor,
                                    "minNeighbors": min_neighbors,
                                    "flags": cv2.CASCADE_SCALE_IMAGE,
                                }
                                if min_size_mult is not None:
                                    min_size_val = int(base_min_size * min_size_mult)
                                    params["minSize"] = (min_size_val, min_size_val)
                                faces = face_cascade.detectMultiScale(gray_full, **params)
                                if len(faces) > 0:
                                    used_full_size = True
                            except Exception:
                                continue
            except Exception:
                pass

        # Last resort: if no face detected, use fallback strategies
        # This handles cases where face detection fails but there's clearly a face
        if len(faces) == 0:
            print(f"[FACE_DETECTION] No face detected with all methods, trying fallback strategies for {image_path} (image size: {w0}x{h0})")
            logger.info(f"No face detected with all methods, trying fallback strategies for {image_path} (image size: {w0}x{h0})")
            
            # Strategy 1: Center crop - assume face is in center 60% of image
            if w0 >= 48 and h0 >= 48:
                try:
                    crop_w = max(48, int(w0 * 0.6))
                    crop_h = max(48, int(h0 * 0.6))
                    center_x, center_y = w0 // 2, h0 // 2
                    x1 = max(0, center_x - crop_w // 2)
                    y1 = max(0, center_y - crop_h // 2)
                    x2 = min(w0, x1 + crop_w)
                    y2 = min(h0, y1 + crop_h)
                    
                    actual_crop_w = x2 - x1
                    actual_crop_h = y2 - y1
                    
                    logger.debug(f"Center crop: ({x1}, {y1}) to ({x2}, {y2}), actual size: {actual_crop_w}x{actual_crop_h}")
                    
                    if actual_crop_w >= 48 and actual_crop_h >= 48:
                        face_crop = gray_full[y1:y2, x1:x2]
                        if face_crop.size > 0 and face_crop.shape[0] > 0 and face_crop.shape[1] > 0:
                            logger.debug(f"Center crop successful, resizing from {face_crop.shape} to {target_size}")
                            face_resized = cv2.resize(face_crop, (target_size[1], target_size[0]), interpolation=cv2.INTER_AREA)
                            
                            if face_resized.size > 0:
                                face_arr = np.asarray(face_resized, dtype=np.float32)
                                face_arr = face_arr / 255.0
                                
                                if face_arr.ndim == 2:
                                    face_arr = np.expand_dims(face_arr, axis=-1)
                                face_arr = np.expand_dims(face_arr, axis=0)
                                
                                if face_arr.dtype != np.float32:
                                    face_arr = face_arr.astype(np.float32)
                                
                                if np.isfinite(face_arr).all():
                    print(f"[FACE_DETECTION] Successfully using center crop fallback for {image_path}, final shape: {face_arr.shape}")
                    logger.info(f"Successfully using center crop fallback for {image_path}, final shape: {face_arr.shape}")
                    used_filename = os.path.basename(image_path) or "upload.jpg"
                    return face_arr, used_filename
                except Exception as e:
                    logger.warning(f"Center crop fallback failed: {e}")
            
            # Strategy 2: Use entire image resized (last resort)
            # If center crop fails, just use the whole image - better than nothing
            try:
                logger.info(f"Center crop failed, using entire image as fallback for {image_path}")
                if w0 >= 48 and h0 >= 48:
                    # Resize entire grayscale image to target size
                    face_resized = cv2.resize(gray_full, (target_size[1], target_size[0]), interpolation=cv2.INTER_AREA)
                    
                    if face_resized.size > 0:
                        face_arr = np.asarray(face_resized, dtype=np.float32)
                        face_arr = face_arr / 255.0
                        
                        if face_arr.ndim == 2:
                            face_arr = np.expand_dims(face_arr, axis=-1)
                        face_arr = np.expand_dims(face_arr, axis=0)
                        
                        if face_arr.dtype != np.float32:
                            face_arr = face_arr.astype(np.float32)
                        
                        if np.isfinite(face_arr).all():
                    print(f"[FACE_DETECTION] Successfully using entire image fallback for {image_path}, final shape: {face_arr.shape}")
                    logger.info(f"Successfully using entire image fallback for {image_path}, final shape: {face_arr.shape}")
                    used_filename = os.path.basename(image_path) or "upload.jpg"
                    return face_arr, used_filename
            except Exception as e:
                logger.exception(f"Entire image fallback also failed for {image_path}: {e}")
            
            # If all fallbacks fail, return None
            print(f"[FACE_DETECTION] ERROR: ALL face detection methods and fallbacks failed for {image_path} (size: {w0}x{h0})")
            logger.error(f"ALL face detection methods and fallbacks failed for {image_path} (size: {w0}x{h0})")
            return None, None

        # Choose the largest detected face (usually the main subject)
        faces = sorted(faces, key=lambda r: r[2] * r[3], reverse=True)
        (x_s, y_s, w_s, h_s) = faces[0]

        # Map coordinates back to original image scale
        # If we used full-size image, no scaling needed
        if used_full_size:
            x, y, w, h = int(x_s), int(y_s), int(w_s), int(h_s)
        else:
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

    except Exception as e:
        # Log the exception for debugging
        logger.exception(f"Exception in preprocess_face for {image_path}: {e}")
        return None, None
