import cv2
import socket
import os
from dotenv import load_dotenv
load_dotenv()

DUAL_CAM = os.getenv("DUAL_CAM") == "True"
PORT_0 = int(os.getenv("CAM_PORT_0"))
PORT_1 = int(os.getenv("CAM_PORT_1"))
ID_0 = int(os.getenv("CAM_ID_0"))
ID_1 = int(os.getenv("CAM_ID_1"))
HOST = os.getenv("HOST_HOST")

server_socket_0, server_socket_1 = None, None
cap_0, cap_1 = None, None

def main():
    server_socket_0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket_0.bind((HOST, PORT_0))
    server_socket_0.listen(5)
    print(f"Listening on port {PORT_0} ...")
    cap_0 = cv2.VideoCapture(ID_0, cv2.CAP_DSHOW)
    cap_0.set(3, 1280)
    cap_0.set(4, 720)

    if DUAL_CAM:
        server_socket_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket_1.bind((HOST, PORT_1))
        server_socket_1.listen(5)
        print(f"Listening on port {PORT_1} ...")
        cap_1 = cv2.VideoCapture(ID_1, cv2.CAP_DSHOW)
        cap_1.set(3, 1280)
        cap_1.set(4, 720)

    while True:
        client_socket_0, client_address_0 = server_socket_0.accept()
        print(f"Accepted connection from {client_address_0}")

        if DUAL_CAM:
            client_socket_1, client_address_1 = server_socket_1.accept()
            print(f"Accepted connection from {client_address_1}")

        try:
            while True:
                ret, frame = cap_0.read()
                if not ret:
                    break

                # Encode the frame as JPEG
                _, encoded_frame = cv2.imencode('.jpg', frame)
                frame_size = len(encoded_frame).to_bytes(4, byteorder='big')

                # Send frame size and frame data to the client
                client_socket_0.send(frame_size)
                client_socket_0.send(encoded_frame.tobytes())

                if DUAL_CAM:
                    ret, frame = cap_1.read()
                    if not ret:
                        break

                    # Encode the frame as JPEG
                    _, encoded_frame = cv2.imencode('.jpg', frame)
                    frame_size = len(encoded_frame).to_bytes(4, byteorder='big')

                    # Send frame size and frame data to the client
                    client_socket_1.send(frame_size)
                    client_socket_1.send(encoded_frame.tobytes())

        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket_0.close()
            
            if DUAL_CAM:
                client_socket_1.close()

def cleanup():
    if server_socket_0:
        server_socket_0.close()
    
    if server_socket_1:
        server_socket_1.close()

    if cap_0:
        cap_0.release()

    if cap_1:
        cap_1.release()

if __name__ == "__main__":
    try:
        main()
    finally:
        cleanup()