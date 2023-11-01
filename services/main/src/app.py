from flask import Flask, render_template, request, redirect, url_for, Response, send_file
import os
import numpy as np
from PIL import Image
import cv2
import uuid
import imageio
import time
import json

from pipeline import pipeline

app = Flask(__name__)

TEMP_FOLDER = "/app/static/"
os.makedirs(TEMP_FOLDER, exist_ok=True)

OUTPUT_FOLDER = "/app/data/annotated/"

frame = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x02\x01\x01\x01\x01\x01\x02\x01\x01\x01\x02\x02\x02\x02\x02\x04\x03\x02\x02\x02\x02\x05\x04\x04\x03\x04\x06\x05\x06\x06\x06\x05\x06\x06\x06\x07\t\x08\x06\x07\t\x07\x06\x06\x08\x0b\x08\t\n\n\n\n\n\x06\x08\x0b\x0c\x0b\n\x0c\t\n\n\n\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfd\xfc\xaf\xff\xd9'

def get_frames():
    global frame
    while True:
        time.sleep(0.2)
        yield (b'--frame\r\nContent-Type: text/plain\r\n\r\n' + frame + b'\r\n')       


@app.route('/')
def index():
    return render_template('image.html')

@app.route('/live_feed')
def liveFeed():
    return render_template('live_feed.html')


@app.route('/upload_image', methods=['POST', 'GET'])
def upload_image():
    if 'image' not in request.files:
        return render_template('image.html')

    image = request.files['image']

    if image.filename == '':
        return render_template('image.html')

    if image:
        # get uploaded image as opencv image
        pil_image = Image.open(image)
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        annotated_images = pipeline([opencv_image])

        # save annotated image to temp folder
        image_files = []
        for img in annotated_images:
            temp_filename = str(uuid.uuid4()) + '.jpg'
            file_path = os.path.join(TEMP_FOLDER, temp_filename)
            cv2.imwrite(file_path, img)
            image_files.append(temp_filename)

        return render_template('image.html', annotated_image_files=image_files)


@app.route('/upload_video', methods=['POST', 'GET'])
def upload_video():
    if 'video' not in request.files:
        return render_template('video.html')

    video = request.files['video']

    if video.filename == '':
        return render_template('video.html')

    if video:
        # save video to temp folder
        temp_filename = str(uuid.uuid4()) + '.mp4'
        file_path = os.path.join(TEMP_FOLDER, temp_filename)

        video.save(file_path)

        cap = cv2.VideoCapture(file_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        cap.release()

        os.remove(file_path)

        annotated_video = pipeline(frames)

        writer = imageio.get_writer(file_path, fps=fps)

        for cv2_img in annotated_video:
            pil_img = Image.fromarray(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB))
            writer.append_data(np.array(pil_img))
        writer.close()

        return render_template('video.html', video_filename=temp_filename)

@app.route('/frame', methods=['GET', 'POST'])
def frame_route():
    if request.method == 'GET':
        response = Response(get_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    else:
        global frame
        frame = request.data
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/file/<filename>')
def serve_file(filename):
    file_path = os.path.join(TEMP_FOLDER, filename)
    return send_file(file_path)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')