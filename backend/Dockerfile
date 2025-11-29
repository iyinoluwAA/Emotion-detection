# backend/Dockerfile (replace with this)
FROM tensorflow/tensorflow:2.20.0

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# system deps for opencv and runtime model download (curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements (full file)
COPY requirements.txt /app/requirements.txt

# Prepare a requirements file that excludes tensorflow and numpy
# (this avoids installing TF again and prevents numpy/ABI issues)
RUN sed -n '/^tensorflow/!p; /^numpy/!p' /app/requirements.txt > /app/req_no_tf.txt

# Upgrade pip and install Python deps (ignore system-installed packages to avoid uninstall errors)
RUN python -m pip install --upgrade pip setuptools wheel

RUN pip install --no-cache-dir "numpy<2"

# Install requirements in stages to reduce peak memory usage
# Install lighter packages first, then heavy ML packages
RUN pip install --no-cache-dir --upgrade --ignore-installed \
    Flask==3.1.1 \
    flask-cors==4.0.0 \
    h5py>=3.7.0 \
    Pillow>=9.0.0 \
    opencv-python-headless==4.9.0.80 \
    requests>=2.28.0 \
    gunicorn>=23.0.0

# Install torch and transformers separately to manage memory better
# Use CPU-only torch to reduce size (no CUDA dependencies)
# Note: transformers requires PyTorch >= 2.1, so we need 2.1.0 or higher
RUN pip install --no-cache-dir --upgrade --ignore-installed \
    torch>=2.1.0 --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir --upgrade --ignore-installed \
    transformers>=4.30.0

# Note: Model files are downloaded at runtime (app startup), not during Docker build
# This prevents memory issues during build on Render's free tier (512MB limit)

# Copy app (everything in backend)
COPY . /app/

# Copy entrypoint (must exist at backend/scripts/entrypoint.sh)
COPY scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose port (local use only)
EXPOSE 5000

# Entrypoint: download model if missing, then start gunicorn with Render-provided $PORT
ENTRYPOINT ["/app/entrypoint.sh"]
