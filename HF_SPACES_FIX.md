# 🔧 Fix for Hugging Face Spaces Dockerfile

## Problem
The Dockerfile is trying to chmod `/app/scripts/entrypoint.sh` but the file might be named `entrypoint_hf.sh`.

## Solution

### Option 1: Rename File in Hugging Face (Easiest)

1. Go to your Space: https://huggingface.co/spaces/HimAJ/emotion-detection-api
2. Go to **"Files and versions"** tab
3. Find `scripts/entrypoint_hf.sh`
4. Click on it → Click **"Rename"** or edit icon
5. Rename to: `scripts/entrypoint.sh`
6. Save

### Option 2: Update Dockerfile (If you can't rename)

Replace your `Dockerfile` in Hugging Face with this updated version:

```dockerfile
# Dockerfile for Hugging Face Spaces
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt /app/requirements.txt

# Upgrade pip and install
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY . /app/

# Handle entrypoint (rename if needed, then make executable)
RUN if [ -f /app/scripts/entrypoint_hf.sh ]; then \
        mv /app/scripts/entrypoint_hf.sh /app/scripts/entrypoint.sh; \
    fi && \
    if [ -f /app/scripts/entrypoint.sh ]; then \
        chmod +x /app/scripts/entrypoint.sh; \
    fi

# Hugging Face Spaces uses port 7860
EXPOSE 7860

# Use entrypoint if exists, otherwise run main.py
ENTRYPOINT ["/bin/sh", "-c"]
CMD ["if [ -f /app/scripts/entrypoint.sh ]; then exec /app/scripts/entrypoint.sh; else PORT=7860 exec python main.py; fi"]
```

---

## Quick Fix Steps

**Easiest**: Just rename the file in Hugging Face:
1. Files tab → `scripts/entrypoint_hf.sh`
2. Rename to `scripts/entrypoint.sh`
3. Save
4. Build will restart automatically

**Alternative**: Update Dockerfile with the code above (handles both names)

---

## After Fix

The build should continue and you'll see:
- ✅ Model downloads
- ✅ App startup
- ✅ API ready on port 7860

