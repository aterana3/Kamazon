from channels.generic.websocket import AsyncWebsocketConsumer
import json
import os
from PIL import Image as PILImage
from io import BytesIO
import numpy as np
from django.conf import settings
import uuid
from kamazon.ia.detection import is_dark_image, detect_product

class ProductTrainingConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.room_group_name = None

    async def connect(self):
        self.token = self.scope['url_route']['kwargs']['token']
        self.room_group_name = f'{self.token}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"WebSocket connected to group: {self.room_group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"WebSocket disconnected from group: {self.room_group_name}")

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)

        action = data.get('action')

        if action == 'temp':
            await self.save_temporary(data)
        elif action == 'save':
            await self.save(data)

    async def save_temporary(self, data):
        product_id = data.get('id_product')
        image_data = data.get('image')
        roiCoords = data.get('roi')
        filename = str(uuid.uuid4()) + '.jpg'

        img = PILImage.open(BytesIO(bytes(image_data)))
        img = img.resize((settings.IMG_WIDTH, settings.IMG_HEIGHT))

        # Save image
        temp_dir = os.path.join(settings.TEMP_ROOT, str(product_id))
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        temp_file_path = os.path.join(temp_dir, filename)

        img.save(temp_file_path, 'JPEG')

        json_annotation_file = os.path.join(temp_dir, 'annotations.json')

        await self.send(text_data=json.dumps({'message': f'Temporary image {filename} saved.'}))

    async def save(self, data):
        product_id = data.get('id_product')
        dataset_dir = os.path.join(settings.DATASET_ROOT, str(product_id))
        if not os.path.exists(dataset_dir):
            os.makedirs(dataset_dir)

        temp_dir = os.path.join(settings.TEMP_ROOT, str(product_id))
        temp_files = os.listdir(temp_dir)

        for filename in temp_files:
            temp_file_path = os.path.join(temp_dir, filename)
            with open(temp_file_path, 'rb') as f:
                image_data = f.read()

            file_path = os.path.join(dataset_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(image_data)

            os.remove(temp_file_path)
        await self.send(text_data=json.dumps({'message': 'Images saved successfully.'}))

class ProductDetectorConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = None
        self.room_group_name = None

    async def connect(self):
        self.name = self.scope['url_route']['kwargs']['name']

        self.room_group_name = f'cart_{self.name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        print(f"WebSocket connected to user: {self.name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"WebSocket disconnected from user: {self.name}")

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            try:
                image_bytes = bytes_data
                image = PILImage.open(BytesIO(image_bytes))
                image = np.array(image)
                if is_dark_image(image):
                    await self.send(text_data=json.dumps({'error': 'La imagen es muy oscura.'}))
                    return
                class_name, confidence = detect_product(image)
                if class_name:
                    await self.send(
                        text_data=json.dumps({
                            'class_name': class_name,
                            'confidence': confidence
                        })
                    )
                else:
                    await self.send(text_data=json.dumps({'error': 'Producto no reconocido o confianza baja.'}))
            except Exception as e:
                print(f'Error al procesar la imagen: {e}')
                await self.send(text_data=json.dumps({'error': 'Error al procesar la imagen.'}))