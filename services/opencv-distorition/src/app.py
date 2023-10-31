from flask import Flask, request
import cv2
import requests
import json
import os
import uuid
import math

YOLO_ENDPOINT = "http://yolo-localization:5000"
CLIP_ENDPOINT = "http://clip-classifier:5000"
UPLOAD_FOLDER = "/app/data/uploaded/"

# camera constants for distance calc
CAM_FOCAL_LENGTH = 2000 #in pixels (roughly)
STEREO_BASELINE = 0.1 #in meteres

# import the calibration data
CALIBRATION_VALUES_PATH = "stereo_rectify_maps.xml"

cv_file = cv2.FileStorage("/app/src/stereo_rectify_maps.xml", cv2.FILE_STORAGE_READ)
Left_Map_x = cv_file.getNode("Left_Stereo_Map_x").mat()
Left_Map_y = cv_file.getNode("Left_Stereo_Map_y").mat()
Right_Map_x = cv_file.getNode("Right_Stereo_Map_x").mat()
Right_Map_y = cv_file.getNode("Right_Stereo_Map_y").mat()
cv_file.release()
CAL_MAPS = [[Left_Map_x, Left_Map_y], [Right_Map_x, Right_Map_y]]

def run_yolo(imgs):
    data = {
        'imgs': imgs
    }

    # call yolo-localization service to get bounding boxes
    yolo_results = requests.get(YOLO_ENDPOINT, json=data)
    boxes = json.loads(yolo_results.content)

    return boxes

def calculate_distance(unique_file_paths):
    boxes = run_yolo(unique_file_paths)
    
    distances = []
    for i in range(0, len(boxes[0])):
        centerL = (boxes[0][i]['xyxy'][0] + boxes[0][i]['xyxy'][2]) / 2
        centerR = (boxes[1][i]['xyxy'][0] + boxes[1][i]['xyxy'][2]) / 2
        print(centerL, centerR)
        distance = STEREO_BASELINE * CAM_FOCAL_LENGTH / abs(centerL - centerR)
        distances.append(distance)
    return distances


app = Flask(__name__)

@app.route("/", methods=['GET'])
def run():
    all_img_pairs = []

    # get json data
    json_data = request.get_json()

    img_path_pairs = json_data.get('img_pairs', [])

    if img_path_pairs == []:
        return "No image pairs provided", 400

    for img_pair in img_path_pairs:
        if os.path.isfile(img_pair[0]) and os.path.isfile(img_pair[1]):
            imgs = [cv2.imread(path) for path in img_pair]
            all_img_pairs.append(imgs)
        else:
            return f"Image Pair {img_pair} does not exist", 400
        
    data = []
    for img_pair in all_img_pairs:
        imgL = cv2.remap(img_pair[0], CAL_MAPS[0][0], CAL_MAPS[0][1], cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
        imgR = cv2.remap(img_pair[1], CAL_MAPS[1][0], CAL_MAPS[1][1], cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
        
        unique_filenames = [str(uuid.uuid4()) + '.png', str(uuid.uuid4()) + '.png']
        unique_file_paths = [os.path.join(UPLOAD_FOLDER, fname) for fname in unique_filenames]
        cv2.imwrite(unique_file_paths[0], imgL)
        cv2.imwrite(unique_file_paths[1], imgR)
        
        distances = calculate_distance(unique_file_paths)
        data.append(distances)
        
        for file_path in unique_file_paths:
            os.remove(file_path)
            
    return data


@app.route("/test")
def test():
    return 'Server is Live'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
