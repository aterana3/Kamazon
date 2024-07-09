import sys
import json
from apps.products.models import Product
import os
from django.conf import settings
import yaml
import subprocess

# IMPORTANT
sys.stdout.reconfigure(encoding='utf-8')

def get_number_of_classes():
    class_index_file = 'class_index.json'
    try:
        with open(class_index_file, 'r') as file:
            class_index = json.load(file)
            return len(class_index)
    except FileNotFoundError:
        return 0
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON file: {class_index_file}: {e}")
        return 0

def get_name_of_products():
    names = []
    class_index_file = 'class_index.json'
    try:
        with open(class_index_file, 'r') as file:
            class_index = json.load(file)
            for key in class_index:
                try:
                    product = Product.objects.get(pk=key)
                    names.append(product.name)
                except Product.DoesNotExist as e:
                    print(f"Product with ID {key} does not exist: {e}")
            return names
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON file: {class_index_file}: {e}")
        return []

def create_yaml_file():
    config_file = 'dataset.yaml'
    num_class = get_number_of_classes()
    names = get_name_of_products()
    if not names:
        print('No product names found. Please run the class_index.py script first.')
        return
    if num_class > 0:
        train_path = os.path.join(settings.DATASET_ROOT, 'train')
        val_path = os.path.join(settings.DATASET_ROOT, 'val')
        data = {
            'train': train_path,
            'val': val_path,
            'nc': num_class,
            'names': names
        }

        yaml_str = yaml.dump(data, default_flow_style=None, sort_keys=False)

        yaml_lines = yaml_str.split('\n')
        for i, line in enumerate(yaml_lines):
            if line.startswith('names:'):
                quoted_names = [f'"{name}"' for name in names]
                yaml_lines[i] = f'names: [{", ".join(quoted_names)}]'
                break

        modified_yaml_str = '\n'.join(yaml_lines)

        with open(config_file, 'w') as file:
            file.write(modified_yaml_str)
    else:
        print('No class index file found. Please run the class_index.py script first.')


def create_model():
    command = [
        "yolo ",
        "task=segment ",
        "mode=train ",
        "epochs=4 ",
        "data=dataset.yaml ",
        "model=yolov8n.pt ",
        "imgsz=640 ",
        "batch=4"
    ]
    subprocess.run(command)