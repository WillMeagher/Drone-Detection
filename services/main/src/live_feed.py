import os
import threading
from tools import camera_client, speed_test
from pipeline import pipeline, pipeline_stereo
import cv2

from dotenv import load_dotenv
load_dotenv()

DUAL_CAM = os.getenv("DUAL_CAM") == "True"
PORT_0 = int(os.getenv("CAM_PORT_0"))
PORT_1 = int(os.getenv("CAM_PORT_1"))
HOST = os.getenv("DOCKER_INTERNAL_HOST")

TEMP_FOLDER = os.getenv("APP_DYNAMIC_FOLDER")
IMAGE_NAME = os.getenv("FEED_FILE_NAME")

class LiveThread:
    def __init__(self):
        self.running = False
        self.thread = None
        self.frame_getter_0 = None
        self.frame_getter_1 = None

    def start_thread(self):
        if self.thread is None or not self.running:
            self.thread = threading.Thread(target=self._capture_frames)
            self.running = True
            
            self.frame_getter_0 = camera_client.FrameCapture(PORT_0, HOST)
            if DUAL_CAM:
                self.frame_getter_1 = camera_client.FrameCapture(PORT_1, HOST)
            
            if self.frame_getter_0.start() and (not DUAL_CAM or self.frame_getter_1.start()):
                self.thread.start()
            else:
                self.running = False

    def stop_thread(self):
            
        self.running = False

        if self.frame_getter_0.is_running():
            self.frame_getter_0.stop()
        if DUAL_CAM and self.frame_getter_1.is_running():
            self.frame_getter_1.stop()

        if os.path.exists(TEMP_FOLDER + IMAGE_NAME):
            os.remove(TEMP_FOLDER + IMAGE_NAME)
    
    def is_running(self):
        return self.running

    def _capture_frames(self):
        frame_0, frame_1 = None, None
        output_frame = None

        while self.running:
            if frame_0 is None:
                frame_0 = self.frame_getter_0.new_frame()
            if frame_1 is None and DUAL_CAM:
                frame_1 = self.frame_getter_1.new_frame()

            if frame_0 is not None and (not DUAL_CAM or frame_1 is not None):
                if DUAL_CAM:
                    output_frame = pipeline_stereo([frame_0, frame_1])[0]
                else:
                    output_frame = pipeline([frame_0])[0]

                frame_0, frame_1 = None, None

                cv2.imwrite(TEMP_FOLDER + IMAGE_NAME, output_frame)


if __name__ == "__main__":
    feed = LiveThread()
    try:
        feed.start_thread()
    finally:
        feed.stop_thread()
