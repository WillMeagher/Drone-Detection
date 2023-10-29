import requests
import os

from tools import camera_client, speed_test, input_check

from dotenv import load_dotenv
load_dotenv()

DUAL_CAM = os.getenv("DUAL_CAM") == "True"
PORT_0 = int(os.getenv("CAM_PORT_0"))
PORT_1 = int(os.getenv("CAM_PORT_1"))
HOST = os.getenv("DOCKER_INTERNAL_HOST")

frame_getter = camera_client.FrameCapture(PORT_0, HOST)

def main():

    speed_tester = speed_test.SpeedTest()

    if frame_getter.start():
        while True:
            frame = frame_getter.new_frame()
            if frame is not None:
                pass
            
                speed_tester.loop(print_loops=True)

            if input_check.check("q"):
                break
    else:
        print("Failed to connect to camera server")

def cleanup():
    input_check.exit()

    if frame_getter.is_running():
        frame_getter.stop()

if __name__ == "__main__":
    try:
        main()
    finally:
        cleanup()