from flask import Flask, request
from ultralytics import YOLO
from PIL import Image

MODEL_PATH = '/app/src/models/yolov8n_some_trainging.pt'
yolo_model = YOLO(MODEL_PATH)

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def run():
    img = request.args.get('img')
    img = Image.open(img)
    result = yolo_model(img)[0]
    data = [{
            'xyxy': box.xyxy.tolist()[0],
            'lable': result.names[int(box.cls)],
            'conf': float(box.conf),
        } for box in result.boxes]
    return data

@app.route("/test")
def test():
    return 'Server is Live'

if __name__ == "__main__":
    app.run(host='localhost', port=5000)