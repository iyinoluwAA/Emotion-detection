# Facial Emotion Recognition

A small, self-contained project that detects human emotions from face images using a Keras CNN and a Flask API.  
This repo is in the development stage — improvements, tests, and production hardening are ongoing.

---

## 🚀 Quick Start

```bash
git clone https://github.com/iyinoluwAA/Emotion-detection.git
cd Emotion-detection
if need cd backend

# Create virtual environment
python -m venv .venv
# Activate venv (Windows)
.venv\Scripts\activate
# Activate venv (Linux/macOS)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download model if not present
chmod +x download_model.sh
./download_model.sh   # saves model to models/emotion_model.keras

# Start server
python main.py
The server will run at:
http://127.0.0.1:5000

📂 Files & Commands
main.py — start the Flask app

batch_test.py — send all images in test_faces/ to /detect endpoint

predictions_log.csv — auto-created log of successful predictions

download_model.sh — fetches the model if it’s not included

🧠 Model
Expected path: models/emotion_model.keras

Downloaded automatically from:
https://github.com/iyinoluwAA/Emotion-detection/releases/download/v1.0.0/emotion_model.keras


🔖 Labels (IMPORTANT)
The model predicts emotions in this order:

0: angry
1: disgust
2: fear
3: happy
4: neutral
5: sad
6: surprise
⚠️ Do not change this order unless retraining.

🌐 API
POST /detect — accepts multipart/form-data with field image.

Example response:

{ "emotion": "happy", "confidence": 0.92 }
Errors:

400 — missing image or no face detected

422 — low confidence

📜 How It Works

Model Loading — A pre-trained CNN model is loaded from models/emotion_model.keras.

Face Detection — The uploaded image is scanned for faces.

Preprocessing — The detected face is resized and normalized.

Prediction — The model outputs the most likely emotion and confidence score.

Logging — Predictions are saved to predictions_log.csv.

📊 Credits & Dataset
Model trained on public datasets such as FER-2013 and CK+.
If you use this in production or research, please cite the datasets and any related papers.

📄 License
MIT License
Copyright (c) 2025 AJ
