
import sqlite3
import os
import datetime
from typing import Dict, Tuple, List, Optional
import threading

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    filename TEXT,
    image_path TEXT,
    emotion TEXT,
    confidence REAL
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_predictions_ts ON predictions(ts DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_emotion ON predictions(emotion);
CREATE INDEX IF NOT EXISTS idx_predictions_confidence ON predictions(confidence);
"""

# Connection pool for better performance
_db_lock = threading.Lock()
_connection_pool: Dict[str, sqlite3.Connection] = {}


def get_connection(db_path: str, timeout: int = 10) -> sqlite3.Connection:
    """
    Get a database connection with connection pooling.
    For SQLite, we use a simple per-thread connection approach.
    """
    thread_id = threading.get_ident()
    key = f"{db_path}_{thread_id}"
    
    with _db_lock:
        if key not in _connection_pool:
            conn = sqlite3.connect(db_path, timeout=timeout, check_same_thread=False)
            # Optimize SQLite settings
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA cache_size=10000;")
            conn.execute("PRAGMA temp_store=MEMORY;")
            _connection_pool[key] = conn
        return _connection_pool[key]


def init_db(db_path: str):
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(db_path, timeout=10)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA cache_size=10000;")
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()

def log_prediction(db_path: str, filename: str, emotion: str, confidence: float, image_path: Optional[str] = None):
    """
    Logs a prediction row. This function ensures ts is a string and that
    values bound to SQLite are primitive types (no functions or callables).
    
    Args:
        db_path: Path to SQLite database
        filename: Original filename
        emotion: Detected emotion
        confidence: Confidence score
        image_path: Path to stored image file (optional)
    """
    # Defensive conversions
    try:
        ts = datetime.datetime.now(datetime.UTC).isoformat()
    except Exception:
        # fallback to str(datetime)
        ts = str(datetime.datetime.utcnow())

    if filename is None:
        filename = ""
    else:
        filename = str(filename)

    if emotion is None:
        emotion = ""
    else:
        emotion = str(emotion)

    if image_path is None:
        image_path = ""
    else:
        image_path = str(image_path)

    try:
        confidence_val = float(confidence or 0.0)
    except Exception:
        confidence_val = 0.0

    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        # Check if image_path column exists, if not, add it
        cur.execute("PRAGMA table_info(predictions)")
        columns = [row[1] for row in cur.fetchall()]
        
        if "image_path" not in columns:
            # Migrate schema - add image_path column
            cur.execute("ALTER TABLE predictions ADD COLUMN image_path TEXT")
            conn.commit()
        
        cur.execute(
            "INSERT INTO predictions (ts, filename, image_path, emotion, confidence) VALUES (?, ?, ?, ?, ?)",
            (ts, filename, image_path, emotion, confidence_val)
        )
        conn.commit()
        return cur.lastrowid
    except Exception:
        # On error, close connection and retry with new connection
        with _db_lock:
            thread_id = threading.get_ident()
            key = f"{db_path}_{thread_id}"
            if key in _connection_pool:
                try:
                    _connection_pool[key].close()
                except:
                    pass
                del _connection_pool[key]
        raise

def get_metrics(db_path: str) -> Dict:
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM predictions")
        total = cur.fetchone()[0] or 0
        cur.execute("SELECT emotion, COUNT(*) FROM predictions GROUP BY emotion")
        rows = cur.fetchall()
        by_label = {r[0]: r[1] for r in rows}
        return {"total": total, "by_label": by_label}
    except Exception:
        with _db_lock:
            thread_id = threading.get_ident()
            key = f"{db_path}_{thread_id}"
            if key in _connection_pool:
                try:
                    _connection_pool[key].close()
                except:
                    pass
                del _connection_pool[key]
        raise

def tail_rows(db_path: str, limit: int = 10, offset: int = 0, emotion_filter: Optional[str] = None, 
              min_confidence: Optional[float] = None, max_confidence: Optional[float] = None,
              date_from: Optional[str] = None, date_to: Optional[str] = None) -> Tuple:
    """
    Fetch rows from predictions table with filtering and pagination.
    
    Returns:
        List of tuples: (id, ts, filename, image_path, emotion, confidence) or 
        (ts, filename, image_path, emotion, confidence) depending on query
    """
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        
        # Build query with filters
        query = "SELECT id, ts, filename, image_path, emotion, confidence FROM predictions WHERE 1=1"
        params = []
        
        if emotion_filter:
            query += " AND emotion = ?"
            params.append(emotion_filter)
        
        if min_confidence is not None:
            query += " AND confidence >= ?"
            params.append(min_confidence)
        
        if max_confidence is not None:
            query += " AND confidence <= ?"
            params.append(max_confidence)
        
        if date_from:
            query += " AND ts >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND ts <= ?"
            params.append(date_to)
        
        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cur.execute(query, params)
        return cur.fetchall()
    except Exception:
        with _db_lock:
            thread_id = threading.get_ident()
            key = f"{db_path}_{thread_id}"
            if key in _connection_pool:
                try:
                    _connection_pool[key].close()
                except:
                    pass
                del _connection_pool[key]
        raise


def delete_prediction(db_path: str, prediction_id: int) -> bool:
    """
    Delete a prediction by ID.
    
    Args:
        db_path: Path to SQLite database
        prediction_id: ID of prediction to delete
    
    Returns:
        True if deleted, False otherwise
    """
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM predictions WHERE id = ?", (prediction_id,))
        conn.commit()
        return cur.rowcount > 0
    except Exception:
        with _db_lock:
            thread_id = threading.get_ident()
            key = f"{db_path}_{thread_id}"
            if key in _connection_pool:
                try:
                    _connection_pool[key].close()
                except:
                    pass
                del _connection_pool[key]
        raise


def get_total_count(db_path: str, emotion_filter: Optional[str] = None,
                   min_confidence: Optional[float] = None, max_confidence: Optional[float] = None,
                   date_from: Optional[str] = None, date_to: Optional[str] = None) -> int:
    """Get total count of predictions matching filters."""
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        
        query = "SELECT COUNT(*) FROM predictions WHERE 1=1"
        params = []
        
        if emotion_filter:
            query += " AND emotion = ?"
            params.append(emotion_filter)
        
        if min_confidence is not None:
            query += " AND confidence >= ?"
            params.append(min_confidence)
        
        if max_confidence is not None:
            query += " AND confidence <= ?"
            params.append(max_confidence)
        
        if date_from:
            query += " AND ts >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND ts <= ?"
            params.append(date_to)
        
        cur.execute(query, params)
        return cur.fetchone()[0] or 0
    except Exception:
        with _db_lock:
            thread_id = threading.get_ident()
            key = f"{db_path}_{thread_id}"
            if key in _connection_pool:
                try:
                    _connection_pool[key].close()
                except:
                    pass
                del _connection_pool[key]
        raise
