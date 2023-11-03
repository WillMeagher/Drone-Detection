from flask import Flask, request
from ultralytics import YOLO
from PIL import Image
import os

MODEL_PATH = '/app/src/models/yolov8s_20_epochs.pt'
yolo_model = YOLO(MODEL_PATH)

app = Flask(__name__)


@app.route("/", methods = ['GET'])
def run():
    all_imgs = []

    # get json data
    json_data = request.get_json()
    img_paths = json_data.get('imgs', [])
    
    if img_paths == []:
        return "No images provided", 400

    for img in img_paths:
        if os.path.isfile(img):
            all_imgs.append(Image.open(img))
        else:
            return f"Image {img} does not exist", 400

    data = []
    for img in all_imgs:
        result = yolo_model(img)[0]
        this_data = [{
                'xyxy': box.xyxy.tolist()[0],
                'label': result.names[int(box.cls)],
                'conf': float(box.conf),
            } for box in result.boxes]

        data.append(this_data)
    
    return data


@app.route("/test")
def test():
    return 'Server is Live'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)