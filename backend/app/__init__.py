from flask import Flask, request, jsonify
from .model_loader import load_emotion_model
from .utils import preprocess_face
import datetime
import os
import csv


def create_app():
    app = Flask(__name__)

    # Load model and labels
    model, labels = load_emotion_model()

    # Ensure log file exists
    LOG_FILE = os.path.join(os.getcwd(), 'predictions_log.csv')
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'emotion', 'confidence'])

    @app.route('/')
    def index():
        return '✅ Flask backend is running.'

    @app.route('/detect', methods=['POST'])
    def detect_emotion():
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400

        file = request.files['image']
        save_path = f'/tmp/{file.filename}'
        file.save(save_path)

        face, _ = preprocess_face(save_path)
        if face is None:
            return jsonify({'error': 'No face detected'}), 400

        predictions = model.predict(face)[0]
        label_index = int(predictions.argmax())
        emotion    = labels[label_index]       # ← integer index
        confidence = float(predictions.max())

        MIN_CONFIDENCE = 0.5
        if confidence < MIN_CONFIDENCE:
            return jsonify({
                'error': 'Low confidence in prediction.',
                'confidence': round(confidence, 3)
            }), 422

        # Log to CSV
        with open(LOG_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.datetime.now().isoformat(), emotion, round(confidence, 3)])

        return jsonify({'emotion': emotion, 'confidence': round(confidence, 3)})

    return app
