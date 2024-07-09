import os.path
import cv2
import numpy as np
from ultralytics import YOLO
from django.conf import settings
import json
from apps.products.models import Product
from asgiref.sync import sync_to_async


def is_dark_image(image, threshold=20):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray_image)
    return brightness < threshold


def load_model():
    models_dir = settings.MODELS_ROOT
    model_path = os.path.join(models_dir, "yolov8m.pt")
    if not os.path.exists(model_path):
        print("Model not found")
        return None
    model = YOLO(model_path)
    return model


def get_product_id(class_index):
    class_index_file = 'class_index.json'
    try:
        with open(class_index_file, 'r') as file:
            data = json.load(file)
            for product_id, index in data.items():
                if index == class_index:
                    return int(product_id)
            return None
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON file: {class_index_file}: {e}")
        return None


def detect_products(image):
    model = load_model()
    if model is None:
        print("Model not found")
        return None

    results = model.predict(image, imgsz=640, conf=0.50)
    detections = {}
    if results:
        for result in results:
            boxes = result.boxes
            if boxes:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cls = int(box.cls[0])
                    product_id = get_product_id(cls)
                    if product_id is not None:
                        if product_id not in detections:
                            detections[product_id] = 0
                        detections[product_id] += 1
    return detections
