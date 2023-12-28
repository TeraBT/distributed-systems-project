#!/usr/bin/env python3

import json
import os
import random
import uuid
from datetime import datetime, timedelta

def generate_sensor_data(datapoints: int = 10):
    start_time: datetime = datetime.now()
    start_value: float = 0.5

    progression_value: float = random.choice([-0.05, 0.0, 0.05])
    noise_limits: tuple[float, float] = (-0.02, 0.02)

    return [
        {
            # One datatapoint every 10 minutes
            int((start_time + timedelta(minutes=i * 10)).timestamp()): min(
                1.0, start_value + i * progression_value + random.uniform(*noise_limits)
            )
        }
        for i in range(datapoints)
    ]

def generate_sensor_station():
    return {
        "station_id": str(uuid.uuid4()),
        "measurements": generate_sensor_data(),
    }

def generate_camera(camera_folder_path: str):
    return {
        "camera_id": str(uuid.uuid4()),
        "images_path": camera_folder_path,
    }

def generate_street_section(street_name):
    return {
        "section_id": str(uuid.uuid4()),
        "street_name": street_name,
        "defaultSpeedLimit": random.choice([30, 40, 50,]),
    }

def generate_street(street_name: str, camera_folder_paths):
    return {
        "street_name": street_name,
        "cameras": [
            generate_camera(camera_folder_path) for camera_folder_path in camera_folder_paths
        ],
        "sensor_station": generate_sensor_station(),
        "sections": [
            generate_street_section(street_name)
        ],
        "trafficCapacity": random.choice([5, 10, 15, 20, 25, 30, 35, 40,]),
        "airQualityLimit": random.uniform(0.5, 1.0),
    }

if __name__ == "__main__":
    script_dir: str = os.path.dirname(os.path.abspath(__file__))
    images_folder_name: str = "images"
    images_path: str = os.path.join(script_dir, images_folder_name)
    streets: list[str] = os.listdir(images_path)

    streets: list[str] = [street for street in streets]
    dataset: list[dict] = [generate_street(street, os.listdir(os.path.join(images_path, street))) for street in streets]
    json_data: str = json.dumps(dataset, indent=2)

    with open('data.json', 'w') as json_file:
        json_file.write(json_data)
