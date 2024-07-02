import tensorflow as tf
from apps.products.models import Product
import numpy as np
import cv2
from PIL import Image as PILImage
from io import BytesIO
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

img_height = 224
img_width = 224

# Cargar el modelo entrenado
def load_model():
    model_path = 'product_classifier.keras'
    return tf.keras.models.load_model(model_path)


def load_class_labels():
    products = Product.objects.all()
    return [product.id for product in products]

def is_image_dark(image, threshold=20):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray_image)
    return brightness < threshold

def predict_product(image_bytes):
    print("Starting predict_product function")
    model = load_model()
    print("Model loaded successfully")

    try:
        # Abrir la imagen desde bytes con PIL
        image = PILImage.open(BytesIO(image_bytes))
        print("Image opened successfully")

        # Redimensionar la imagen al tamaño esperado por el modelo y aplicar preprocesamiento
        image = image.resize((img_height, img_width))
        print("Image resized successfully")
        image_np = np.array(image)
        print(f"Image converted to numpy array: shape {image_np.shape}")
        image_resized = preprocess_input(image_np)
        print(f"Image preprocessed: shape {image_resized.shape}")

        # Expandir dimensiones si es necesario (para modelos que esperan un lote de imágenes)
        image_resized = np.expand_dims(image_resized, axis=0)
        print(f"Expanded image shape: {image_resized.shape}")

        # Realizar la predicción
        predictions = model.predict(image_resized)
        print(f"Predictions: {predictions}")

        # Obtener la clase predicha
        predicted_class = np.argmax(predictions, axis=1)[0]
        print(f"Predicted class: {predicted_class}")

        return predicted_class

    except Exception as e:
        print(f'Error al predecir el producto: {e}')
        return None