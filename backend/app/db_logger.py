# app/db_logger.py
import sqlite3
import os
import datetime
from typing import Dict, Tuple

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    filename TEXT,
    emotion TEXT,
    confidence REAL
);
"""

def init_db(db_path: str):
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(db_path, timeout=10)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()

def log_prediction(db_path: str, filename: str, emotion: str, confidence: float):
    """
    Logs a prediction row. This function ensures ts is a string and that
    values bound to SQLite are primitive types (no functions or callables).
    """
    # Defensive conversions
    try:
        ts = datetime.datetime.utcnow().isoformat()
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

    try:
        confidence_val = float(confidence or 0.0)
    except Exception:
        confidence_val = 0.0

    conn = sqlite3.connect(db_path, timeout=10)
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO predictions (ts, filename, emotion, confidence) VALUES (?, ?, ?, ?)",
            (ts, filename, emotion, confidence_val)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

def get_metrics(db_path: str) -> Dict:
    conn = sqlite3.connect(db_path, timeout=10)
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM predictions")
        total = cur.fetchone()[0] or 0
        cur.execute("SELECT emotion, COUNT(*) FROM predictions GROUP BY emotion")
        rows = cur.fetchall()
        by_label = {r[0]: r[1] for r in rows}
        return {"total": total, "by_label": by_label}
    finally:
        conn.close()

def tail_rows(db_path: str, limit: int = 10) -> Tuple:
    conn = sqlite3.connect(db_path, timeout=10)
    try:
        cur = conn.cursor()
        cur.execute("SELECT ts, filename, emotion, confidence FROM predictions ORDER BY id DESC LIMIT ?", (limit,))
        return cur.fetchall()
    finally:
        conn.close()
