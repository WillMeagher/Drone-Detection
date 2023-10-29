Northrop Grumman Drone Detection Challenge

This repository contains a Docker-based machine learning project aimed at addressing the Northrop Grumman Drone Detection Challenge. The goal of this project is to create and retrain an image recognition neural network capable of detecting and classifying small UAVs (drones) within an image.

Project Timeline
Start Date: October 23, 2023
End Date: November 2, 2023

Notes from Ethan:  
This is the best looking dataset I came across: [df](https://www.kaggle.com/datasets/sshikamaru/drone-yolo-detection)

I made an app in the main container which just allows uploading images and being sent back the images with the bounding boxes the yolo model finds. I did not write any code for training/tuning the model, the server just uses whatever weights file you point it at in the config file. The app can be running by calling `make start` then `make deploy`. My start scripts are a little scuffed but they work. I had an issue with the main container where the `requests` library is always missing, even though it is in `requirements.txt`. No idea whats going on there