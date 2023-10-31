from flask import Flask, request
import cv2
import os

# camera constants for distance calc
CAM_FOCAL_LENGTH = 2000 #in pixels (roughly)
STEREO_BASELINE = 0.1 #in meteres

# import the calibration data
CALIBRATION_VALUES_PATH = "stereo_rectify_maps.xml"

cv_file = cv2.FileStorage("/app/src/stereo_rectify_maps.xml", cv2.FILE_STORAGE_READ)
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

    img_path_pairs = json_data.get('img_pairs', [])

    if img_path_pairs == []:
        return "No image pairs provided", 400

    for img_pair in img_path_pairs:
        if not (os.path.isfile(img_pair[0]) and os.path.isfile(img_pair[1])):
            return f"Image Pair {img_pair} does not exist", 400
        
    for image_pair_path in img_path_pairs:
        old_imgL = cv2.imread(image_pair_path[0])
        old_imgR = cv2.imread(image_pair_path[1])

        imgL = cv2.remap(old_imgL, CAL_MAPS[0][0], CAL_MAPS[0][1], cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
        imgR = cv2.remap(old_imgR, CAL_MAPS[1][0], CAL_MAPS[1][1], cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
        
        # rewrite the images with the undistorted versions
        cv2.imwrite(image_pair_path[0], imgL)
        cv2.imwrite(image_pair_path[1], imgR)
            
    return "Images Undistorted", 200


@app.route("/test")
def test():
    return 'Server is Live'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
