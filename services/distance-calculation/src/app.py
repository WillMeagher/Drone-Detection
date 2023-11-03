from flask import Flask, request

# camera constants for distance calc
CAM_FOCAL_LENGTH = 2000 #in pixels (roughly)
STEREO_BASELINE = 0.1 #in meteres

DIMENSION_TOLERANCE_PERCENT = 1
HEIGHT_TOLERANCE_PERCENT = 1
WIDTH_TOLERANCE_PERCENT = 1

app = Flask(__name__)

# need to add checks and logic for if one camera detects a drone and the other doesn't
# also need check to match up boxes if they are not in the same order
def calculate_distance(boxes_L, boxes_R):    
    distances = [None] * len(boxes_L)
    for i in range(len(boxes_L)):
        for j in range(len(boxes_R)):
            width_L, height_L = boxes_L[i]['xyxy'][2] - boxes_L[i]['xyxy'][0], boxes_L[i]['xyxy'][3] - boxes_L[i]['xyxy'][1]
            width_R, height_R = boxes_R[j]['xyxy'][2] - boxes_R[j]['xyxy'][0], boxes_R[j]['xyxy'][3] - boxes_R[j]['xyxy'][1]
            
            if abs(width_L - width_R) > width_L * DIMENSION_TOLERANCE_PERCENT:
                # widths don't match
                continue

            if abs(height_L - height_R) > height_L * DIMENSION_TOLERANCE_PERCENT:
                # heiths don't match
                continue

            center_L_x, center_R_x = (boxes_L[i]['xyxy'][0] + boxes_L[i]['xyxy'][2]) / 2, (boxes_R[j]['xyxy'][0] + boxes_R[j]['xyxy'][2]) / 2

            if abs(center_L_x - center_R_x) > width_L * WIDTH_TOLERANCE_PERCENT:
                # width location don't match
                continue

            center_L_y, center_R_y = (boxes_L[i]['xyxy'][1] + boxes_L[i]['xyxy'][3]) / 2, (boxes_R[j]['xyxy'][1] + boxes_R[j]['xyxy'][3]) / 2

            if abs(center_L_y - center_R_y) > height_L * HEIGHT_TOLERANCE_PERCENT:
                # height location don't match
                continue

            distance = STEREO_BASELINE * CAM_FOCAL_LENGTH / abs(center_L_x - center_R_x + 0.0000001)

            distances[i] = distance
    return distances


@app.route("/", methods=['GET'])
def run():
    # get json data
    json_data = request.get_json()

    boxes = json_data.get('boxes', [])

    if boxes == []:
        return "No box pairs provided", 400

    if len(boxes) % 2 != 0:
        return "Uneven number of boxes provided", 400
        
    data = []
    for i in range(0, len(boxes), 2):
        distances = calculate_distance(boxes[i], boxes[i + 1])
        data.append(distances)
            
    return data


@app.route("/test")
def test():
    return 'Server is Live'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
