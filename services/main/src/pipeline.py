import requests
import os
import json
import cv2
import numpy as np
import uuid
import matplotlib.pyplot as plt

from dotenv import load_dotenv
load_dotenv()

UPLOAD_FOLDER = "/app/data/uploaded/"
ANNOTATED_FOLDER = "/app/data/annotated/"

YOLO_ENDPOINT = "http://yolo-localization:5000"
CLIP_ENDPOINT = "http://clip-classifier:5000"


def run_yolo(imgs):
    data = {
        'imgs': imgs
    }

    # call yolo-localization service to get bounding boxes
    yolo_results = requests.get(YOLO_ENDPOINT, json=data)
    boxes = json.loads(yolo_results.content)

    return boxes


def run_clip(imgs, images_boxes):
    data = {
        'imgs': imgs,
        'boxes': images_boxes
    }

    # call clip-classifier service to get classifications
    clip_results = requests.get(CLIP_ENDPOINT, json=data)
    types = json.loads(clip_results.content)

    return types


def get_results(img, boxes, results):
    cmap = plt.get_cmap('viridis')
    font = cv2.FONT_HERSHEY_SIMPLEX

    for i, box in enumerate(boxes):
        startPoint = int(box['xyxy'][0]), int(box['xyxy'][1])
        endPoint = int(box['xyxy'][2]), int(box['xyxy'][3])

        type_conf = results[i]['type']['label']
        weight_conf = results[i]['weight']['label']

        color = cmap(box['conf'])
        color = color[2] * 255, color[1] * 255, color[0] * 255
        cv2.rectangle(img, startPoint, endPoint, color=color, thickness = 2)
        cv2.rectangle(img, startPoint, (startPoint[0] + 200, startPoint[1] - 25), color=color, thickness = -1)
        text = f'Drone - {box["conf"]:.2f}%'
        cv2.putText(img, text, (startPoint[0] + 2, startPoint[1] - 2), font, 0.75, color=(255, 255, 255), bottomLeftOrigin=False, thickness = 2)
        cv2.putText(img, f'Type - {type_conf}', (startPoint[0] + 2, startPoint[1] + 20), font, 0.75, color=(255, 255, 255), bottomLeftOrigin=False, thickness = 2)
        cv2.putText(img, f'Weight - {weight_conf}', (startPoint[0] + 2, startPoint[1] + 40), font, 0.75, color=(255, 255, 255), bottomLeftOrigin=False, thickness = 2)

    return img


def pipeline(imgs):
    file_names = []

    # save uploaded files
    for img in imgs:
        unique_filename = str(uuid.uuid4()) + '.jpg'
        unique_file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        cv2.imwrite(unique_file_path, img)
        file_names.append(unique_file_path)

    # run yolo-localization and clip-classifier
    boxes = run_yolo(file_names)
    types = run_clip(file_names, boxes)

    # annotate images
    results = []
    for i in range(len(file_names)):
        img = cv2.imread(file_names[i])
        result_img = get_results(img, boxes[i], types[i])
        results.append(result_img)
    
    # remove uploaded files
    for file_name in file_names:
        os.remove(file_name)

    return results