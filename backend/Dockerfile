# backend/Dockerfile — built for Render / local docker
FROM python:3.11-slim

# workdir
WORKDIR /app

# Avoid cache problems, set TERM
ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=xterm

# copy requirements first for layer caching
COPY backend/requirements.txt /app/requirements.txt

# install apt packages needed by OpenCV and common libs
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libgl1 \
      libglib2.0-0 \
      libsm6 \
      libxrender1 \
      libxext6 \
 && rm -rf /var/lib/apt/lists/*

# upgrade pip and install wheels
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy app code
COPY backend/ /app/

# expose port used by the app
EXPOSE 5000
ENV PORT=5000

CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "60"]
