from flask import Flask, request
from ultralytics import YOLO
from PIL import Image

WEIGHTSPATH = '/app/data/yolo/model/weights/yolov8n_some_trainging.pt'
model = YOLO(WEIGHTSPATH)

app = Flask(__name__)

@app.route("/detect", methods = ['GET'])
def detect():
    img = request.args.get('img')
    img = Image.open(img)
    result = model(img)[0]
    data = [{
            'xyxy': box.xyxy.tolist()[0],
            'lable': result.names[int(box.cls)],
            'conf': float(box.conf),
        } for box in result.boxes]
    return data

@app.route("/")
def test():
    return 'Server is Live'