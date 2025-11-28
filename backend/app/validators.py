"""
Request validation utilities.
"""
import os
from typing import Tuple, Optional
from werkzeug.utils import secure_filename
from PIL import Image


def validate_image_file(file, max_size: int, allowed_extensions: tuple) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate uploaded image file.
    
    Args:
        file: FileStorage object from Flask
        max_size: Maximum file size in bytes
        allowed_extensions: Tuple of allowed extensions (e.g., (".jpg", ".png"))
    
    Returns:
        Tuple of (is_valid, error_message, sanitized_filename)
        If valid: (True, None, filename)
        If invalid: (False, error_message, None)
    """
    if not file or not file.filename:
        return False, "No file provided", None
    
    # Check filename
    filename = secure_filename(file.filename)
    if not filename:
        return False, "Invalid filename", None
    
    # Check extension
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_extensions:
        return False, f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}", None
    
    # Check file size (if available)
    try:
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > max_size:
            max_mb = max_size / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_mb:.1f}MB", None
        
        if file_size == 0:
            return False, "File is empty", None
    except Exception:
        # If we can't check size, continue (will be caught by MAX_CONTENT_LENGTH)
        pass
    
    # Validate it's actually an image by trying to open it
    try:
        file.seek(0)
        img = Image.open(file)
        img.verify()  # Verify it's a valid image
        file.seek(0)  # Reset after verification
    except Exception as e:
        return False, f"Invalid image file: {str(e)}", None
    
    return True, None, filename


def validate_pagination_params(limit: Optional[str], offset: Optional[str]) -> Tuple[int, int, Optional[str]]:
    """
    Validate pagination parameters.
    
    Returns:
        Tuple of (limit, offset, error_message)
    """
    try:
        limit_val = int(limit) if limit else 20
        limit_val = max(1, min(200, limit_val))
    except ValueError:
        return 20, 0, "Invalid limit parameter. Must be an integer."
    
    try:
        offset_val = int(offset) if offset else 0
        offset_val = max(0, offset_val)
    except ValueError:
        return limit_val, 0, "Invalid offset parameter. Must be an integer."
    
    return limit_val, offset_val, None


def validate_confidence_range(min_conf: Optional[str], max_conf: Optional[str]) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """
    Validate confidence range parameters.
    
    Returns:
        Tuple of (min_confidence, max_confidence, error_message)
    """
    min_val = None
    max_val = None
    
    if min_conf:
        try:
            min_val = float(min_conf)
            if not 0 <= min_val <= 1:
                return None, None, "min_confidence must be between 0 and 1"
        except ValueError:
            return None, None, "Invalid min_confidence parameter. Must be a number."
    
    if max_conf:
        try:
            max_val = float(max_conf)
            if not 0 <= max_val <= 1:
                return None, None, "max_confidence must be between 0 and 1"
        except ValueError:
            return None, None, "Invalid max_confidence parameter. Must be a number."
    
    if min_val is not None and max_val is not None and min_val > max_val:
        return None, None, "min_confidence cannot be greater than max_confidence"
    
    return min_val, max_val, None

