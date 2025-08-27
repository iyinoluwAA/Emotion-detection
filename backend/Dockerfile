# backend/Dockerfile
FROM tensorflow/tensorflow:2.20.0

WORKDIR /app

# system deps (opencv needs libgl / libglib) and curl for entrypoint download
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
       libgl1 \
       libglib2.0-0 \
       curl \
  && rm -rf /var/lib/apt/lists/*

# copy only requirements first (small)
COPY requirements.txt /app/requirements.txt

# create a requirements file that excludes tensorflow/tensorflow-cpu lines
# (we already have TensorFlow in the base image, so skip installing it)
RUN sed -n '/^tensorflow/!p' /app/requirements.txt > /app/req_no_tf.txt

# upgrade pip, install rest of dependencies (no tensorflow)
RUN python -m pip install --upgrade pip setuptools wheel \
  && pip install --no-cache-dir -r /app/req_no_tf.txt

# copy app code
COPY . /app/

# copy entrypoint & make executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# port for local help; Render provides $PORT at runtime and entrypoint respects it
EXPOSE 5000

ENTRYPOINT ["/app/entrypoint.sh"]
