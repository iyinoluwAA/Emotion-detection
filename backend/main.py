# main.py
import os
import logging

# Make PROJECT_ROOT explicit so module-level code in the container works reliably
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Ensure logs dir exists
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Configure file logging (keeps container stdout clean and persists errors)
logfile = os.path.join(LOG_DIR, "app.log")
handler = logging.FileHandler(logfile)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(module)s: %(message)s")
handler.setFormatter(formatter)

root_logger = logging.getLogger()
# Add handler only if not already added (avoids duplicates in dev reload)
if not any(isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", "") == logfile for h in root_logger.handlers):
    root_logger.addHandler(handler)

# Import factory after logging and directory setup so imports don't crash during bootstrap
from app import create_app

# Create app (allow env-driven config if needed)
app = create_app()

if __name__ == "__main__":
    # allow overriding host/port via env (useful in Docker)
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", os.environ.get("FLASK_RUN_PORT", 5000)))
    debug = os.environ.get("FLASK_DEBUG", "0") in ("1", "true", "True")
    app.logger.info("Starting app on %s:%s (debug=%s)", host, port, debug)
    app.run(host=host, port=port, debug=debug)
