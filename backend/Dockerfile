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

RUN pip install --no-cache-dir --upgrade --ignore-installed -r /app/req_no_tf.txt

# Copy app (everything in backend)
COPY . /app/

# Copy entrypoint (must exist at backend/scripts/entrypoint.sh)
COPY scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose port (local use only)
EXPOSE 5000

# Entrypoint: download model if missing, then start gunicorn with Render-provided $PORT
ENTRYPOINT ["/app/entrypoint.sh"]
