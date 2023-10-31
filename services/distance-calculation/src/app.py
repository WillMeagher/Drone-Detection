from flask import Flask, request

UPLOAD_FOLDER = "/app/data/uploaded/"

# camera constants for distance calc
CAM_FOCAL_LENGTH = 2000 #in pixels (roughly)
STEREO_BASELINE = 0.1 #in meteres

app = Flask(__name__)

# need to add checks and logic for if one camera detects a drone and the other doesn't
# also need check to match up boxes if they are not in the same order
def calculate_distance(boxes):    
    distances = []
    for i in range(0, len(boxes[0])):
        centerL = (boxes[0][i]['xyxy'][0] + boxes[0][i]['xyxy'][2]) / 2
        centerR = (boxes[1][i]['xyxy'][0] + boxes[1][i]['xyxy'][2]) / 2
        print(centerL, centerR)
        distance = STEREO_BASELINE * CAM_FOCAL_LENGTH / abs(centerL - centerR)
        distances.append(distance)
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
        distances = calculate_distance([boxes[i], boxes[i+1]])
        data.append(distances)
            
    return data


@app.route("/test")
def test():
    return 'Server is Live'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
