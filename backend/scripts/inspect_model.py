#!/usr/bin/env python3
"""
Inspect the emotion model to understand its structure and expected labels.
"""
import os
import sys
import numpy as np
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tensorflow.keras.models import load_model

def inspect_model():
    model_path = PROJECT_ROOT / "models" / "emotion_model.keras"
    
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        return
    
    print(f"📦 Loading model from: {model_path}")
    model = load_model(model_path)
    
    print("\n" + "="*60)
    print("MODEL STRUCTURE")
    print("="*60)
    model.summary()
    
    print("\n" + "="*60)
    print("MODEL INPUT/OUTPUT SHAPES")
    print("="*60)
    print(f"Input shape: {model.input_shape}")
    print(f"Output shape: {model.output_shape}")
    
    # Test with dummy input
    print("\n" + "="*60)
    print("TESTING WITH DUMMY INPUT")
    print("="*60)
    dummy_input = np.random.random((1, 48, 48, 1)).astype(np.float32)
    output = model.predict(dummy_input, verbose=0)
    
    print(f"Output shape: {output.shape}")
    print(f"Number of classes: {output.shape[-1]}")
    print(f"Output probabilities: {output[0]}")
    print(f"Sum of probabilities (should be ~1.0): {np.sum(output[0]):.6f}")
    
    # Check if model has metadata
    print("\n" + "="*60)
    print("MODEL METADATA")
    print("="*60)
    if hasattr(model, 'config'):
        print("Model config available")
        if 'layers' in model.config:
            print(f"Number of layers: {len(model.config['layers'])}")
    
    # Expected labels
    print("\n" + "="*60)
    print("EXPECTED LABEL ORDER")
    print("="*60)
    from app.model_loader import DEFAULT_LABELS
    print(f"Default labels: {DEFAULT_LABELS}")
    print(f"Label count: {len(DEFAULT_LABELS)}")
    
    # Check for labels.json
    labels_path = PROJECT_ROOT / "models" / "labels.json"
    if labels_path.exists():
        import json
        with open(labels_path, 'r') as f:
            custom_labels = json.load(f)
        print(f"Custom labels found: {custom_labels}")
    else:
        print("No labels.json found, using DEFAULT_LABELS")
    
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    if output.shape[-1] != len(DEFAULT_LABELS):
        print(f"⚠️  WARNING: Model outputs {output.shape[-1]} classes but DEFAULT_LABELS has {len(DEFAULT_LABELS)} labels!")
        print("   This mismatch could cause incorrect emotion mapping.")
    else:
        print("✅ Model output matches label count")
    
    print("\nTo fix emotion misclassification:")
    print("1. Verify the model was trained with the same label order as DEFAULT_LABELS")
    print("2. Check if labels.json exists and has the correct order")
    print("3. Test with known images to see which emotions are being predicted")

if __name__ == "__main__":
    inspect_model()


