import sys
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from django.conf import settings
import json
import os

# IMPORTANT
sys.stdout.reconfigure(encoding='utf-8')


def train_model():
    print("Training model...")
    dataset = settings.DATASET_ROOT
    datagen = ImageDataGenerator(rescale=1. / 255, validation_split=0.2)

    train_generator = datagen.flow_from_directory(
        dataset,
        target_size=(settings.IMG_WIDTH, settings.IMG_HEIGHT),
        batch_size=32,
        class_mode='categorical',
        subset='training'
    )

    validation_generator = datagen.flow_from_directory(
        dataset,
        target_size=(settings.IMG_WIDTH, settings.IMG_HEIGHT),
        batch_size=32,
        class_mode='categorical',
        subset='validation'
    )

    model = tf.keras.models.Sequential([
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(settings.IMG_WIDTH, settings.IMG_HEIGHT, 3)),
        tf.keras.layers.MaxPooling2D(2, 2),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D(2, 2),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(len(train_generator.class_indices), activation='softmax')
    ])

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    model.fit(train_generator, validation_data=validation_generator, epochs=10)

    model_dir = settings.MODELS_ROOT

    model.save(os.path.join(model_dir, 'model.keras'))

    with open('class_indices.json', 'w') as f:
        json.dump(train_generator.class_indices, f)
    print("Model saved.")
