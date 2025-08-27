# backend/Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# system deps required for opencv & downloading (curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# copy only what's needed for pip first (speeds layer cache)
COPY requirements.txt /app/requirements.txt

# upgrade pip
RUN python -m pip install --upgrade pip setuptools wheel

# Install numpy first to avoid ABI mismatch (if you choose a pinned version)
# If you want numpy pinned, uncomment:
# RUN pip install --no-cache-dir numpy==1.26.4

# Install remaining deps
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy app files
COPY . /app/

# make scripts executable
RUN chmod +x /app/scripts/download_model.sh /app/scripts/entrypoint.sh || true

# Use entrypoint to run download at container start and then start gunicorn
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
# default command (can be overridden in Render)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app", "--workers", "2", "--threads", "2", "--timeout", "60"]
