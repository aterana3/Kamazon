import os
import xml.etree.ElementTree as ET
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense
from tensorflow.data import AUTOTUNE
from django.conf import settings
import sys

sys.stdout.reconfigure(encoding='utf-8')

def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    label = root.find('object').find('name').text
    bndbox = root.find('object').find('bndbox')
    xmin = int(bndbox.find('xmin').text)
    ymin = int(bndbox.find('ymin').text)
    xmax = int(bndbox.find('xmax').text)
    ymax = int(bndbox.find('ymax').text)
    return label, (xmin, ymin, xmax, ymax)

def process_data(data_dir, img_height, img_width, class_indices):
    images = []
    labels = []
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.jpg'):
                image_path = os.path.join(root, file)
                xml_path = os.path.splitext(image_path)[0] + '.xml'
                if not os.path.exists(xml_path):
                    continue
                label, (xmin, ymin, xmax, ymax) = parse_xml(xml_path)
                image = tf.keras.preprocessing.image.load_img(image_path)
                original_width, original_height = image.size
                image = image.resize((img_width, img_height))
                image = tf.keras.preprocessing.image.img_to_array(image)
                image = preprocess_input(image)

                # Ajustar las coordenadas del bounding box a las dimensiones de la imagen redimensionada
                scale_x = img_width / float(original_width)
                scale_y = img_height / float(original_height)
                xmin = int(xmin * scale_x)
                ymin = int(ymin * scale_y)
                xmax = int(xmax * scale_x)
                ymax = int(ymax * scale_y)

                images.append(image)
                label_array = np.zeros(len(class_indices) + 4)
                label_array[class_indices[label]] = 1
                label_array[len(class_indices):] = [xmin, ymin, xmax, ymax]
                labels.append(label_array)
    return np.array(images), np.array(labels)

def create_dataset(images, labels, batch_size):
    dataset = tf.data.Dataset.from_tensor_slices((images, labels))
    dataset = dataset.shuffle(buffer_size=1024).batch(batch_size).prefetch(buffer_size=AUTOTUNE)
    return dataset

def train_model():
    data_dir = settings.DATASET_ROOT
    batch_size = 32
    img_height = 224
    img_width = 224

    class_labels = set()
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.xml'):
                xml_file = os.path.join(root, file)
                label, _ = parse_xml(xml_file)
                class_labels.add(label)

    class_labels = sorted(list(class_labels))
    num_classes = len(class_labels)
    class_indices = {label: idx for idx, label in enumerate(class_labels)}

    # Procesar los datos
    images, labels = process_data(data_dir, img_height, img_width, class_indices)
    dataset = create_dataset(images, labels, batch_size)

    base_model = MobileNetV2(input_shape=(img_height, img_width, 3), include_top=False, weights='imagenet')
    base_model.trainable = False

    model = Sequential([
        base_model,
        GlobalAveragePooling2D(),
        Dense(128, activation='relu'),
        Dense(num_classes + 4, activation='linear')
    ])

    model.compile(optimizer='adam',
                  loss='mean_squared_error',
                  metrics=['accuracy'])

    model.fit(
        dataset,
        epochs=10,
        steps_per_epoch=len(images) // batch_size
    )

    models_dir = settings.MODELS_ROOT
    model.save(os.path.join(models_dir, 'product_classifier.keras'))
