import os.path

import cv2
import numpy as np
from django.conf import settings
import tensorflow as tf
import json


def is_dark_image(image, threshold=20):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray_image)
    return brightness < threshold


def load_model():
    model_file = os.path.join(settings.MODELS_ROOT, "model.keras")
    model = tf.keras.models.load_model(model_file)
    return model


def load_index():
    with open('class_indices.json', 'r') as f:
        class_indices = json.load(f)
    class_indices = {v: k for k, v in class_indices.items()}
    return class_indices


def detect_product(image):
    image = cv2.resize(image, (settings.IMG_WIDTH, settings.IMG_HEIGHT))
    image = np.expand_dims(image, axis=0)
    image = image / 255.0

    model = load_model()
    pred = model.predict(image)
    class_indices = load_index()

    class_id = np.argmax(pred)
    class_name = class_indices[class_id]
    confidence = float(pred[0][class_id])

    if confidence > 0.7:
        return class_name, confidence
    return None, 0.0
