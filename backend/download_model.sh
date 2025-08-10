#!/bin/bash

# Create models directory if it doesn't exist
mkdir -p models

# Download the model from the GitHub release
MODEL_URL="https://github.com/iyinoluwAA/Emotion-detection/releases/download/v1.0.0/emotion_model.h5"
MODEL_PATH="models/emotion_model.h5"

echo "Downloading model from $MODEL_URL..."
curl -L "$MODEL_URL" -o "$MODEL_PATH"

echo "Download complete: $MODEL_PATH"