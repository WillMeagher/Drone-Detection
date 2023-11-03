from flask import Flask, request, jsonify
from easy_clip import Clip
from PIL import Image
import os
import sys

app = Flask(__name__)

MODEL_PATH = "/app/clip-data/CLIP/ViT-B-32.pt"
clip_model = Clip(MODEL_PATH)

TYPE_CLASSES = [
    "a quadcopter", 
    "a fixed wing drone", 
    "a hexacopter",
    "a octocopter",
    "a drone with more than four propellers",
]

def get_cropped(img, box):
    startPoint = int(box['xyxy'][0]), int(box['xyxy'][1])
    endPoint = int(box['xyxy'][2]), int(box['xyxy'][3])

    return img.crop((startPoint[0], startPoint[1], endPoint[0], endPoint[1]))


@app.route("/", methods = ['GET'])
def run():
    all_imgs = []

    # get json data
    json_data = request.get_json()

    img_paths = json_data.get('imgs', [])
    images_boxes = json_data.get('boxes', [])

    if img_paths == []:
        return "No images provided", 400

    for img in img_paths:
        if os.path.isfile(img):
            all_imgs.append(Image.open(img))
        else:
            return f"Image {img} does not exist", 400

    if images_boxes != [] and len(images_boxes) != len(img_paths):
        return "Number of images and boxes does not match", 400

    if images_boxes == []:
        images_boxes = [None] * len(img_paths)

    type_values, type_indices = [], []

    for i, image_boxes in enumerate(images_boxes):
        type_values.append([])
        type_indices.append([])

        if image_boxes == None:
            img = all_imgs[i]

            type_v, type_i = clip_model.run(img, TYPE_CLASSES)

            type_values[i].append(type_v)
            type_indices[i].append(type_i)
        else:
            for box in image_boxes:
                cropped_img = get_cropped(all_imgs[i], box)

                type_v, type_i = clip_model.run(cropped_img, TYPE_CLASSES)

                type_values[i].append(type_v)
                type_indices[i].append(type_i)

    data = []
    for i in range(len(type_values)):
        data.append([])
        
        for j in range(len(type_values[i])):
            data[i].append({
                "type": {
                    "conf": type_values[i][j][0].item(),
                    "label": TYPE_CLASSES[type_indices[i][j][0]]
                }
            })

    return data

@app.route("/test")
def test():
    return 'Server is Live'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)