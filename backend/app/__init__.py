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
IMAGES_DIR_DEFAULT = os.path.join(PROJECT_ROOT, "images")
LOG_CSV = os.path.join(PROJECT_ROOT, "predictions_log.csv")
DB_PATH = os.path.join(PROJECT_ROOT, "predictions.db")

# App-level defaults (can be overridden via app.config)
DEFAULTS = {
    "MIN_CONFIDENCE": 0.18,  # Lowered to 0.18 for ambiguous cases (was 0.20, originally 0.5)
    "MAX_FILE_SIZE": 5 * 1024 * 1024,  # 5 MB
    "TMP_DIR": TMP_DIR_DEFAULT,
    "IMAGES_DIR": IMAGES_DIR_DEFAULT,
    "ALLOWED_EXT": (".jpg", ".jpeg", ".png"),
    "CORS_ORIGINS": "*",  # Can be overridden for production
}

# Ensure directories exist
os.makedirs(DEFAULTS["TMP_DIR"], exist_ok=True)
os.makedirs(DEFAULTS["IMAGES_DIR"], exist_ok=True)

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
    
    # CORS configuration - allow config override
    cors_origins = cfg.get("CORS_ORIGINS", DEFAULTS["CORS_ORIGINS"])
    if cors_origins == "*":
        CORS(app, resources={r"/*": {"origins": "*"}})
    else:
        # Allow list of origins
        origins_list = cors_origins.split(",") if isinstance(cors_origins, str) else cors_origins
        CORS(app, resources={r"/*": {"origins": origins_list}})

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
    app.config["IMAGES_DIR"] = cfg.get("IMAGES_DIR", DEFAULTS["IMAGES_DIR"])
    app.config["ALLOWED_EXT"] = cfg["ALLOWED_EXT"]
    app.config["MIN_CONFIDENCE"] = cfg["MIN_CONFIDENCE"]
    

    # Ensure tmp directory exists (again, per app)
    os.makedirs(app.config["TMP_DIR"], exist_ok=True)

    # Local (deferred) imports — avoid import-time side effects
    from .model_loader import load_emotion_model
    from .db_logger import init_db, log_prediction, get_metrics, tail_rows, get_total_count, delete_prediction
    from .utils import preprocess_face
    from .image_storage import save_image, get_image_path, ensure_images_dir
    from .validators import validate_image_file, validate_pagination_params, validate_confidence_range
    from .rate_limiter import detect_limiter, logs_limiter, images_limiter, get_client_identifier

    # Initialize DB
    try:
        init_db(DB_PATH)
        app.logger.info("Initialized SQLite DB at %s", DB_PATH)
    except Exception:
        app.logger.exception("Failed to initialize DB at startup")

    # Load model & labels. Keep these local to the factory (no module-level side effects).
    # We'll load models on-demand based on request parameter
    base_model = None
    base_labels = None
    base_model_version = "unknown"
    base_model_type = "unknown"
    finetuned_model = None
    finetuned_labels = None
    finetuned_model_version = "unknown"
    finetuned_model_type = "unknown"
    
    # Load base model by default
    try:
        # load_emotion_model returns (model, labels, version, model_type)
        res = load_emotion_model(force_model='base')
        if isinstance(res, tuple) and len(res) == 4:
            base_model, base_labels, base_model_version, base_model_type = res
        elif isinstance(res, tuple) and len(res) == 3:
            base_model, base_labels, base_model_version = res
            base_model_type = "keras"  # Default for old format
        elif isinstance(res, tuple) and len(res) == 2:
            base_model, base_labels = res
            base_model_type = "keras"  # Default for old format
        else:
            # Unexpected return shape - try to be permissive
            try:
                base_model = res
                base_labels = None
                base_model_type = "keras"
            except Exception:
                base_model = None
                base_labels = None
                base_model_type = "unknown"
        app.logger.info("Base model loaded: %s (version=%s, type=%s)", bool(base_model), base_model_version, base_model_type)
        print(f"[APP] Base model loaded: type={base_model_type}, version={base_model_version}, labels={len(base_labels) if base_labels else 0}")
    except Exception as exc:
        app.logger.exception("Base model failed to load at startup: %s", exc)
        base_model = None
        base_labels = None
        base_model_version = "failed"
        base_model_type = "unknown"
    
    # Try to load fine-tuned model
    try:
        res = load_emotion_model(force_model='fine-tuned')
        if isinstance(res, tuple) and len(res) == 4:
            finetuned_model, finetuned_labels, finetuned_model_version, finetuned_model_type = res
        elif isinstance(res, tuple) and len(res) == 3:
            finetuned_model, finetuned_labels, finetuned_model_version = res
            finetuned_model_type = "keras"
        elif isinstance(res, tuple) and len(res) == 2:
            finetuned_model, finetuned_labels = res
            finetuned_model_type = "keras"
        app.logger.info("Asripa model loaded: %s (version=%s, type=%s)", bool(finetuned_model), finetuned_model_version, finetuned_model_type)
        print(f"[APP] Asripa model loaded: type={finetuned_model_type}, version={finetuned_model_version}")
    except Exception as exc:
        app.logger.warning("Asripa model not available: %s", exc)
        finetuned_model = None
        finetuned_labels = None
        finetuned_model_version = "not-available"
        finetuned_model_type = "unknown"

    # Store in app.config - default to base model
    app.config["BASE_MODEL"] = base_model
    app.config["BASE_LABELS"] = base_labels
    app.config["BASE_MODEL_VERSION"] = base_model_version
    app.config["BASE_MODEL_TYPE"] = base_model_type
    app.config["FINETUNED_MODEL"] = finetuned_model
    app.config["FINETUNED_LABELS"] = finetuned_labels
    app.config["FINETUNED_MODEL_VERSION"] = finetuned_model_version
    app.config["FINETUNED_MODEL_TYPE"] = finetuned_model_type
    # Default to base model
    app.config["MODEL"] = base_model
    app.config["LABELS"] = base_labels
    app.config["MODEL_VERSION"] = base_model_version
    app.config["MODEL_TYPE"] = base_model_type

    # ----------------------------
    # Error handlers (import before routes to ensure proper handling)
    # ----------------------------
    from .error_handlers import register_error_handlers, APIError, ValidationError, NotFoundError, ServiceUnavailableError
    
    register_error_handlers(app)
    
    # Make these available in route scope
    globals()['APIError'] = APIError
    globals()['ValidationError'] = ValidationError
    globals()['NotFoundError'] = NotFoundError
    globals()['ServiceUnavailableError'] = ServiceUnavailableError
    
    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_file(e):
        return jsonify({"error": "File too large", "max_size_mb": app.config.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024) / (1024 * 1024)}), 413

    # ----------------------------
    # Routes
    # ----------------------------
    @app.route("/")
    def index():
        return jsonify({"status": "ok", "message": "Flask backend running"}), 200

    @app.route("/health", methods=["GET"])
    def health():
        """
        Lightweight health check endpoint.
        Optimized for speed - minimal checks to avoid timeouts.
        """
        try:
            # Quick check - don't do expensive operations
            model_loaded = bool(app.config.get("MODEL"))
            model_type = app.config.get("MODEL_TYPE", "unknown")
            model_version = app.config.get("MODEL_VERSION", "unknown")
            
            # Get labels count quickly
            labels_obj = app.config.get("LABELS")
            labels_count = len(labels_obj) if labels_obj and hasattr(labels_obj, "__len__") else 0
            
            return jsonify(
                {
                    "ok": True,
                    "model_loaded": model_loaded,
                    "model_type": model_type,
                    "model_version": model_version,
                    "labels_count": labels_count,
                }
            ), 200
        except Exception as e:
            # Even if there's an error, return 200 to indicate service is running
            # This prevents false "offline" status
            app.logger.warning(f"Health check error (non-fatal): {e}")
            return jsonify(
                {
                    "ok": True,
                    "model_loaded": False,
                    "model_type": "unknown",
                    "model_version": "unknown",
                    "labels_count": 0,
                    "warning": "Health check had minor issues but service is running",
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
        """
        GET /logs?limit=20&offset=0&emotion=happy&min_confidence=0.5&max_confidence=1.0&date_from=2024-01-01&date_to=2024-12-31
        
        Returns paginated and filtered logs.
        """
        # Rate limiting
        client_id = get_client_identifier(request)
        is_allowed, remaining = logs_limiter.is_allowed(client_id)
        if not is_allowed:
            return jsonify({
                "error": "Rate limit exceeded",
                "detail": f"Maximum {logs_limiter.max_requests} requests per {logs_limiter.window_seconds} seconds",
                "retry_after": logs_limiter.window_seconds,
            }), 429
        
        try:
            # Validate pagination
            limit, offset, pagination_error = validate_pagination_params(
                request.args.get("limit"),
                request.args.get("offset"),
            )
            if pagination_error:
                return jsonify({"error": pagination_error}), 400
            
            # Validate confidence range
            min_confidence, max_confidence, confidence_error = validate_confidence_range(
                request.args.get("min_confidence"),
                request.args.get("max_confidence"),
            )
            if confidence_error:
                return jsonify({"error": confidence_error}), 400
            
            # Filters
            emotion_filter = request.args.get("emotion", None)
            if emotion_filter and emotion_filter.strip():
                emotion_filter = emotion_filter.strip()
            else:
                emotion_filter = None
            
            date_from = request.args.get("date_from", None)
            date_to = request.args.get("date_to", None)
            
            # Fetch data
            rows = tail_rows(
                DB_PATH,
                limit=limit,
                offset=offset,
                emotion_filter=emotion_filter,
                min_confidence=min_confidence,
                max_confidence=max_confidence,
                date_from=date_from,
                date_to=date_to,
            )
            
            total = get_total_count(
                DB_PATH,
                emotion_filter=emotion_filter,
                min_confidence=min_confidence,
                max_confidence=max_confidence,
                date_from=date_from,
                date_to=date_to,
            )
            
            # Convert to list of dicts
            result = []
            for r in rows:
                if len(r) == 6:
                    _id, ts, filename, image_path, emotion, confidence = r
                    record = {
                        "id": _id,
                        "ts": ts,
                        "filename": filename,
                        "image_path": image_path or filename,  # Fallback to filename if no image_path
                        "emotion": emotion,
                        "confidence": confidence,
                    }
                elif len(r) == 5:
                    _id, ts, filename, emotion, confidence = r
                    record = {
                        "id": _id,
                        "ts": ts,
                        "filename": filename,
                        "image_path": filename,  # Fallback
                        "emotion": emotion,
                        "confidence": confidence,
                    }
                elif len(r) == 4:
                    ts, filename, emotion, confidence = r
                    record = {
                        "ts": ts,
                        "filename": filename,
                        "image_path": filename,  # Fallback
                        "emotion": emotion,
                        "confidence": confidence,
                    }
                else:
                    record = {"row": r}
                result.append(record)
            
            return jsonify({
                "ok": True,
                "logs": result,
                "pagination": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset + limit) < total,
                },
            }), 200
        except Exception as exc:
            app.logger.exception("Failed to fetch logs")
            return jsonify({"error": "Failed to fetch logs", "detail": str(exc)}), 500

    @app.route("/logs/<int:prediction_id>", methods=["DELETE"])
    def delete_log(prediction_id: int):
        """
        DELETE /logs/<id>
        
        Delete a prediction by ID.
        """
        # Rate limiting
        client_id = get_client_identifier(request)
        is_allowed, remaining = logs_limiter.is_allowed(client_id)
        if not is_allowed:
            return jsonify({
                "error": "Rate limit exceeded",
                "detail": f"Maximum {logs_limiter.max_requests} requests per {logs_limiter.window_seconds} seconds",
                "retry_after": logs_limiter.window_seconds,
            }), 429
        
        try:
            # Delete from database
            deleted = delete_prediction(DB_PATH, prediction_id)
            
            if not deleted:
                return jsonify({"error": "Prediction not found"}), 404
            
            # Optionally delete associated image file
            from .image_storage import delete_image
            # Note: We'd need to fetch the image_path first, but for now just delete from DB
            # You can enhance this later to also delete the image file
            
            return jsonify({"ok": True, "message": "Prediction deleted successfully"}), 200
        except Exception as exc:
            app.logger.exception(f"Failed to delete prediction {prediction_id}")
            return jsonify({"error": "Failed to delete prediction", "detail": str(exc)}), 500

    @app.route("/detect", methods=["POST"])
    def detect():
        """
        POST form-data: image file under key 'image'
        Returns: JSON {emotion, confidence} or error JSON
        """
        # Rate limiting
        client_id = get_client_identifier(request)
        is_allowed, remaining = detect_limiter.is_allowed(client_id)
        if not is_allowed:
            return jsonify({
                "error": "Rate limit exceeded",
                "detail": f"Maximum {detect_limiter.max_requests} requests per {detect_limiter.window_seconds} seconds",
                "retry_after": detect_limiter.window_seconds,
            }), 429
        
        # Get model selection from query parameter (default: 'base')
        model_selection = request.args.get("model", "base").lower()
        if model_selection == "fine-tuned" or model_selection == "finetuned":
            model_local = app.config.get("FINETUNED_MODEL")
            labels_local = app.config.get("FINETUNED_LABELS") or []
            model_type = app.config.get("FINETUNED_MODEL_TYPE", "keras")
            model_version = app.config.get("FINETUNED_MODEL_VERSION", "unknown")
            if model_local is None:
                app.logger.warning("Asripa model requested but not available, using base model")
                model_local = app.config.get("BASE_MODEL")
                labels_local = app.config.get("BASE_LABELS") or []
                model_type = app.config.get("BASE_MODEL_TYPE", "keras")
                model_version = app.config.get("BASE_MODEL_VERSION", "unknown")
        else:
            # Use base model (default)
            model_local = app.config.get("BASE_MODEL")
            labels_local = app.config.get("BASE_LABELS") or []
            model_type = app.config.get("BASE_MODEL_TYPE", "keras")
            model_version = app.config.get("BASE_MODEL_VERSION", "unknown")
        
        app.logger.info(f"Using model: {model_selection} (version: {model_version})")

        if model_local is None:
            app.logger.error("Detect called but model not loaded")
            raise ServiceUnavailableError("Model not loaded on server")
        
        print(f"[DETECT] Using model type: {model_type}")

        # Validate upload presence
        if "image" not in request.files:
            raise ValidationError("No image provided")
        
        file = request.files["image"]
        
        # Comprehensive validation
        is_valid, error_msg, filename = validate_image_file(
            file,
            max_size=app.config.get("MAX_CONTENT_LENGTH", DEFAULTS["MAX_FILE_SIZE"]),
            allowed_extensions=app.config.get("ALLOWED_EXT", DEFAULTS["ALLOWED_EXT"]),
        )
        
        if not is_valid:
            raise ValidationError(error_msg)

        tmp_dir = app.config.get("TMP_DIR", TMP_DIR_DEFAULT)
        tmp_path = os.path.join(tmp_dir, filename)
        used_filename = filename

        try:
            # Save file and verify it was saved
            file.save(tmp_path)
            if not os.path.exists(tmp_path):
                app.logger.error("Failed to save uploaded file to %s", tmp_path)
                raise ValidationError("Failed to save uploaded image")
            
            file_size = os.path.getsize(tmp_path)
            if file_size == 0:
                app.logger.error("Saved file is empty: %s", tmp_path)
                raise ValidationError("Uploaded image is empty")
            
            print(f"[DETECT] Saved file: {tmp_path}, size: {file_size} bytes")
            app.logger.info("Saved file: %s, size: %d bytes", tmp_path, file_size)

            # Import numpy for both paths
            import numpy as np

            # Handle ViT and Keras models differently
            if model_type == "vit":
                # Vision Transformer model - needs RGB PIL Image
                from app.vit_utils import preprocess_face_for_vit, predict_with_vit
                from PIL import Image
                
                face_image, used_filename = preprocess_face_for_vit(tmp_path)
                if face_image is None:
                    app.logger.warning("No face detected for file %s (size: %d bytes)", filename, file_size)
                    raise ValidationError("No face detected in image. Please ensure your face is clearly visible, well-lit, and facing the camera.")
                
                # Run ViT prediction
                idx, confidence, all_probs = predict_with_vit(model_local, face_image, labels_local)
                emotion = labels_local[idx] if idx < len(labels_local) else str(idx)
                
                # Debug output
                sorted_probs = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)
                app.logger.info(f"Prediction probabilities for {filename} (sorted): {sorted_probs}")
                print(f"[DETECT] All emotion probabilities (sorted by confidence):")
                for emo, prob in sorted_probs:
                    marker = " <-- SELECTED" if emo == emotion else ""
                    print(f"  {emo}: {prob:.3f}{marker}")
                print(f"[DETECT] Predicted emotion: {emotion}, confidence: {confidence:.3f}")
                
                # Warn if happy probability is suspiciously low (potential misclassification)
                happy_prob = all_probs.get('happy', 0.0)
                if happy_prob < 0.15 and confidence > 0.3 and emotion != 'happy':
                    app.logger.warning(f"⚠️  Low happy probability ({happy_prob:.3f}) but high confidence ({confidence:.3f}) for {emotion}. Possible misclassification.")
                    print(f"[DETECT] ⚠️  WARNING: Happy probability is very low ({happy_prob:.3f}) - possible misclassification")
                
                # Convert to numpy array format for compatibility with rest of code
                probs = np.array([all_probs.get(labels_local[i] if i < len(labels_local) else f"class_{i}", 0.0) 
                                 for i in range(len(labels_local))])
            else:
                # Keras model - existing code path
                # Preprocess face - preprocess_face is imported above in factory scope
                res = preprocess_face(tmp_path)
                if isinstance(res, tuple):
                    face_array, used_filename = res
                else:
                    face_array = res

                if face_array is None:
                    app.logger.warning("No face detected for file %s (size: %d bytes)", filename, file_size)
                    raise ValidationError("No face detected in image. Please ensure your face is clearly visible, well-lit, and facing the camera.")

                # Defensive conversion and validations (numpy already imported above)
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
                    preds = model_local.predict(face_input, verbose=0)
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
                
                # Verify model output matches expected number of classes
                expected_classes = len(labels_local) if isinstance(labels_local, (list, dict)) else 7
                if len(probs) != expected_classes:
                    app.logger.warning(f"Model output has {len(probs)} classes but labels have {expected_classes}. Labels: {labels_local}")
                    print(f"[WARNING] Model output shape mismatch: {len(probs)} classes vs {expected_classes} labels")

                idx = int(np.argmax(probs))
                confidence = float(probs[idx])
                
                # Debug: Log all prediction probabilities to understand model behavior
                all_probs = {}
                for i in range(len(probs)):
                    if isinstance(labels_local, list) and i < len(labels_local):
                        all_probs[labels_local[i]] = float(probs[i])
                    elif isinstance(labels_local, dict):
                        label_key = str(i) if str(i) in labels_local else i if i in labels_local else f"class_{i}"
                        all_probs[label_key] = float(probs[i])
                    else:
                        all_probs[str(i)] = float(probs[i])
                
                # Sort by probability (highest first) for easier debugging
                sorted_probs = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)
                app.logger.info(f"Prediction probabilities for {filename} (sorted): {sorted_probs}")
                print(f"[DETECT] All emotion probabilities (sorted by confidence):")
                for emotion, prob in sorted_probs:
                    marker = " <-- SELECTED" if emotion == (labels_local[idx] if isinstance(labels_local, list) and idx < len(labels_local) else str(idx)) else ""
                    print(f"  {emotion}: {prob:.3f}{marker}")
                print(f"[DETECT] Predicted emotion index: {idx}, confidence: {confidence:.3f}")
                print(f"[DETECT] Available labels: {labels_local}")

                # Resolve label safely
                if isinstance(labels_local, dict):
                    emotion = labels_local.get(str(idx)) or labels_local.get(idx) or list(labels_local.values())[idx]
                elif isinstance(labels_local, list):
                    emotion = labels_local[idx] if 0 <= idx < len(labels_local) else str(idx)
                else:
                    emotion = str(idx)
                
                print(f"[DETECT] Mapped emotion label: {emotion}")

            # Save image even for low confidence (for debugging/analysis)
            images_dir = app.config.get("IMAGES_DIR", IMAGES_DIR_DEFAULT)
            stored_filename = None
            try:
                stored_filename = save_image(tmp_path, images_dir, used_filename)
            except Exception:
                app.logger.exception("Failed to save image, continuing without storage")
            
            # Confidence threshold - slightly lower for better detection in challenging conditions
            # But still maintain quality standards
            min_conf = app.config.get("MIN_CONFIDENCE", DEFAULTS["MIN_CONFIDENCE"])
            # Allow slightly lower confidence (0.45) but warn user
            if confidence < min_conf:
                try:
                    log_prediction(DB_PATH, used_filename, "low_confidence", confidence, stored_filename)
                except Exception:
                    app.logger.exception("Failed logging low-confidence prediction")
                return jsonify({
                    "error": "low confidence",
                    "confidence": round(confidence, 3),
                    "filename": stored_filename or used_filename,
                }), 422

            # Log and respond (image already saved above)
            try:
                log_prediction(DB_PATH, used_filename, emotion, confidence, stored_filename)
            except Exception:
                app.logger.exception("Failed to log prediction to DB")

            # Return all probabilities for debugging (frontend can use this to show top emotions)
            all_emotion_probs = {}
            if model_type == "vit":
                # For ViT, all_probs already contains the dict
                all_emotion_probs = {k: round(v, 4) for k, v in all_probs.items()}
            else:
                # For Keras, build from probs array
                for i in range(len(probs)):
                    if isinstance(labels_local, list) and i < len(labels_local):
                        all_emotion_probs[labels_local[i]] = round(float(probs[i]), 4)
                    elif isinstance(labels_local, dict):
                        label_key = str(i) if str(i) in labels_local else i if i in labels_local else f"class_{i}"
                        all_emotion_probs[label_key] = round(float(probs[i]), 4)
            
            return jsonify({
                "emotion": emotion,
                "confidence": round(confidence, 3),
                "filename": stored_filename or used_filename,
                "all_probabilities": all_emotion_probs,  # Include all probabilities for debugging
                "model": model_selection,
                "model_version": model_version,
            }), 200

        except (ValidationError, APIError, NotFoundError, ServiceUnavailableError) as exc:
            # Let Flask's error handler process these
            raise
        except Exception as exc:
            app.logger.exception("detection error for file %s", filename)
            tb = traceback.format_exc()
            return jsonify({"error": "internal error", "detail": str(exc), "trace": tb}), 500

        finally:
            # cleanup tmp file (image is already saved to images/ if successful)
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                app.logger.exception("failed removing tmp file")

    # ----------------------------
    # Image serving endpoint
    # ----------------------------
    @app.route("/images/<filename>", methods=["GET"])
    def serve_image(filename: str):
        """
        Serve stored images.
        GET /images/{filename}
        """
        from flask import send_from_directory, abort
        
        # Rate limiting
        client_id = get_client_identifier(request)
        is_allowed, remaining = images_limiter.is_allowed(client_id)
        if not is_allowed:
            return jsonify({
                "error": "Rate limit exceeded",
                "detail": f"Maximum {images_limiter.max_requests} requests per {images_limiter.window_seconds} seconds",
                "retry_after": images_limiter.window_seconds,
            }), 429
        
        try:
            images_dir = app.config.get("IMAGES_DIR", IMAGES_DIR_DEFAULT)
            image_path = get_image_path(images_dir, filename)
            
            if not image_path:
                app.logger.warning("Image not found: %s (checked in %s)", filename, images_dir)
                abort(404)
            
            # Extract the actual filename from the path (in case secure_filename changed it)
            actual_filename = os.path.basename(image_path)
            
            return send_from_directory(
                images_dir,
                actual_filename,
                mimetype="image/jpeg",  # Default, will be auto-detected
            )
        except Exception as exc:
            app.logger.exception("Failed to serve image %s", filename)
            return jsonify({"error": "Failed to serve image", "detail": str(exc)}), 500

    return app
