"""
Image storage utilities for saving and serving uploaded images.
"""
import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, Tuple
from werkzeug.utils import secure_filename


def ensure_images_dir(images_dir: str) -> str:
    """Ensure images directory exists and return its path."""
    os.makedirs(images_dir, exist_ok=True)
    return images_dir


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename to avoid collisions.
    Format: {uuid}_{secure_original_name} or just {uuid}.jpg if original is invalid
    """
    # Get secure base name
    base_name = secure_filename(original_filename)
    if not base_name:
        base_name = "upload.jpg"
    
    # Add UUID prefix for uniqueness (use full UUID to ensure uniqueness)
    name, ext = os.path.splitext(base_name)
    if not ext or ext.lower() not in ('.jpg', '.jpeg', '.png'):
        ext = '.jpg'
    unique_id = str(uuid.uuid4())  # Full UUID for better uniqueness
    return f"{unique_id}_{name}{ext}"


def save_image(source_path: str, images_dir: str, original_filename: str) -> Optional[str]:
    """
    Save an image from source_path to images_dir with a unique filename.
    
    Args:
        source_path: Path to source image file
        images_dir: Directory to save images to
        original_filename: Original filename for reference
    
    Returns:
        Stored filename (relative to images_dir) or None on failure
    """
    try:
        ensure_images_dir(images_dir)
        
        # Generate unique filename
        stored_filename = generate_unique_filename(original_filename)
        dest_path = os.path.join(images_dir, stored_filename)
        
        # Copy file
        shutil.copy2(source_path, dest_path)
        
        return stored_filename
    except Exception as e:
        # Log error but don't fail the request
        import logging
        logging.getLogger(__name__).exception(f"Failed to save image: {e}")
        return None


def get_image_path(images_dir: str, filename: str) -> Optional[str]:
    """
    Get full path to an image file if it exists.
    
    Args:
        images_dir: Base images directory
        filename: Image filename
    
    Returns:
        Full path to image or None if not found
    """
    if not filename:
        return None
    
    # Security: ensure filename doesn't contain path traversal
    # Extract just the basename to prevent directory traversal
    base_filename = os.path.basename(filename)
    safe_filename = secure_filename(base_filename)
    
    if not safe_filename:
        return None
    
    # Use safe_filename for the path (secure_filename may have sanitized it)
    # But also try the original if it's already safe
    image_path = os.path.join(images_dir, safe_filename)
    
    if os.path.exists(image_path) and os.path.isfile(image_path):
        return image_path
    
    # Also try the original filename if it's different and seems safe
    if safe_filename != base_filename:
        # Check if original is safe (no path separators, no parent dir references)
        if base_filename == filename and '/' not in base_filename and '\\' not in base_filename and '..' not in base_filename:
            alt_path = os.path.join(images_dir, base_filename)
            if os.path.exists(alt_path) and os.path.isfile(alt_path):
                return alt_path
    
    return None


def delete_image(images_dir: str, filename: str) -> bool:
    """
    Delete an image file.
    
    Args:
        images_dir: Base images directory
        filename: Image filename to delete
    
    Returns:
        True if deleted, False otherwise
    """
    try:
        image_path = get_image_path(images_dir, filename)
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
            return True
        return False
    except Exception:
        return False
