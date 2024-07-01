import json
import os
from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer
import xml.etree.ElementTree as ET
from PIL import Image


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
        filename = data.get('filename')
        image_data = data.get('image')
        product_id = data.get('id_product')
        class_label = data.get('name_product')

        # Save image
        temp_dir = os.path.join(settings.TEMP_ROOT, str(product_id))
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        temp_file_path = os.path.join(temp_dir, filename)
        with open(temp_file_path, 'wb') as f:
            f.write(bytes(image_data))

        roi = data.get('roi')
        self.generate_xml(product_id, filename, roi)
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

    def generate_xml(self, product_id, filename, roi):
        image_path = os.path.join(settings.TEMP_ROOT, str(product_id), filename)
        image = Image.open(image_path)
        image_width, image_height = image.size

        root = ET.Element("annotation")

        filename_elem = ET.SubElement(root, "filename")
        filename_elem.text = filename

        size_elem = ET.SubElement(root, "size")
        ET.SubElement(size_elem, "width").text = str(image_width)
        ET.SubElement(size_elem, "height").text = str(image_height)

        roi_elem = ET.SubElement(root, "object")
        ET.SubElement(roi_elem, "name").text = str(product_id)
        ET.SubElement(roi_elem, "pose").text = "Unspecified"
        ET.SubElement(roi_elem, "truncated").text = "0"
        ET.SubElement(roi_elem, "difficult").text = "0"

        bndbox_elem = ET.SubElement(roi_elem, "bndbox")
        ET.SubElement(bndbox_elem, "xmin").text = str(roi['x'])
        ET.SubElement(bndbox_elem, "ymin").text = str(roi['y'])
        ET.SubElement(bndbox_elem, "xmax").text = str(roi['x'] + roi['width'])
        ET.SubElement(bndbox_elem, "ymax").text = str(roi['y'] + roi['height'])

        xml_string = ET.tostring(root).decode('utf-8')
        xml_filename = os.path.splitext(filename)[0] + '.xml'
        xml_file_path = os.path.join(settings.TEMP_ROOT, str(product_id), xml_filename)

        with open(xml_file_path, 'w') as f:
            f.write(xml_string)

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
                pass
            except Exception as e:
                print(f'Error al procesar la imagen: {e}')
