import os.path

import cv2
import numpy as np
from ultralytics import YOLO


def is_dark_image(image, threshold=20):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray_image)
    return brightness < threshold


def load_model():
    model_file = "yolov8n.pt"
    if not os.path.exists(model_file):
        return None
    model = YOLO(model_file)
    return model

def detect_products(image):
    model = load_model()
    if model is None:
        print("Model not found")
        return None
    results = model.predict(image, imgsz=640, conf=0.98)
    annotations = results[0].plot()
    return annotations