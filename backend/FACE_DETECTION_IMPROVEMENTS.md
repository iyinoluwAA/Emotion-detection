# Face Detection & Emotion Recognition Improvements - Research

## Key Findings

### 1. Low Light Detection Issues
**Problem**: Face detection fails or has low confidence in dark conditions, even with flashlight.

**Solutions from Research**:
- **Adaptive Histogram Equalization (CLAHE)**: Already implemented, but can be enhanced
- **Gamma Correction**: Adjust brightness/contrast for very dark or very bright images
- **Multi-scale Detection**: Try multiple detection scales more aggressively
- **DNN-based Face Detection**: More robust than Haar cascades (MTCNN, RetinaFace)
- **Brightness Normalization**: Normalize image brightness before detection
- **Multiple Detection Attempts**: Try original, enhanced, and gamma-corrected versions

### 2. Image Display Issues
**Problem**: Images show "No Image" instead of actual captured images.

**Root Causes**:
- Image filename not properly returned from backend
- Image path not stored correctly in database
- Frontend not constructing correct image URL
- Images not being saved to storage

**Solutions**:
- Ensure `image_path` is returned in `/detect` response
- Verify images are saved before logging to database
- Check frontend image URL construction
- Add image modal for viewing full-size images

### 3. Accuracy Improvements
**Research-Based Techniques**:
- **Face Alignment**: Align faces to standard position (eyes level)
- **Data Augmentation**: During preprocessing, apply slight variations
- **Multi-crop Ensemble**: Crop face with multiple padding ratios and average predictions
- **Confidence Threshold Tuning**: Lower threshold for low-light conditions
- **Preprocessing Pipeline**: 
  - Gamma correction for brightness
  - CLAHE for contrast
  - Gaussian blur reduction
  - Sharpening for clarity

### 4. Better Face Detection in Various Lighting
**Techniques**:
1. **Gamma Correction**: `I_out = I_in^(1/gamma)` - brightens dark images
2. **Histogram Equalization**: Global and adaptive (CLAHE)
3. **Contrast Limited Adaptive Histogram Equalization (CLAHE)**: Already using, can tune parameters
4. **Brightness Normalization**: Scale pixel values to optimal range
5. **Multi-pass Detection**: Try detection on original, enhanced, and gamma-corrected versions

## Implementation Plan

### Phase 1: Enhanced Preprocessing (Immediate)
- Add gamma correction for low-light images
- Improve CLAHE parameters
- Add brightness normalization
- Multi-pass detection (try multiple preprocessing approaches)

### Phase 2: Better Face Detection (Short-term)
- Consider DNN-based detection (MTCNN or RetinaFace) for better accuracy
- Multi-scale detection with more aggressive parameters
- Face alignment before emotion prediction

### Phase 3: Image Display Fixes (Immediate)
- Fix image path storage and retrieval
- Add image modal component
- Verify image serving endpoint works

### Phase 4: UI Improvements (Immediate)
- Center charts
- Add image click handlers
- Improve image display in table

## Technical Details

### Gamma Correction Formula
```python
gamma = 0.5  # For dark images (brightens)
gamma = 2.0  # For bright images (darkens)
lookup_table = np.array([((i / 255.0) ** (1.0 / gamma)) * 255 for i in np.arange(0, 256)]).astype("uint8")
corrected = cv2.LUT(image, lookup_table)
```

### Optimal CLAHE Parameters for Low Light
- `clipLimit`: 3.0-4.0 (higher for darker images)
- `tileGridSize`: (8, 8) or (16, 16) for better local adaptation

### Multi-Pass Detection Strategy
1. Try original image
2. Try CLAHE enhanced
3. Try gamma-corrected (gamma=0.5 for dark, 2.0 for bright)
4. Try combination: gamma + CLAHE
5. Use most confident detection

