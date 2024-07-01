import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
import xml.etree.ElementTree as ET
from django.conf import settings


class TrainingModel:

    def __init__(self):
        self.DATASET_ROOT = settings.DATASET_ROOT
        self.MODELS_ROOT = settings.MODELS_ROOT
        self.IMG_HEIGHT = 224
        self.IMG_WIDTH = 224
        self.num_classes = self.count_classes()

    def count_classes(self):
        class_dirs = next(os.walk(self.DATASET_ROOT))[1]
        return len(class_dirs)

    def parse_xml(self, xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()

        filename = root.find('filename').text
        size_elem = root.find('size')
        width = int(size_elem.find('width').text)
        height = int(size_elem.find('height').text)

        objects = []
        for obj in root.findall('object'):
            bbox = obj.find('bndbox')
            xmin = int(bbox.find('xmin').text)
            ymin = int(bbox.find('ymin').text)
            xmax = int(bbox.find('xmax').text)
            ymax = int(bbox.find('ymax').text)
            class_name = obj.find('name').text
            objects.append({
                'class_name': class_name,
                'bbox': [xmin, ymin, xmax, ymax]
            })

        return filename, width, height, objects

    def load_image(self, image_path):
        img = tf.io.read_file(image_path)
        img = tf.image.decode_jpeg(img, channels=3)
        img = tf.image.resize(img, [self.IMG_HEIGHT, self.IMG_WIDTH])
        img = img / 255.0
        return img

    def create_dataset(self):
        images = []
        annotations = []

        for product_dir in os.listdir(self.DATASET_ROOT):
            if os.path.isdir(os.path.join(self.DATASET_ROOT, product_dir)):
                for filename in os.listdir(os.path.join(self.DATASET_ROOT, product_dir)):
                    if filename.endswith('.xml'):
                        xml_path = os.path.join(self.DATASET_ROOT, product_dir, filename)
                        image_path = os.path.join(self.DATASET_ROOT, product_dir,
                                                  os.path.splitext(filename)[0] + '.jpg')

                        filename, width, height, objects = self.parse_xml(xml_path)
                        images.append(image_path)
                        annotations.append({
                            'filename': filename,
                            'width': width,
                            'height': height,
                            'objects': objects
                        })

        image_dataset = tf.data.Dataset.from_tensor_slices(images)
        annotation_dataset = tf.data.Dataset.from_tensor_slices(annotations)

        dataset = tf.data.Dataset.zip((image_dataset, annotation_dataset))
        dataset = dataset.map(lambda image, annotation: (self.load_image(image), annotation))
        return dataset

    def build_train_model(self):
        dataset = self.create_dataset()

        model = Sequential([
            Conv2D(32, (3, 3), activation='relu', input_shape=(self.IMG_HEIGHT, self.IMG_WIDTH, 3)),
            MaxPooling2D((2, 2)),
            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            Flatten(),
            Dense(64, activation='relu'),
            Dense(self.num_classes, activation='softmax')
        ])

        model.compile(optimizer='adam',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        model.fit(dataset, epochs=10)

        model_name = 'products.h5'
        model_path = os.path.join(self.MODELS_ROOT, model_name)
        model.save(model_path)
        print(f'Modelo guardado en: {model_path}')
