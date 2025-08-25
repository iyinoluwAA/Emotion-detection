# app/__init__.py
import os
import datetime
import csv
import traceback
import logging

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

# ----------------------------
# Module-level config (deterministic)
# ----------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_DIR_DEFAULT = os.path.join(PROJECT_ROOT, "tmp")
LOG_CSV = os.path.join(PROJECT_ROOT, "predictions_log.csv")
DB_PATH = os.path.join(PROJECT_ROOT, "predictions.db")

# App-level defaults (can be overridden via app.config)
DEFAULTS = {
    "MIN_CONFIDENCE": 0.5,
    "MAX_FILE_SIZE": 5 * 1024 * 1024,  # 5 MB
    "TMP_DIR": TMP_DIR_DEFAULT,
    "ALLOWED_EXT": (".jpg", ".jpeg", ".png"),
}

# Ensure tmp dir exists
os.makedirs(DEFAULTS["TMP_DIR"], exist_ok=True)

# Ensure CSV header exists (helpful for older logs)
if not os.path.exists(LOG_CSV):
    try:
        with open(LOG_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "filename", "emotion", "confidence"])
    except Exception:
        # Non-fatal — keep module import light.
        pass


# ----------------------------
# Factory
# ----------------------------
def create_app(config: dict | None = None):
    """
    Create and return the Flask application.
    Heavy imports (model loading, db init) are performed inside this factory
    so importing modules from scripts/tests doesn't trigger expensive work.
    """
    # Merge defaults with provided config
    cfg = DEFAULTS.copy()
    if config:
        cfg.update(config)

    app = Flask(__name__)
    CORS(app)  # you can restrict origins: CORS(app, origins=[...])

    # ---------- file logging setup (after app created) ----------
    LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except Exception:
        # If logs dir cannot be created, continue; app.logger will still work to stdout
        pass

    log_path = os.path.join(LOG_DIR, "app.log")
    try:
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.INFO)  # change to ERROR if you prefer
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(module)s: %(message)s")
        file_handler.setFormatter(formatter)

        # avoid adding duplicate handlers when reloading
        abs_log_path = os.path.abspath(log_path)
        if not any(
            isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", None) == abs_log_path
            for h in app.logger.handlers
        ):
            app.logger.addHandler(file_handler)
            # set app logger level (don't lower if already configured higher)
            app.logger.setLevel(logging.INFO)
    except Exception:
        # If logging can't be configured, keep going — logger will fallback to default handlers.
        app.logger.exception("Failed to configure file logging")

    # Apply config to app
    app.config["MAX_CONTENT_LENGTH"] = cfg["MAX_FILE_SIZE"]
    app.config["TMP_DIR"] = cfg["TMP_DIR"]
    app.config["ALLOWED_EXT"] = cfg["ALLOWED_EXT"]
    app.config["MIN_CONFIDENCE"] = cfg["MIN_CONFIDENCE"]

    # Ensure tmp directory exists (again, per app)
    os.makedirs(app.config["TMP_DIR"], exist_ok=True)

    # Local (deferred) imports — avoid import-time side effects
    from .model_loader import load_emotion_model
    from .db_logger import init_db, log_prediction, get_metrics, tail_rows
    from .utils import preprocess_face

    # Initialize DB
    try:
        init_db(DB_PATH)
        app.logger.info("Initialized SQLite DB at %s", DB_PATH)
    except Exception:
        app.logger.exception("Failed to initialize DB at startup")

    # Load model & labels. Keep these local to the factory (no module-level side effects).
    model = None
    labels = None
    model_version = "unknown"
    try:
        # load_emotion_model may return (model, labels) or (model, labels, version)
        res = load_emotion_model()
        if isinstance(res, tuple) and len(res) == 3:
            model, labels, model_version = res
        elif isinstance(res, tuple) and len(res) == 2:
            model, labels = res
        else:
            # Unexpected return shape - try to be permissive
            try:
                model = res
                labels = None
            except Exception:
                model = None
                labels = None
        app.logger.info("Model loaded: %s (version=%s)", bool(model), model_version)
    except Exception as exc:
        app.logger.exception("Model failed to load at startup: %s", exc)
        model = None
        labels = None
        model_version = "failed"

    # Store in app.config for possible runtime replacement
    app.config["MODEL"] = model
    app.config["LABELS"] = labels
    app.config["MODEL_VERSION"] = model_version

    # ----------------------------
    # Error handlers
    # ----------------------------
    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_file(e):
        return jsonify({"error": "File too large. Max 5MB."}), 413

    # ----------------------------
    # Routes
    # ----------------------------
    @app.route("/")
    def index():
        return jsonify({"status": "ok", "message": "Flask backend running"}), 200

    @app.route("/health", methods=["GET"])
    def health():
        model_loaded = bool(app.config.get("MODEL"))
        labels_obj = app.config.get("LABELS")
        labels_count = len(labels_obj) if labels_obj and hasattr(labels_obj, "__len__") else 0
        return jsonify(
            {
                "ok": True,
                "model_loaded": model_loaded,
                "model_version": app.config.get("MODEL_VERSION"),
                "labels_count": labels_count,
            }
        ), 200

    @app.route("/metrics")
    def metrics():
        try:
            m = get_metrics(DB_PATH)
            recent = tail_rows(DB_PATH, limit=10)
            return jsonify({"ok": True, "metrics": m, "recent": recent}), 200
        except Exception as exc:
            app.logger.exception("Failed to fetch metrics")
            return jsonify({"error": "Failed to fetch metrics", "details": str(exc)}), 500

    @app.route("/logs", methods=["GET"])
    def logs():
        try:
            limit = int(request.args.get("limit", 20))
            limit = max(1, min(200, limit))  # clamp
            rows = tail_rows(DB_PATH, limit=limit)  # tail_rows returns list of tuples
            # convert to list of dicts (id, ts, filename, emotion, confidence)
            result = []
            for r in rows:
                if len(r) == 4:
                    ts, filename, emotion, confidence = r
                    record = {"ts": ts, "filename": filename, "emotion": emotion, "confidence": confidence}
                elif len(r) == 5:
                    _id, ts, filename, emotion, confidence = r
                    record = {"id": _id, "ts": ts, "filename": filename, "emotion": emotion, "confidence": confidence}
                else:
                    record = {"row": r}
                result.append(record)
            return jsonify({"ok": True, "logs": result}), 200
        except Exception as exc:
            app.logger.exception("Failed to fetch logs")
            return jsonify({"error": "failed", "detail": str(exc)}), 500

    @app.route("/detect", methods=["POST"])
    def detect():
        """
        POST form-data: image file under key 'image'
        Returns: JSON {emotion, confidence} or error JSON
        """
        # Use config-stored model/labels (these can be updated at runtime).
        model_local = app.config.get("MODEL")
        labels_local = app.config.get("LABELS") or []

        if model_local is None:
            app.logger.error("Detect called but model not loaded")
            return jsonify({"error": "Model not loaded on Server"}), 503

        # Validate upload presence
        if "image" not in request.files:
            return jsonify({"error": "No image provided."}), 400

        file = request.files["image"]
        filename = secure_filename(file.filename or "upload.jpg")
        if filename == "":
            return jsonify({"error": "Invalid filename"}), 400

        ext = os.path.splitext(filename)[1].lower()
        if ext not in app.config.get("ALLOWED_EXT", (".jpg", ".jpeg", ".png")):
            return jsonify({"error": f"Unsupported file type: {ext}"}), 415

        tmp_dir = app.config.get("TMP_DIR", TMP_DIR_DEFAULT)
        tmp_path = os.path.join(tmp_dir, filename)
        used_filename = filename

        try:
            file.save(tmp_path)

            # Preprocess face - preprocess_face is imported above in factory scope
            res = preprocess_face(tmp_path)
            if isinstance(res, tuple):
                face_array, used_filename = res
            else:
                face_array = res

            if face_array is None:
                app.logger.info("No face detected for file %s", filename)
                return jsonify({"error": "No face detected."}), 400

            # Defensive conversion and validations
            import numpy as np

            try:
                face_input = np.asarray(face_array)
            except Exception as exc:
                app.logger.exception("Failed converting preprocessed face to numpy array")
                return jsonify({"error": "Invalid preprocessed face data."}), 500

            if getattr(face_input, "dtype", None) == object:
                app.logger.error("face_input has object dtype (likely contains None) for file %s", filename)
                return jsonify({"error": "Invalid preprocessed face data (object dtype)."}), 500

            # Ensure batch dim and channel dim
            if face_input.ndim == 2:
                # (H, W) -> (1, H, W, 1)
                face_input = np.expand_dims(np.expand_dims(face_input, axis=-1), axis=0)
            elif face_input.ndim == 3:
                # (H, W, C) -> (1, H, W, C)
                face_input = np.expand_dims(face_input, axis=0)
            elif face_input.ndim == 4:
                # already batched
                pass
            else:
                app.logger.error("Unsupported preprocessed face ndim %s for file %s", getattr(face_input, "ndim", None), filename)
                return jsonify({"error": "Unsupported preprocessed face shape."}), 500

            # sanity checks
            if face_input.shape[0] < 1:
                return jsonify({"error": "Empty batch sent to model."}), 500
            try:
                if not np.isfinite(face_input.astype("float32")).all():
                    app.logger.error("face_input contains non-finite values for file %s", filename)
                    return jsonify({"error": "Preprocessed face contains non-finite values."}), 500
            except Exception:
                app.logger.exception("Failed checking finiteness of face_input")
                return jsonify({"error": "Preprocessed face contains invalid numeric values."}), 500

            # Run prediction
            try:
                preds = model_local.predict(face_input)
            except Exception as exc:
                app.logger.exception("Model predict failed for file %s", filename)
                return jsonify({"error": "Prediction failed", "detail": str(exc)}), 500

            if preds is None:
                return jsonify({"error": "Prediction returned no output"}), 500

            arr = np.asarray(preds)
            if arr.ndim == 2:
                probs = arr[0]
            elif arr.ndim == 1:
                probs = arr
            else:
                app.logger.error("Unexpected prediction shape %s for file %s", getattr(arr, "shape", None), filename)
                return jsonify({"error": "Unexpected prediction shape", "shape": list(getattr(arr, "shape", []))}), 500

            if probs.size == 0:
                return jsonify({"error": "Empty prediction probabilities"}), 500

            idx = int(np.argmax(probs))
            confidence = float(probs[idx])

            # Resolve label safely
            if isinstance(labels_local, dict):
                emotion = labels_local.get(str(idx)) or labels_local.get(idx) or list(labels_local.values())[idx]
            elif isinstance(labels_local, list):
                emotion = labels_local[idx] if 0 <= idx < len(labels_local) else str(idx)
            else:
                emotion = str(idx)

            # Confidence threshold
            min_conf = app.config.get("MIN_CONFIDENCE", DEFAULTS["MIN_CONFIDENCE"])
            if confidence < min_conf:
                try:
                    log_prediction(DB_PATH, used_filename, "low_confidence", confidence)
                except Exception:
                    app.logger.exception("Failed logging low-confidence prediction")
                return jsonify({"error": "low confidence", "confidence": round(confidence, 3)}), 422

            # Log and respond
            try:
                log_prediction(DB_PATH, used_filename, emotion, confidence)
            except Exception:
                app.logger.exception("Failed to log prediction to DB")

            return jsonify({"emotion": emotion, "confidence": round(confidence, 3)}), 200

        except Exception as exc:
            app.logger.exception("detection error for file %s", filename)
            tb = traceback.format_exc()
            return jsonify({"error": "internal error", "detail": str(exc), "trace": tb}), 500

        finally:
            # cleanup tmp file
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                app.logger.exception("failed removing tmp file")

    return app
