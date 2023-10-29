from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from PIL import Image  # Pillow library for image processing
import cv2  # OpenCV for computer vision (for annotating images)
import numpy as np
from config import config
import requests
import json
import uuid  # For generating unique filenames
from matplotlib import pyplot as plt
import shutil

app = Flask(__name__)

annotated_folder = config['annotated_folder']
upload_folder = config['uploaded_folder']

# Ensure the annotated folder exists
os.makedirs(annotated_folder, exist_ok=True)
os.makedirs(upload_folder, exist_ok=True)

# Function to process the uploaded image and annotate it (you will need to implement this part)
def process_image(unique_filename):
    image_path = os.path.join(upload_folder, unique_filename)
    
    # call yolo-localization service to get bounding boxes
    r = requests.get(config['yolo_endpoint'], {'img': image_path})
    boxes = json.loads(r.content)
    
    # begin processing photo locally
    img = cv2.imread(image_path)
    
    # annotate boxes onto image and send to clip for classification
    cmap = plt.get_cmap('viridis')
    font = cv2.FONT_HERSHEY_SIMPLEX
    for box in boxes:
        startPoint = int(box['xyxy'][0]), int(box['xyxy'][1])
        endPoint = int(box['xyxy'][2]), int(box['xyxy'][3])
        
        # this is specifically we would hit the clip service
        
        color = cmap(box['conf'])
        color = color[2] * 255, color[1] * 255, color[0] * 255
        cv2.rectangle(img, startPoint, endPoint, color=color, thickness = 2)
        cv2.rectangle(img, startPoint, (startPoint[0] + 200, startPoint[1] - 25), color=color, thickness = -1)
        text = f'Drone - {box["conf"]:.2f}%'
        cv2.putText(img, text, (startPoint[0] + 2, startPoint[1] - 2), font, 0.75, color=(255, 255, 255), bottomLeftOrigin=False, thickness = 2)
    
    # save the annotated version so it can be served
    save_path = os.path.join(annotated_folder, unique_filename)
    cv2.imwrite(save_path, img)

    return unique_filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return redirect(url_for('index'))

    image = request.files['image']

    if image.filename == '':
        return redirect(url_for('index'))

    if image:
        # Save the uploaded image to the UPLOAD_FOLDER
        unique_filename = str(uuid.uuid4()) + '.jpg'
        image_path = os.path.join(upload_folder, unique_filename)
        image.save(image_path)
        
        # Process the image and get the unique annotated image filename
        annotated_image_filename = process_image(unique_filename)

        return render_template('index.html', annotated_image=annotated_image_filename)

@app.route('/annotated/<filename>')
def annotated_file(filename):
    return send_from_directory(annotated_folder, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
