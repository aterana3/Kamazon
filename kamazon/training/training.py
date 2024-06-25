import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os
import numpy as np
from django.conf import settings
import sys

sys.stdout.reconfigure(encoding='utf-8')


batch_size = 32
img_height = 200
img_width = 200


def train_model(product_id):
    product_dir = os.path.join(settings.DATASET_ROOT, str(product_id))

    if not os.path.exists(product_dir):
        raise FileNotFoundError(f"The directory for product ID {product_id} does not exist.")

    datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=0.2
    )

    train_gen = datagen.flow_from_directory(
        settings.DATASET_ROOT,
        target_size=(img_height, img_width),
        batch_size=batch_size,
        class_mode='binary',
        subset='training'
    )

    val_gen = datagen.flow_from_directory(
        settings.DATASET_ROOT,
        target_size=(img_height, img_width),
        batch_size=batch_size,
        class_mode='binary',
        subset='validation'
    )

    print(f"Number of training samples: {train_gen.samples}")
    print(f"Number of validation samples: {val_gen.samples}")

    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(img_height, img_width, 3)),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    model.fit(
        train_gen,
        epochs=10,
        validation_data=val_gen
    )

    model_path = os.path.join(settings.MODELS_ROOT, f'model_{product_id}.h5')
    model.save(model_path)
    print(f"Model saved to {model_path}")



def load_model(product_id):
    model_path = os.path.join(settings.MODELS_ROOT, f'model_{product_id}.h5')
    if not os.path.exists(model_path):
        raise Exception(f"El modelo {model_path} no existe.")

    model = tf.keras.models.load_model(model_path)
    return model

def predict(model, img_path):
    img = tf.keras.preprocessing.image.load_img(img_path, target_size=(img_height, img_width))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0

    predictions = model.predict(img_array)
    return predictions
