#!/usr/bin/env python3
"""Login to HuggingFace Hub using Python API."""

from huggingface_hub import login

print("🔐 HuggingFace Login")
print("   1. Go to https://huggingface.co/settings/tokens")
print("   2. Create a new token (read + write permissions)")
print("   3. Copy the token")
print()
token = input("Paste your HuggingFace token: ").strip()

if not token:
    print("❌ Token required")
    exit(1)

try:
    login(token=token)
    print("✅ Successfully logged in!")
except Exception as e:
    print(f"❌ Login failed: {e}")
    exit(1)

