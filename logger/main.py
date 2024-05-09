import threading
import socket
import cv2
from picamera2 import Picamera2
import numpy as np
import os
import requests
from datetime import datetime
import csv
from dotenv import load_dotenv
import qwiic_bme280
import sys
import time
import json

# Global event to signal threads to stop
stop_event = threading.Event()

# Load environment variables
load_dotenv()

# Access your API token
api_token = os.getenv("API_TOKEN")

#an area in which to ignore activity
ignore_zone = None



# Initialize BME280 sensor
mySensor = qwiic_bme280.QwiicBme280()
if not mySensor.connected:
    print(
        "The Qwiic BME280 device isn't connected to the system. Please check your connection",
        file=sys.stderr,
    )
else:
    mySensor.begin()
    mySensor.filter = 1
    mySensor.standby_time = 0
    mySensor.over_sample = 1
    mySensor.pressure_oversample = 1
    mySensor.humidity_oversample = 1
    mySensor.mode = mySensor.MODE_NORMAL

def get_ignore_zone():
    ignore_zone = os.getenv("IGNORE_ZONE")
    if ignore_zone:
        x, y, width, height = map(int, ignore_zone.split(','))
        return x, y, width, height
    return None
class CameraManager:
    def __init__(self):
        self.camera = Picamera2()
        self.lock = threading.Lock()
        self.low_res_config = self.camera.create_video_configuration(
            main={"size": (640, 480)}
        )
        # , "format": "XRGB8888" is required for the PI HQ cam to get accurate colors
        self.high_res_config = self.camera.create_video_configuration(
            main={"size": (2560, 1440), "format": "XRGB8888"}
        )
        print("cam started")

    def configure(self, config):
        with self.lock:
            self.camera.stop()
            self.camera.configure(config)
            self.camera.start()

    def capture_frame(self):
        with self.lock:
            try:
                try:
                    frame = self.camera.capture_array()
                except Exception as e:
                    print(
                        f"An unexpected error occurred while capturing the frame: {type(e).__name__}, {str(e)}"
                    )
                    return None

                return frame
            except Exception as e:
                print(f"Failed to capture frame: {e}")
                return None

    def stop(self):
        print("stop")
        with self.lock:
            self.camera.stop()


camera_manager = CameraManager()

def merge_contours_and_get_bboxes(contours):
    # Helper function to calculate bounding box from a contour
    def get_bounding_box(contour):
        print("Received contour:", contour)
    
        # Convert the points in the contour to lists of x and y coordinates
        coords = zip(*[pt[0] for pt in contour]) if contour else ([], [])
        # print(coords)
        try:
            x_coords, y_coords =coords
            print
        except:
            return [0, 0, 0, 0] 
        # Since we're unpacking directly, no need to check len(), it'll raise an error if not correct
        print("fush")
        if x_coords and y_coords:  # Check if there are any coordinates to process
            print("rect")
            return min(x_coords), min(y_coords), max(x_coords), max(y_coords)
        else:
            return [0, 0, 0, 0] 
    
    # Helper function to check if two bounding boxes overlap
    def boxes_intersect(box1, box2):
        return (box1[0] <= box2[2] and box1[2] >= box2[0] and
                box1[1] <= box2[3] and box1[3] >= box2[1])
    
    merged_bboxes = []
    used = set()
    print("location 1")
    print("location 2",contours)
    for i, cont1 in enumerate(contours):
        print("Type of cont1 before calling get_bounding_box:", type(cont1))
        print("cont1: ", cont1)
    
        if i in used:
            continue
        print("cont1: ", cont1)
        bound1 = get_bounding_box(cont1)
        print("bound 1", bound1)
        for j, cont2 in enumerate(contours):
            if i != j and j not in used:
                bound2 = get_bounding_box(cont2)
                if boxes_intersect(bound1, bound2):
                    # Expand the bounding box to include both contours
                    merged_x1 = min(bound1[0], bound2[0])
                    merged_y1 = min(bound1[1], bound2[1])
                    merged_x2 = max(bound1[2], bound2[2])
                    merged_y2 = max(bound1[3], bound2[3])
                    bound1 = (merged_x1, merged_y1, merged_x2, merged_y2)
                    used.add(j)
        # Store the merged bounding box
        bbox  = bound1
        if len(bbox) ==4:
            x, y, x2, y2 = bound1
            width = x2 - x
            height = y2 - y
            merged_bboxes.append([x, y, width, height])
        else:
            print("unable to get bbox", bbox)
        used.add(i)
    
    return merged_bboxes


