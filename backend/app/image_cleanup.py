"""
Image cleanup utility to remove orphaned images (not referenced in database).
Can be run as a scheduled job or manually.
"""
import os
import sqlite3
from pathlib import Path
from typing import Set
import logging

logger = logging.getLogger(__name__)


def get_referenced_images(db_path: str) -> Set[str]:
    """
    Get set of all image filenames referenced in the database.
    
    Returns:
        Set of image filenames (basenames only)
    """
    conn = sqlite3.connect(db_path, timeout=10)
    try:
        cur = conn.cursor()
        
        # Check if image_path column exists
        cur.execute("PRAGMA table_info(predictions)")
        columns = [row[1] for row in cur.fetchall()]
        
        if "image_path" not in columns:
            # Column doesn't exist yet, return empty set
            return set()
        
        # Get all non-empty image_path values
        cur.execute("SELECT DISTINCT image_path FROM predictions WHERE image_path IS NOT NULL AND image_path != ''")
        rows = cur.fetchall()
        
        # Extract just the filenames (basenames)
        referenced = set()
        for row in rows:
            if row[0]:
                filename = os.path.basename(row[0])
                if filename:
                    referenced.add(filename)
        
        return referenced
    finally:
        conn.close()


def cleanup_orphaned_images(images_dir: str, db_path: str, dry_run: bool = True) -> dict:
    """
    Remove image files that are not referenced in the database.
    
    Args:
        images_dir: Directory containing images
        db_path: Path to SQLite database
        dry_run: If True, only report what would be deleted without actually deleting
    
    Returns:
        Dict with cleanup statistics
    """
    if not os.path.exists(images_dir):
        logger.warning(f"Images directory does not exist: {images_dir}")
        return {
            "total_images": 0,
            "referenced": 0,
            "orphaned": 0,
            "deleted": 0,
            "errors": 0,
        }
    
    # Get referenced images from database
    referenced = get_referenced_images(db_path)
    logger.info(f"Found {len(referenced)} referenced images in database")
    
    # Get all image files in directory
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
    all_images = []
    
    for file_path in Path(images_dir).iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            all_images.append(file_path.name)
    
    total_images = len(all_images)
    logger.info(f"Found {total_images} image files in directory")
    
    # Find orphaned images
    orphaned = [img for img in all_images if img not in referenced]
    
    stats = {
        "total_images": total_images,
        "referenced": len(referenced),
        "orphaned": len(orphaned),
        "deleted": 0,
        "errors": 0,
    }
    
    if not orphaned:
        logger.info("No orphaned images found")
        return stats
    
    logger.info(f"Found {len(orphaned)} orphaned images")
    
    # Delete orphaned images
    for filename in orphaned:
        file_path = os.path.join(images_dir, filename)
        try:
            if not dry_run:
                os.remove(file_path)
                logger.debug(f"Deleted orphaned image: {filename}")
            else:
                logger.debug(f"Would delete orphaned image: {filename}")
            stats["deleted"] += 1
        except Exception as e:
            logger.error(f"Failed to delete {filename}: {e}")
            stats["errors"] += 1
    
    if dry_run:
        logger.info(f"DRY RUN: Would delete {stats['deleted']} orphaned images")
    else:
        logger.info(f"Deleted {stats['deleted']} orphaned images")
    
    return stats


def cleanup_old_images(images_dir: str, db_path: str, days_old: int = 30, dry_run: bool = True) -> dict:
    """
    Remove images older than specified days that are not referenced in recent predictions.
    
    Args:
        images_dir: Directory containing images
        db_path: Path to SQLite database
        days_old: Remove images older than this many days
        dry_run: If True, only report what would be deleted
    
    Returns:
        Dict with cleanup statistics
    """
    import datetime
    
    if not os.path.exists(images_dir):
        return {
            "total_images": 0,
            "old_images": 0,
            "deleted": 0,
            "errors": 0,
        }
    
    # Calculate cutoff date
    cutoff_date = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=days_old)
    cutoff_iso = cutoff_date.isoformat()
    
    # Get images referenced after cutoff
    conn = sqlite3.connect(db_path, timeout=10)
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT image_path 
            FROM predictions 
            WHERE image_path IS NOT NULL 
            AND image_path != '' 
            AND ts >= ?
        """, (cutoff_iso,))
        recent_images = {os.path.basename(row[0]) for row in cur.fetchall() if row[0]}
    finally:
        conn.close()
    
    # Find old images
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
    old_images = []
    
    for file_path in Path(images_dir).iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            # Check file modification time
            mtime = datetime.datetime.fromtimestamp(file_path.stat().st_mtime, tz=datetime.UTC)
            if mtime < cutoff_date:
                # Only delete if not in recent images
                if file_path.name not in recent_images:
                    old_images.append(file_path.name)
    
    stats = {
        "total_images": len(list(Path(images_dir).iterdir())),
        "old_images": len(old_images),
        "deleted": 0,
        "errors": 0,
    }
    
    for filename in old_images:
        file_path = os.path.join(images_dir, filename)
        try:
            if not dry_run:
                os.remove(file_path)
            stats["deleted"] += 1
        except Exception as e:
            logger.error(f"Failed to delete {filename}: {e}")
            stats["errors"] += 1
    
    return stats


