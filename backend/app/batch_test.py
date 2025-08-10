import os
import requests
from json import JSONDecodeError

FOLDER = "../test_faces"
ENDPOINT = "http://127.0.0.1:5000/detect"

for filename in os.listdir(FOLDER):
    if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    path = os.path.join(FOLDER, filename)
    with open(path, "rb") as img_file:
        files = {"image": img_file}
        try:
            resp = requests.post(ENDPOINT, files=files)
        except requests.exceptions.ConnectionError as e:
            print(f"⚠️ Could not connect to server: {e}")
            break

        print(f"📸 {filename}", end="")

        # If not JSON, print the raw text
        if 'application/json' not in resp.headers.get('Content-Type',''):
            print(f"\n   ❌ Server returned non-JSON response:\n{resp.text}\n")
            continue

        try:
            data = resp.json()
        except JSONDecodeError:
            print(f"\n   ❌ Invalid JSON:\n{resp.text}\n")
            continue

        if resp.status_code == 200:
            print(f"\n   ✅ Emotion: {data['emotion']} | Confidence: {data['confidence']}")
        else:
            print(f"\n   ❌ Error {resp.status_code}: {data.get('error','Unknown error')}")
