Facial Emotion Recognition

A small, self-contained project that detects human emotions from face images using a Keras CNN and a Flask API. This repo is in active development — improvements, tests, and production hardening are ongoing.

🚀 Quick Start
git clone https://github.com/iyinoluwAA/Emotion-detection.git
cd Emotion-detection/backend   # backend lives inside backend/

Virtualenv (local dev)
python -m venv .venv
# Activate (Linux / macOS)
source .venv/bin/activate
# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

Download the model (release asset)

The repo does not include the trained model binary. Use the included script to download it from the release:

chmod +x scripts/download_model.sh
./scripts/download_model.sh   # saves model to backend/models/emotion_model.keras

Start the server (local)
# from backend/
python main.py
# The server will run at:
# http://127.0.0.1:5000  (or a host port mapped by docker-compose)

🪟 Windows / WSL note

Windows users (WSL / Docker Desktop)

The backend was developed on Linux-like environments. If you're on Windows, use WSL2 (recommended) or Docker Desktop with WSL integration to avoid path/permission issues.

If using WSL2:

Run commands from the WSL shell (Ubuntu/etc.) so paths like /home/... and /mnt/c/... behave as expected.

Example to upload a Windows file from WSL with curl:

curl -F "image=@/mnt/c/Users/<you>/Pictures/test.jpg" http://127.0.0.1:5000/detect


If using PowerShell/Windows directly, be aware of line-endings and path differences; Docker is the easiest consistent way (see Docker section).

If you hit Address already in use or port allocation issues: check existing processes or containers listening on port 5000 (ss -ltnp / lsof -i :5000 inside WSL or use Docker Desktop UI).

🐳 Docker (recommended for testing / CI)

Docker provides a reproducible environment (good for Windows users or CI).

Build & run with Compose
# from repo root
docker-compose up --build
# or detached
docker-compose up -d --build

Check runtime logs
docker-compose logs --tail 200 backend
docker-compose logs -f backend

Smoke test from host (after compose maps ports)

Note: container port 5000 may be mapped to a different host port (e.g. 5001). Use docker-compose port backend 5000 to see mapping.

# example (adjust path to your test image):
curl -F "image=@tests/../test_faces/neutral_test.jpg" http://127.0.0.1:5000/detect
curl http://127.0.0.1:5000/health

Running tests inside the container (optional)
docker-compose run --rm backend pytest -q


Notes

The container image installs packages like TensorFlow and OpenCV. On some hosts you may see CPU/GPU informational messages (e.g., Could not find cuda drivers) — those are normal unless you plan to use GPU inside the container.

Docker is the path of least friction for Windows users — it reproduces the Linux dev environment faithfully.

🔌 API
POST /detect

Accepts multipart/form-data with field image (file).

Response on success:

{ "emotion": "happy", "confidence": 0.92 }


Errors:

400 — missing image, invalid file, or no face detected

413 — file too large (max 5MB)

422 — low confidence (below threshold)

500 — internal error

Example with curl:

curl -F "image=@/path/to/face.jpg" http://127.0.0.1:5000/detect

GET /health

Returns a small JSON object describing model status:

{
  "ok": true,
  "model_loaded": true,
  "model_version": "v_unknown",
  "labels_count": 7
}

GET /metrics and GET /logs

GET /metrics returns DB metrics and counts (basic).

GET /logs?limit=20 returns recent logged predictions (the backend exposes a /logs endpoint for the frontend/history view).

🧠 Model

Expected path: backend/models/emotion_model.keras

The release on GitHub stores the trained .keras model as a release asset. The scripts/download_model.sh fetches it to backend/models/.

DO NOT add the model binary to git (too large). Use GitHub releases or separate storage and download during setup or CI.

Labels (model output indices) — important: do not change unless retraining:

0: angry
1: disgust
2: fear
3: happy
4: neutral
5: sad
6: surprise

✅ Tests

Unit tests are included with pytest. Run locally:

pytest -q


CI can run the same tests inside Docker:

docker-compose run --rm backend pytest -q

🔒 Do NOT commit

Add these to .gitignore (or check the repo .gitignore):

# python
__pycache__/
*.pyc
.venv/
venv/

# logs and db
backend/logs/
backend/predictions.db

# models (do not commit trained models)
backend/models/
*.keras
*.h5

# OS
.DS_Store
Thumbs.db


Add a .dockerignore with similar exclusions so your Docker builds are fast and clean (avoid copying venv, logs, large model files into the image context).

🗄️ Logging & DB

Predictions are logged in predictions.db (SQLite) and optionally in predictions_log.csv.

There is a logs/app.log for server-side error logging (ensure backend/logs/ exists).

For production: consider rotating or archiving the DB or switching to a managed DB (Postgres).

🛠️ Development notes / troubleshooting

If you see TensorFlow/OpenCV / NumPy warnings when building in Docker, they usually indicate binary incompatibility or missing GPU drivers. The app will still run on CPU in most cases.

If Address already in use occurs: find and stop the process using the port (e.g., ss -ltnp | grep 5000 or lsof -i :5000 inside WSL). Docker may map container ports to alternate host ports (inspect using docker-compose port).

If uploads fail with Empty reply from server, check container logs (docker-compose logs) and DB file permissions.

🧾 Commit & push (suggested)

From repo root:

git checkout -b feature/backend-fix
git add Dockerfile docker-compose.yml scripts/download_model.sh README.md backend/app backend/tests
git commit -m "Fix DB logger + migration; add robust app factory and migration script; dockerize backend"
git push -u origin feature/backend-fix


If you accidentally staged a large model file:

git rm --cached backend/models/emotion_model.keras
echo "backend/models/" >> .gitignore
git commit -m "Remove large model from repo; add to .gitignore"
git push

➡️ Next steps / roadmap

Finish frontend (React): camera upload + history view that calls /logs or /metrics.

Add more unit/integration tests (end-to-end) and CI (GitHub Actions).

Dockerize frontend and add a docker-compose stack.

Add monitoring + DB rotation for production (or move to Postgres).

📄 License

MIT License — Copyright (c) 2025 AJ