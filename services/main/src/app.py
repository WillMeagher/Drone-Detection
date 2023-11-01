from flask import Flask, render_template, request, redirect, url_for, Response, send_file
import os
import numpy as np
from PIL import Image
import cv2
import uuid
import imageio
import time
import os

from pipeline import pipeline
from live_feed import LiveThread

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

TEMP_FOLDER = os.getenv("APP_DYNAMIC_FOLDER")
FEED_IMAGE_NAME = os.getenv("FEED_FILE_NAME")

os.makedirs(TEMP_FOLDER, exist_ok=True)
feed = LiveThread()


@app.route('/')
def index():
    return render_template('image.html')


@app.route('/live_feed')
def liveFeed():
    return render_template('live_feed.html', live_feed=str(feed.is_running()).lower())


@app.route('/start_feed', methods=['POST', 'GET'])
def start_feed():
    if not feed.is_running():
        feed.start_thread()
    return redirect(url_for('liveFeed'))


@app.route('/stop_feed', methods=['POST', 'GET'])
def stop_feed():
    if feed.is_running():
        feed.stop_thread()
    return redirect(url_for('liveFeed'))


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

def get_frame():
    while True:
        time.sleep(0.5)
        frame = None
        if feed.is_running():
            frame = cv2.imread(TEMP_FOLDER + FEED_IMAGE_NAME)
        if frame is None:
            frame = cv2.imread('static/404.jpg')
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + open(TEMP_FOLDER + FEED_IMAGE_NAME, 'rb').read() + b'\r\n')

@app.route('/get_feed')
def get_feed():
    response = Response(get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/file/<filename>')
def serve_file(filename):
    file_path = os.path.join(TEMP_FOLDER, filename)

    if not os.path.exists(file_path):
        return url_for('static', filename='404.jpg')

    return send_file(file_path)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)