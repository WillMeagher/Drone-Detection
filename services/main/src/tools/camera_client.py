import socket
import cv2
import os
import numpy as np
import threading
import time

from dotenv import load_dotenv
load_dotenv()

class FrameCapture:
    def __init__(self, port, host):
        self.port = port
        self.host = host
        self.client_socket = None
        self.capture_thread = None
        self.frame = None
        self.running = False

    def start(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))

            self.running = True
            self.capture_thread = threading.Thread(target=self._capture_frames)
            self.capture_thread.start()
            return True
        except ConnectionRefusedError:
            return False

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False
        self.capture_thread.join()
        if self.client_socket:
            self.client_socket.close()

    # Returns the latest frame if available, otherwise returns None
    def new_frame(self):
        if self.frame is not None:
            frame = self.frame
            self.frame = None
            return frame
        else:
            return None

    def _capture_frames(self):
        while self.running:
            frame_size_bytes = self.client_socket.recv(4)
            frame_size = int.from_bytes(frame_size_bytes, byteorder='big')

            frame_data = b''

            while len(frame_data) < frame_size:
                data = self.client_socket.recv(frame_size - len(frame_data))
                if not data:
                    break
                frame_data += data

            if len(frame_data) < frame_size:
                break

            frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
            self.frame = frame

        self.client_socket.close()

if __name__ == "__main__":
    PORT = int(os.getenv("CAM_PORT_0"))
    HOST = os.getenv("DOCKER_INTERNAL_HOST")

    fc = FrameCapture(PORT, HOST)

    fc.start()

    try:
        while True:
            frame = fc.new_frame()
            if frame is not None:
                cv2.imwrite('frame.jpg', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    finally:
        fc.stop()
