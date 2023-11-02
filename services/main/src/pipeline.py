import requests
import os
import json
import cv2
import numpy as np
import uuid
import matplotlib.pyplot as plt
import math

from dotenv import load_dotenv
load_dotenv()

UPLOAD_FOLDER = "/app/data/uploaded/"
ANNOTATED_FOLDER = "/app/data/annotated/"

YOLO_ENDPOINT = "http://yolo-localization:5000"
CLIP_ENDPOINT = "http://clip-classifier:5000"
DISTORTION_ENDPOINT = "http://opencv-distortion:5000"
DISTANCE_ENDPOINT = "http://distance-calculation:5000"

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


def run_distortion(imgs, in_place=True):
    data = {
        'imgs': imgs,
        'in_place': in_place
    }

    distortion_results = requests.get(DISTORTION_ENDPOINT, json=data)
    resut_paths = json.loads(distortion_results.content)

    return resut_paths


def run_distance(boxes):
    data = {
        'boxes': boxes
    }

    distance_results = requests.get(DISTANCE_ENDPOINT, json=data)
    distances = json.loads(distance_results.content)

    return distances

def get_size(width, distance):
    CAM_WIDTH = 1280 #horizontal resolution in pixels
    CAM_HFOV = 55 #horizontal FOV in degrees
    prop = width / 1280
    total_width = distance * math.tan(CAM_HFOV * math.pi / 180) * 2
    return total_width * prop

def get_results(img, boxes, results, distances=None):
    cmap = plt.get_cmap('viridis')
    font = cv2.FONT_HERSHEY_SIMPLEX

    for i, box in enumerate(boxes):
        startPoint = int(box['xyxy'][0]), int(box['xyxy'][1])
        endPoint = int(box['xyxy'][2]), int(box['xyxy'][3])

        drone_type = results[i]['type']['label']
        # drone_weight = results[i]['weight']['label']

        color = cmap(box['conf'])
        color = color[2] * 255, color[1] * 255, color[0] * 255
        # bounding box
        cv2.rectangle(img, startPoint, endPoint, color=color, thickness = 2)
        # drone text background
        cv2.rectangle(img, startPoint, (startPoint[0] + 200, startPoint[1] - 25), color=color, thickness = -1)
        # extra labels background
        cv2.rectangle(img, (startPoint[0], endPoint[1]), (startPoint[0] + 400, startPoint[1] - 60), color=color, thickness = -1)
        
        text = f'Drone - {box["conf"]:.2f}%'
        cv2.putText(img, text, (startPoint[0] + 2, startPoint[1] - 2), font, 0.75, color=(255, 255, 255), bottomLeftOrigin=False, thickness = 2)
        cv2.putText(img, f'Type - {drone_type}', (startPoint[0] + 2, endPoint[1] + 20), font, 0.75, color=(255, 255, 255), bottomLeftOrigin=False, thickness = 2)
        # cv2.putText(img, f'Weight - {drone_weight}', (startPoint[0] + 2, startPoint[1] + 40), font, 0.75, color=(255, 255, 255), bottomLeftOrigin=False, thickness = 2)
        if distances is not None:
            width = int(box['xyxy'][3]) - int(box['xyxy'][1])
            size = get_size(width, distances[i])
            cv2.putText(img, f'Distance - {distances[i]:.2f}m', (startPoint[0] + 2, endPoint[1] + 60), font, 0.75, color=(255, 255, 255), bottomLeftOrigin=False, thickness = 2)
            cv2.putText(img, f'Size - {size:.2f}m', (startPoint[0] + 2, endPoint[1] + 80), font, 0.75, color=(255, 255, 255), bottomLeftOrigin=False, thickness = 2)

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
    # types = run_clip(file_names, boxes)
    types = [0] * len(boxes)

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


def pipeline_stereo(imgs):
    file_names = []

    # save uploaded files
    for img in imgs:
        unique_filename = str(uuid.uuid4()) + '.jpg'
        unique_file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        cv2.imwrite(unique_file_path, img)
        file_names.append(unique_file_path)

    run_distortion(file_names, in_place=True)

    all_boxes = run_yolo(file_names)
    distances = run_distance(all_boxes)

    # the array of boxes and distances is the same shape
    # if the value of a distance is None, remove the box

    left_boxes = all_boxes[::2]
    left_files = file_names[::2]

    left_valid_boxes = []
    valid_distances = []
    for i in range(len(left_boxes)):
        left_valid_boxes.append([])
        valid_distances.append([])
        for j in range(len(left_boxes[i])):
            if distances[i][j] is not None:
                left_valid_boxes[i].append(left_boxes[i][j])
                valid_distances[i].append(distances[i][j])
    

    types = run_clip(left_files, left_valid_boxes)

    results = []
    for i in range(len(left_files)):
        img = cv2.imread(left_files[i])
        result_img = get_results(img, left_valid_boxes[i], types[i], valid_distances[i])
        results.append(result_img)

    # remove uploaded files
    for file_name in file_names:
        os.remove(file_name)

    return results