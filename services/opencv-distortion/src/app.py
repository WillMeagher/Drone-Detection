from flask import Flask, request
import cv2
import os
import uuid

# camera constants for distance calc
CAM_FOCAL_LENGTH = 2000 #in pixels (roughly)
STEREO_BASELINE = 0.1 #in meteres

# import the calibration data
CALIBRATION_VALUES_PATH = "/app/src/stereo_rectify_maps.xml"

cv_file = cv2.FileStorage(CALIBRATION_VALUES_PATH, cv2.FILE_STORAGE_READ)
LEFT_MAP_X = cv_file.getNode("Left_Stereo_Map_x").mat()
LEFT_MAP_Y = cv_file.getNode("Left_Stereo_Map_y").mat()
RIGHT_MAP_X = cv_file.getNode("Right_Stereo_Map_x").mat()
RIGHT_MAP_Y = cv_file.getNode("Right_Stereo_Map_y").mat()
cv_file.release()

CAL_MAPS = [[LEFT_MAP_X, LEFT_MAP_Y], [RIGHT_MAP_X, RIGHT_MAP_Y]]

app = Flask(__name__)


@app.route("/", methods=['GET'])
def run():
    # get json data
    json_data = request.get_json()

    img_paths = json_data.get('imgs', [])
    in_place = json_data.get('in_place', False)

    if img_paths == []:
        return "No images provided", 400

    if len(img_paths) % 2 != 0:
        return "Uneven number of images provided", 400

    data = []

    for i in range(0, len(img_paths), 2):
        if not (os.path.isfile(img_paths[i]) and os.path.isfile(img_paths[i + 1])):
            return f"Image {i} or {i + 1} does not exist", 400
        old_imgL = cv2.imread(img_paths[i])
        old_imgR = cv2.imread(img_paths[i + 1])

        imgL = cv2.remap(old_imgL, CAL_MAPS[0][0], CAL_MAPS[0][1], cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
        imgR = cv2.remap(old_imgR, CAL_MAPS[1][0], CAL_MAPS[1][1], cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
        
        if in_place:
            output_path_0 = img_paths[i]
            output_path_1 = img_paths[i + 1]
        else:
            folder = os.path.dirname(img_paths[i])
            output_path_0 = os.path.join(folder, str(uuid.uuid4()) + '.jpg')
            output_path_1 = os.path.join(folder, str(uuid.uuid4()) + '.jpg')

        # rewrite the images with the undistorted versions
        cv2.imwrite(output_path_0, imgL)
        cv2.imwrite(output_path_1, imgR)

        data.extend([output_path_0, output_path_1])
            
    return data


@app.route("/test")
def test():
    return 'Server is Live'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
