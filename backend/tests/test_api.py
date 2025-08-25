import pytest
import os
from pathlib import Path
from PIL import Image


def create_dummy_image(path: Path):
    """Create a small valid JPEG image for testing."""
    img = Image.new("RGB", (48, 48), color="red")
    img.save(path, "JPEG")


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()

    # Updated to match your actual health endpoint
    assert data["ok"] is True
    assert "model_loaded" in data
    assert "labels_count" in data

def test_detect(client):
    img_path = os.path.join(os.path.dirname(__file__), "..", "test_faces", "neutral_test.jpg")

    with open(img_path, "rb") as f:
        data = {
            "image": (f, "neutral_test.jpg")  # 🔑 must match backend key "image"
        }
        res = client.post(
            "/detect",
            data=data,
            content_type="multipart/form-data",
        )

    assert res.status_code in (200, 422), res.data
    json_data = res.get_json()
    assert "emotion" in json_data or "error" in json_data

