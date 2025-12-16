#!/usr/bin/env python3
"""
Compare base model (92.2%) vs fine-tuned model (78.26%) on test images.

Usage:
    python3 backend/scripts/compare_models.py <image_path>
    python3 backend/scripts/compare_models.py backend/images/
"""

import sys
import argparse
from pathlib import Path
from PIL import Image
import torch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app.vit_utils import preprocess_face_for_vit, predict_with_vit


def load_base_model():
    """Load the original 92.2% model directly from HuggingFace."""
    print("\n" + "="*70)
    print("📥 Loading BASE MODEL (92.2% accuracy)")
    print("="*70)
    
    try:
        from transformers import AutoImageProcessor, AutoModelForImageClassification
        
        model_id = "HardlyHumans/Facial-expression-detection"
        print(f"   Loading: {model_id}")
        
        processor = AutoImageProcessor.from_pretrained(model_id)
        model = AutoModelForImageClassification.from_pretrained(model_id)
        
        # Get labels
        raw_labels = [model.config.id2label[i] for i in range(len(model.config.id2label))]
        label_map = {
            'anger': 'angry',
            'disgust': 'disgust',
            'fear': 'fear',
            'happy': 'happy',
            'neutral': 'neutral',
            'sad': 'sad',
            'surprise': 'surprise',
            'contempt': 'contempt'
        }
        labels = [label_map.get(label.lower(), label.lower()) for label in raw_labels]
        
        model_dict = {'model': model, 'processor': processor, 'type': 'vit'}
        print(f"✅ Base model loaded: 92.2% accuracy")
        return model_dict, labels
    except Exception as e:
        print(f"❌ Failed to load base model: {e}")
        import traceback
        traceback.print_exc()
        raise


def load_finetuned_model():
    """Load the fine-tuned 78.26% model directly."""
    print("\n" + "="*70)
    print("📥 Loading FINE-TUNED MODEL (78.26% accuracy)")
    print("="*70)
    
    try:
        from transformers import AutoImageProcessor, AutoModelForImageClassification
        
        repo_root = Path(__file__).parent.parent.parent
        fine_tuned_dir = repo_root / "backend" / "models" / "fine_tuned_vit"
        
        if not (fine_tuned_dir / "model.safetensors").exists():
            raise FileNotFoundError(f"Fine-tuned model not found: {fine_tuned_dir}")
        
        print(f"   Loading from: {fine_tuned_dir}")
        
        processor = AutoImageProcessor.from_pretrained(str(fine_tuned_dir), local_files_only=True)
        model = AutoModelForImageClassification.from_pretrained(str(fine_tuned_dir), local_files_only=True)
        
        # Get labels
        raw_labels = [model.config.id2label[i] for i in range(len(model.config.id2label))]
        label_map = {
            'anger': 'angry',
            'disgust': 'disgust',
            'fear': 'fear',
            'happy': 'happy',
            'neutral': 'neutral',
            'sad': 'sad',
            'surprise': 'surprise',
            'contempt': 'contempt'
        }
        labels = [label_map.get(label.lower(), label.lower()) for label in raw_labels]
        
        model_dict = {'model': model, 'processor': processor, 'type': 'vit'}
        print(f"✅ Fine-tuned model loaded: 78.26% accuracy")
        return model_dict, labels
    except Exception as e:
        print(f"❌ Failed to load fine-tuned model: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_image(image_path, model_dict, labels, model_name):
    """Test a single image with a model."""
    print(f"\n{'─'*70}")
    print(f"🧪 Testing with {model_name}")
    print(f"{'─'*70}")
    
    try:
        # Preprocess image
        face_image, _ = preprocess_face_for_vit(str(image_path))
        if face_image is None:
            print(f"❌ No face detected in {image_path}")
            return None
        
        # Predict
        idx, confidence, all_probs = predict_with_vit(model_dict, face_image, labels)
        emotion = labels[idx] if idx < len(labels) else str(idx)
        
        # Sort probabilities
        sorted_probs = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)
        
        print(f"📊 Results:")
        print(f"   Predicted: {emotion} (confidence: {confidence:.3f})")
        print(f"   Top 3 predictions:")
        for i, (emo, prob) in enumerate(sorted_probs[:3], 1):
            marker = " ⭐" if emo == emotion else ""
            print(f"     {i}. {emo}: {prob:.3f}{marker}")
        
        return {
            'emotion': emotion,
            'confidence': confidence,
            'all_probs': all_probs,
            'sorted_probs': sorted_probs
        }
    except Exception as e:
        print(f"❌ Error testing image: {e}")
        import traceback
        traceback.print_exc()
        return None


