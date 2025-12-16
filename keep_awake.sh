#!/bin/bash
# Keep system awake while training runs
# This prevents sleep/screen timeout

echo "🔄 Keeping system awake for training..."
echo "Press Ctrl+C to stop"

# Prevent sleep using systemd-inhibit (if available)
if command -v systemd-inhibit &> /dev/null; then
    systemd-inhibit --what=sleep:idle:shutdown \
        --who="Emotion Detection Training" \
        --why="Fine-tuning model in progress" \
        --mode=block \
        sleep 3600  # 1 hour
else
    # Fallback: keep CPU active
    echo "Using fallback method: keeping CPU active..."
    timeout 3600 bash -c 'while true; do sleep 1; done'
fi



