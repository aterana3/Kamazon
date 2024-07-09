from channels.generic.websocket import AsyncWebsocketConsumer
import json
import os
from PIL import Image as PILImage
from io import BytesIO
import numpy as np
from django.conf import settings
import uuid
from kamazon.ia.detection import is_dark_image, detect_products


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
        await self.save(data)

    async def save(self, data):
        product_id = data.get('id_product')
        image_data = data.get('image')
        roi_coordinates = data.get('roi')
        filename = str(uuid.uuid4())
        type = data.get('type')

        img = PILImage.open(BytesIO(bytes(image_data)))

        width, height = img.size

        # Save image
        images = os.path.join(settings.DATASET_ROOT, f"{type}/images")
        if not os.path.exists(images):
            os.makedirs(images)

        file_img = os.path.join(images, filename + '.jpg')

        img.save(file_img, 'JPEG')

        # Calculate ROI in the required format
        roi_x_center = (roi_coordinates['x'] + roi_coordinates['width'] / 2) / width
        roi_y_center = (roi_coordinates['y'] + roi_coordinates['height'] / 2) / height
        roi_width = abs(roi_coordinates['width'] / width)
        roi_height = abs(roi_coordinates['height'] / height)

        # Save ROI
        labels = os.path.join(settings.DATASET_ROOT, f"{type}/labels")
        if not os.path.exists(labels):
            os.makedirs(labels)

        file_txt = os.path.join(labels, filename + '.txt')

        index_class = self.load_class_index()

        if product_id not in index_class:
            objet_id = len(index_class)
            index_class[product_id] = objet_id
            self.save_class_index(index_class)
        else:
            objet_id = index_class[product_id]

        with open(file_txt, 'w') as f:
            f.write(f'{objet_id} {roi_x_center:.6f} {roi_y_center:.6f} {roi_width:.6f} {roi_height:.6f}')

    def load_class_index(self):
        try:
            with open('class_index.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_class_index(self, class_index):
        try:
            with open('class_index.json', 'w') as f:
                json.dump(class_index, f)
        except Exception as e:
            print(f'Error al guardar el archivo: {e}')


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
                detections = detect_products(image)
                await self.send(text_data=json.dumps(detections))
            except Exception as e:
                print(f'Error al procesar la imagen: {e}')
                await self.send(text_data=json.dumps({'error': 'Error al procesar la imagen.'}))
