# Dockerfile — backend
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# install system deps needed by opencv/tensorflow wheels
# keep packages minimal to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    wget \
    git \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy minimal files needed for pip install first
COPY requirements.txt .

# Upgrade pip and wheel
RUN python -m pip install --upgrade pip setuptools wheel

# Install numpy first (important for ABI compatibility)
RUN pip install --no-cache-dir "numpy==1.26.1"

# Install opencv wheel next (so it's compiled/selected against the pinned numpy)
RUN pip install --no-cache-dir "opencv-python-headless==4.7.0.72"

# Now install the rest of the Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Create runtime directories and ensure predictable ownership
RUN mkdir -p tmp logs

EXPOSE 5000

# Use the simpler entrypoint to run your app
ENV FLASK_APP=main.py
CMD ["python", "main.py"]