def compare_models(image_path):
    """Compare both models on the same image."""
    image_path = Path(image_path)
    
    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        return
    
    print("\n" + "="*70)
    print("🔬 MODEL COMPARISON TEST")
    print("="*70)
    print(f"📸 Image: {image_path}")
    
    try:
        # Load base model (92.2%)
        base_model_dict, base_labels = load_base_model()
        
        # Test with base model
        base_result = test_image(image_path, base_model_dict, base_labels, "BASE MODEL (92.2%)")
        
        # Load fine-tuned model (78.26%)
        finetuned_model_dict, finetuned_labels = load_finetuned_model()
        
        # Test with fine-tuned model
        finetuned_result = test_image(image_path, finetuned_model_dict, finetuned_labels, "FINE-TUNED MODEL (78.26%)")
        
        # Compare results
        print("\n" + "="*70)
        print("📊 COMPARISON SUMMARY")
        print("="*70)
        
        if base_result and finetuned_result:
            print(f"\n{'Model':<30} {'Emotion':<15} {'Confidence':<12} {'Happy Prob':<12} {'Surprise Prob':<12}")
            print("-" * 70)
            
            base_happy = base_result['all_probs'].get('happy', 0.0)
            base_surprise = base_result['all_probs'].get('surprise', 0.0)
            finetuned_happy = finetuned_result['all_probs'].get('happy', 0.0)
            finetuned_surprise = finetuned_result['all_probs'].get('surprise', 0.0)
            
            print(f"{'BASE (92.2%)':<30} {base_result['emotion']:<15} {base_result['confidence']:.3f}        {base_happy:.3f}        {base_surprise:.3f}")
            print(f"{'FINE-TUNED (78.26%)':<30} {finetuned_result['emotion']:<15} {finetuned_result['confidence']:.3f}        {finetuned_happy:.3f}        {finetuned_surprise:.3f}")
            
            # Analysis
            print(f"\n🔍 Analysis:")
            if base_result['emotion'] != finetuned_result['emotion']:
                print(f"   ⚠️  Models disagree!")
                print(f"      Base: {base_result['emotion']} ({base_result['confidence']:.3f})")
                print(f"      Fine-tuned: {finetuned_result['emotion']} ({finetuned_result['confidence']:.3f})")
            
            if finetuned_happy > base_happy:
                print(f"   ✅ Fine-tuned model has HIGHER happy probability (+{finetuned_happy - base_happy:.3f})")
            elif base_happy > finetuned_happy:
                print(f"   ⚠️  Base model has HIGHER happy probability (+{base_happy - finetuned_happy:.3f})")
            
            if finetuned_surprise > base_surprise:
                print(f"   ✅ Fine-tuned model has HIGHER surprise probability (+{finetuned_surprise - base_surprise:.3f})")
            elif base_surprise > finetuned_surprise:
                print(f"   ⚠️  Base model has HIGHER surprise probability (+{base_surprise - finetuned_surprise:.3f})")
            
            # Overall confidence comparison
            if finetuned_result['confidence'] > base_result['confidence']:
                print(f"   ✅ Fine-tuned model is MORE confident (+{finetuned_result['confidence'] - base_result['confidence']:.3f})")
            elif base_result['confidence'] > finetuned_result['confidence']:
                print(f"   ⚠️  Base model is MORE confident (+{base_result['confidence'] - finetuned_result['confidence']:.3f})")
        else:
            print("❌ Could not compare - one or both models failed")
    
    except Exception as e:
        print(f"❌ Error during comparison: {e}")
        import traceback
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(description="Compare base vs fine-tuned models")
    parser.add_argument("image_path", help="Path to image file or directory")
    args = parser.parse_args()
    
    image_path = Path(args.image_path)
    
    if image_path.is_file():
        compare_models(image_path)
    elif image_path.is_dir():
        # Test all images in directory
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        images = [f for f in image_path.iterdir() if f.suffix.lower() in image_extensions]
        
        if not images:
            print(f"❌ No images found in {image_path}")
            return
        
        print(f"Found {len(images)} images. Testing each...")
        for img_path in images:
            compare_models(img_path)
            print("\n" + "="*70 + "\n")
    else:
        print(f"❌ Invalid path: {image_path}")


if __name__ == "__main__":
    main()

