from ultralytics import YOLO
import math
import cv2


# Load model
def load_model():
    model = YOLO("models/yolov8l.pt")
    return model


# Detect objects
# Detect objects
def detect_objects(image):
    ObjectModel = load_model()

    clsObject = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
                 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
                 'elephant',
                 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis',
                 'snowboard',
                 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
                 'bottle',
                 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
                 'broccoli', 'carrot',
                 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet',
                 'tv', 'laptop',
                 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator',
                 'book', 'clock', 'vase',
                 'scissors', 'teddy bear', 'hair drier', 'toothbrush']
    results = prediction_model(image, ObjectModel, clsObject)
    return results


def prediction_model(image, model, clase):
    img_height = 224
    img_width = 224
    img = cv2.resize(image, (img_width, img_height))

    results = model(img, stream=True, verbose=False)
    predict = []
    for res in results:
        boxes = res.boxes
        for box in boxes:
            # Bounding box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # Error < 0
            if x1 < 0:
                x1 = 0
            if y1 < 0:
                y1 = 0
            if x2 < 0:
                x2 = 0
            if y2 < 0:
                y2 = 0

            cls = int(box.cls[0])

            conf = math.ceil(box.conf[0])

            predict.append({
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2,
                'cls': clase[cls],
                'conf': conf
            })
        return predict
