
import cv2
import numpy as np

# Load and preprocess face image
def preprocess_face(image_path, target_size=(48, 48)):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    if len(faces) == 0:
        return None, None

    x, y, w, h = faces[0]  # Just use the first detected face
    face = gray[y:y+h, x:x+w]
    face = cv2.resize(face, target_size)
    face = face.astype('float32') / 255.0
    face = np.expand_dims(face, axis=-1)
    face = np.expand_dims(face, axis=0)
    return face, (x, y, w, h)
