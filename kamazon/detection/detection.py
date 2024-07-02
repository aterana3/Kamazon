import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from apps.products.models import Product


# Cargar el modelo entrenado
def load_model():
    model_path = 'models/product_classifier.keras'
    return tf.keras.models.load_model(model_path)

def load_class_labels():
    products = Product.objects.all()
    return [product.name for product in products]


def load_and_preprocess_image(imagen_bytes, img_height, img_width):
    image = tf.image.decode_image(imagen_bytes, channels=3)
    image = tf.image.resize(image, [img_height, img_width])
    image = img_to_array(image)
    image = preprocess_input(image)
    return image

def detect_objects(imagen_bytes, model, class_labels, img_height=224, img_width=224):
    image = load_and_preprocess_image(imagen_bytes, img_height, img_width)
    image_batch = np.expand_dims(image, axis=0)

    predictions = model.predict(image_batch)

    pred_class = np.argmax(predictions[0])
    pred_label = class_labels[pred_class]

    xmin, ymin, xmax, ymax = predictions[0][len(class_labels):]

    return pred_label, (xmin, ymin, xmax, ymax)