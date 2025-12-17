# 🚀 Hugging Face Spaces Setup Guide

## Why Hugging Face Spaces?

- ✅ **16GB RAM** (plenty for both models)
- ✅ **Free forever** (no credit card)
- ✅ **Docker support** (runs your full Flask app)
- ✅ **Your model is already there** (`HimAJ/asripa-emotion-detection`)
- ✅ **Easy deployment**

---

## Step-by-Step Setup

### Step 1: Create a Space

1. Go to: https://huggingface.co/spaces/new
2. **Owner**: Select your account (`HimAJ`)
3. **Space name**: `emotion-detection-api` (or your choice)
4. **SDK**: Select **"Docker"**
5. **Visibility**: **Public** (required for free tier)
6. Click **"Create Space"**

---

### Step 2: Prepare Your Code

Hugging Face Spaces needs a specific structure. Create these files in your Space:

#### File Structure:
```
emotion-detection-api/
├── Dockerfile
├── app.py (or use your existing main.py)
├── requirements.txt
└── [your backend code]
```

#### Option A: Use Your Existing Backend

1. **Copy your backend folder** to the Space
2. **Create a simple `app.py`** that imports your Flask app:

```python
# app.py
from main import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False)
```

3. **Update `requirements.txt`** to include all dependencies

4. **Create/Update `Dockerfile`**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Expose port (Hugging Face Spaces uses 7860)
EXPOSE 7860

# Run app
CMD ["python", "app.py"]
```

---

### Step 3: Upload Files

1. In your Space, click **"Files and versions"** tab
2. Click **"Add file"** → **"Upload files"**
3. Upload:
   - Your `backend/` folder (or just the files)
   - `requirements.txt`
   - `Dockerfile`
   - `app.py`

Or use Git:
1. Click **"Files and versions"** → **"Use the CLI"**
2. Follow instructions to push via Git

---

### Step 4: Set Environment Variables

1. Go to **"Settings"** tab in your Space
2. Scroll to **"Environment variables"**
3. Add:
   - `ASRIPA_MODEL_ID` = `HimAJ/asripa-emotion-detection`
   - `PORT` = `7860` (Hugging Face default)

---

### Step 5: Deploy

1. Hugging Face will automatically build and deploy
2. Check **"Logs"** tab for build progress
3. Wait ~5-10 minutes for first build
4. Your API will be at: `https://huggingface.co/spaces/HimAJ/emotion-detection-api`

---

## Important Notes

### Port Configuration

Hugging Face Spaces uses port **7860** by default. Update your app:

```python
# In app.py or main.py
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port)
```

### Database & Storage

- **SQLite**: Works, but may be ephemeral (resets on restart)
- **File storage**: Limited, but enough for images
- **Consider**: Using Hugging Face datasets for persistent storage

### API Endpoints

Your endpoints will be available at:
- `https://huggingface.co/spaces/HimAJ/emotion-detection-api/detect`
- `https://huggingface.co/spaces/HimAJ/emotion-detection-api/health`
- etc.

---

## Troubleshooting

### Build Fails
- Check **"Logs"** tab for errors
- Ensure `requirements.txt` has all dependencies
- Verify `Dockerfile` is correct

### Out of Memory
- 16GB should be plenty, but if issues occur:
  - Optimize model loading
  - Use lazy loading

### Database Issues
- SQLite may reset on restart
- Consider using Hugging Face datasets for persistence

---

## Alternative: Simplified API

If full Flask app is complex, you can create a simplified version:

```python
# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Import your model loading logic
from model_loader import load_emotion_model

# Load models at startup
base_model, base_labels = load_emotion_model("base")
asripa_model, asripa_labels = load_emotion_model("fine-tuned")

@app.route("/")
def index():
    return jsonify({"status": "ok"})

@app.route("/detect", methods=["POST"])
def detect():
    # Your detection logic
    pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port)
```

---

## Next Steps

1. **Create Space**: https://huggingface.co/spaces/new
2. **Upload code**: Use Git or web interface
3. **Set env vars**: `ASRIPA_MODEL_ID`
4. **Deploy**: Automatic!
5. **Update frontend**: Point to Hugging Face URL

---

## Resources

- **Hugging Face Spaces Docs**: https://huggingface.co/docs/hub/spaces
- **Docker Spaces Guide**: https://huggingface.co/docs/hub/spaces-sdks-docker

Need help? Let me know!

