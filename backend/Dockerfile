# backend/Dockerfile
FROM python:3.11-slim

# Workdir
WORKDIR /app

# Minimal system packages required by opencv/TensorFlow wheel building/execution
# Keep packages small; we remove apt lists afterwards to reduce image size.
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
      build-essential \
      libgl1 \
      libglib2.0-0 \
      curl \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements file (Render will build Docker on their infra so this will be fetched from repo)
COPY requirements.txt /app/requirements.txt

# Upgrade pip & install numpy first to avoid ABI mismatch with opencv/tensorflow compiled wheels
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --default-timeout=60 --retries=5 numpy==1.26.4

# Install the rest of the dependencies with slightly longer timeout & retries
RUN pip install --no-cache-dir --default-timeout=60 --retries=5 -r /app/requirements.txt

# Copy app code
COPY . /app/

# Make the runtime entrypoint executable
COPY scripts/entrypoint.sh /app/scripts/entrypoint.sh
RUN chmod +x /app/scripts/entrypoint.sh

# Expose port used by app
EXPOSE 5000

# Use gunicorn as the process manager and our entrypoint wrapper
# The entrypoint will ensure the model file exists (download if needed) and then exec gunicorn
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app", "--workers", "2", "--threads", "2", "--timeout", "60"]
