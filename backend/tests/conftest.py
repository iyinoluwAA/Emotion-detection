import sys
import pathlib
import pytest

# Ensure backend/ (the package root that contains `app/`) is on sys.path so
# `from app import create_app` can be resolved when running pytest from repo root.
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app

@pytest.fixture
def client():
    app = create_app({"TESTING": True})
    return app.test_client()