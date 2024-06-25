import json
import os
import uuid
from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer

class ProductConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.token = self.scope['url_route']['kwargs']['token']
        self.room_group_name = f'product_{self.token}'

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
            await self.save_temporary_image(data)
        elif action == 'save':
            await self.save_images(data)

    async def save_temporary_image(self, data):
        filename = data.get('filename')
        image_data = data.get('image')
        product_id = data.get('id_product')

        temp_dir = os.path.join(settings.TEMP_ROOT, str(product_id))
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        temp_file_path = os.path.join(temp_dir, filename)

        with open(temp_file_path, 'wb') as f:
            f.write(bytes(image_data))

        await self.send(text_data=json.dumps({'message': f'Temporary image {filename} saved.'}))

    async def save_images(self, data):
        product_id = data.get('id_product')
        dataset_dir = f'{settings.DATASET_ROOT}/{product_id}'
        if not os.path.exists(dataset_dir):
            os.makedirs(dataset_dir)

        temp_dir = os.path.join(settings.TEMP_ROOT, str(product_id))

        temp_files = os.listdir(temp_dir)

        for filename in temp_files:
            temp_file_path = os.path.join(temp_dir, filename)
            with open(temp_file_path, 'rb') as f:
                image_data = f.read()

            file_name = f"{uuid.uuid4()}.jpg"
            file_path = os.path.join(dataset_dir, file_name)
            with open(file_path, 'wb') as f:
                f.write(image_data)

            os.remove(temp_dir)
        await self.send(text_data=json.dumps({'message': 'Images saved successfully.'}))