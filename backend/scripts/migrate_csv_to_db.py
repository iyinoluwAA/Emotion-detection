
import os
import csv
import sys

# ensure project root is on sys.path so "app" package can be imported
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.db_logger import init_db, log_prediction

DB_PATH = os.path.join(PROJECT_ROOT, "predictions.db")
CSV_PATH = os.path.join(PROJECT_ROOT, "predictions_log.csv")

def migrate(csv_path: str, db_path: str):
    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV file not found: {csv_path}")
        return

    init_db(db_path)
    count = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # support older column names
            ts = row.get('timestamp') or row.get('ts') or None
            filename = row.get('filename') or row.get('image') or ''
            emotion = row.get('emotion') or ''
            try:
                confidence = float(row.get('confidence') or 0)
            except Exception:
                confidence = 0.0

            log_prediction(db_path, filename, emotion, confidence)
            count += 1

    print(f"✅ Migrated {count} rows from {csv_path} → {db_path}")

if __name__ == "__main__":
    print("Project root:", PROJECT_ROOT)
    migrate(CSV_PATH, DB_PATH)