def generate_or_append_csv(data):
    filename = "data.csv"
    file_exists = os.path.isfile(filename)
    with open(filename, mode="a" if file_exists else "w", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        if not file_exists:
            writer.writerow(["time", "temperature", "humidity", "media", "contour"])
        for row in data:
            writer.writerow(
                [row["time"], row["temperature"], row["humidity"], row["media"], row["contour"]]
            )
    print(
        f"Data {'appended to' if file_exists else 'written to'} '{filename}' successfully."
    )


def upload_file(url, headers, file_path, key):
    try:
        with open(file_path, "rb") as file:
            files = {key: (file_path, file)}
            response = requests.post(url, files=files, headers=headers)
            if response.status_code in [200, 201]:
                print(f"{file_path} uploaded successfully.")
            else:
                print(
                    f"Failed to upload {file_path}. Status code: {response.status_code}, Error:",
                    response.text,
                )
    except Exception as e:
        print(f"An error occurred: {e}")


def capture_data(contour=None):
    print("capture")
    contour_data = json.dumps(contour.tolist()) if contour is not None else "None"
    if not stop_event.is_set():
        now = datetime.now()
        file_name = now.strftime("%Y-%m-%d_%H-%M-%S")
        img_name = f"images/{file_name}.jpg"
        try:
            camera_manager.configure(camera_manager.high_res_config)
            frame = camera_manager.capture_frame()
            cv2.imwrite(img_name, frame)  # Assuming the frame is directly savable

        finally:
            camera_manager.configure(camera_manager.low_res_config)
        merged_rects = merge_contours_and_get_bboxes(contour)
        data = [
            {
                "time": now.timestamp(),
                "temperature": (
                    mySensor.temperature_celsius if mySensor.connected else 0
                ),
                "humidity": mySensor.humidity if mySensor.connected else 0,
                "media": file_name,
                "contour": contour_data
            }
        ]
        print(data)
        generate_or_append_csv(data)
        # FIRST upload the event data csv file, then upload the images
        upload_file(
            "https://api.spaia.co.za/field/events",
            {"Authorization": f"Bearer {api_token}"},
            "data.csv",
            "events",
        )
        upload_file(
            "https://api.spaia.co.za/media",
            {"Authorization": f"Bearer {api_token}"},
            img_name,
            "file",
        )

        try:
            os.remove(img_name)
            os.remove("data.csv")
        except OSError as e:
            print(f"Error removing files: {e.strerror} - {e.filename}")


def motion_detection():
    camera_manager.configure(camera_manager.low_res_config)
    ignore_zone = get_ignore_zone()
    try:
        # camera_manager.configure(camera_manager.low_res_config)
        first_frame = None
        while not stop_event.is_set():
            try:
                frame = camera_manager.capture_frame()
                if frame is None:
                    print("No frame captured.")
                    continue  # Ensures the loop continues even if a frame isn't captured

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)
                if first_frame is None:
                    first_frame = gray
                    print("Set first frame.")
                    continue

                frame_delta = cv2.absdiff(first_frame, gray)
                thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)
                contours, _ = cv2.findContours(
                    thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )

                motion_detected = False
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if 10 < area < 1000:
                        continue
                    print("Motion detected!")
                    capture_data(contour)  # This will capture and upload data
                    motion_detected = True
                    break  # Break after the first detection to avoid multiple captures

                if motion_detected:
                    # print("Pausing motion detection for 10 seconds...")
                    # time.sleep(10)  # Pause for 30 seconds after capturing data
                    first_frame = None
            except Exception as e:
                print(f"Error during motion detection: {e}")

    except Exception as e:
        print(f"Error in setting up motion detection: {e}")
    finally:
        print("Motion detection stopped")


def socket_listener():

    host = "localhost"
    port = 9090
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        while True:
            client_socket, addr = server_socket.accept()
            with client_socket:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    print("radar data")
                    capture_data()


def main():
    # Start threads

    motion_thread = threading.Thread(target=motion_detection)
    capture_thread = threading.Thread(target=capture_data)
    socket_thread = threading.Thread(target=socket_listener)

    motion_thread.start()
    # capture_thread.start()
    # socket_thread.start()
    try:
        # Wait for user to indicate shutdown
        input("Press Enter to stop...\n")
    finally:
        # Signal all threads to stop
        stop_event.set()

        # Wait for all threads to complete
        motion_thread.join()
        # capture_thread.join()
        # socket_thread.join()

        print("All threads have been stopped gracefully.")


if __name__ == "__main__":
    main()
