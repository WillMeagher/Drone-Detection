import os
import cv2

from tools import camera_client, speed_test, input_check
from pipeline import pipeline, pipeline_stereo

from dotenv import load_dotenv
load_dotenv()

DUAL_CAM = os.getenv("DUAL_CAM") == "True"
PORT_0 = int(os.getenv("CAM_PORT_0"))
PORT_1 = int(os.getenv("CAM_PORT_1"))
HOST = os.getenv("DOCKER_INTERNAL_HOST")

OUTPUT_FOLDER = "/app/data/annotated/"

frame_getter_0, frame_getter_1 = None, None

frame_getter_0 = camera_client.FrameCapture(PORT_0, HOST)
if DUAL_CAM:
    frame_getter_1 = camera_client.FrameCapture(PORT_1, HOST)

def main():

    speed_tester = speed_test.SpeedTest(loops_per_print=10)

    if frame_getter_0.start() and (not DUAL_CAM or frame_getter_1.start()):
        frame_0, frame_1 = None, None

        while True:
            if frame_0 is None:
                frame_0 = frame_getter_0.new_frame()
            if frame_1 is None and DUAL_CAM:
                frame_1 = frame_getter_1.new_frame()

            if frame_0 is not None and (not DUAL_CAM or frame_1 is not None):

                if DUAL_CAM:
                    output_frame = pipeline_stereo([frame_0, frame_1])[0]
                else:
                    output_frame = pipeline([frame_0])[0]

                cv2.imwrite(OUTPUT_FOLDER + "img.jpg", output_frame)

                frame_0, frame_1 = None, None
                speed_tester.loop(print_loops=True)

            if input_check.check("q"):
                break
    else:
        print("Failed to connect to camera server")

def cleanup():
    input_check.exit()

    if frame_getter_0.is_running():
        frame_getter_0.stop()
    
    if DUAL_CAM and frame_getter_1.is_running():
        frame_getter_1.stop()

if __name__ == "__main__":
    try:
        main()
    finally:
        cleanup()