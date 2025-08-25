#!/usr/bin/env python3
"""
scripts/batch_test.py

Usage (from project root):
    PYTHONPATH=. python scripts/batch_test.py
    PYTHONPATH=. python scripts/batch_test.py --folder test_faces --endpoint http://127.0.0.1:5000/detect

This script looks for images in <project_root>/<folder>.
"""
import os
import sys
import argparse
import mimetypes
import requests
from json import JSONDecodeError

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def iter_images(folder):
    for fn in sorted(os.listdir(folder)):
        if fn.lower().endswith((".jpg", ".jpeg", ".png")):
            yield fn

def main():
    parser = argparse.ArgumentParser(description="Batch test images against /detect endpoint")
    parser.add_argument("--folder", "-f", default="test_faces", help="Folder relative to project root containing test images")
    parser.add_argument("--endpoint", "-e", default="http://127.0.0.1:5000/detect", help="Detect endpoint URL")
    parser.add_argument("--timeout", "-t", type=float, default=10.0, help="Request timeout seconds")
    args = parser.parse_args()

    folder = os.path.join(PROJECT_ROOT, args.folder)
    if not os.path.exists(folder):
        print(f"[ERROR] Test folder not found: {folder}")
        print("Create the folder and add some .jpg/.png test images, or pass --folder path.")
        sys.exit(2)

    print(f"Using folder: {folder}")
    print(f"Endpoint: {args.endpoint}")
    print("Starting batch test...")

    for filename in iter_images(folder):
        path = os.path.join(folder, filename)
        mime_type, _ = mimetypes.guess_type(path)
        if not mime_type:
            mime_type = "application/octet-stream"

        with open(path, "rb") as img_file:
            files = {"image": (filename, img_file, mime_type)}
            try:
                resp = requests.post(args.endpoint, files=files, timeout=args.timeout)
            except requests.exceptions.ConnectionError as e:
                print(f"⚠️ Could not connect to server at {args.endpoint}: {e}")
                sys.exit(3)
            except requests.exceptions.Timeout:
                print(f"⚠️ Request timed out for {filename}")
                continue
            except Exception as e:
                print(f"⚠️ Unexpected error for {filename}: {e}")
                continue

            print(f"📸 {filename}", end="")

            content_type = resp.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                print(f"\n   ❌ Server returned non-JSON response (status {resp.status_code}):\n{resp.text}\n")
                continue

            try:
                data = resp.json()
            except JSONDecodeError:
                print(f"\n   ❌ Invalid JSON (status {resp.status_code}):\n{resp.text}\n")
                continue

            if resp.status_code == 200:
                print(f"\n   ✅ Emotion: {data.get('emotion')} | Confidence: {data.get('confidence')}")
            else:
                print(f"\n   ❌ Error {resp.status_code}: {data.get('error', 'Unknown error')} (detail: {data})")

    print("Batch test finished.")

if __name__ == "__main__":
    main()
