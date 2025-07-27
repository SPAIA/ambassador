from picamera2 import Picamera2
import threading
import time
import cv2
from libcamera import controls  # Ensure you import controls from libcamera

class CameraManager:
    def __init__(self):
        self.camera = Picamera2()
        self.lock = threading.Lock()
        self.low_res_config = self.camera.create_video_configuration(
            main={"size": (640, 480)}
        )
        self.high_res_config = self.camera.create_video_configuration(
            main={"size": (2304, 1296), "format": "XRGB8888"}
        )
        print("cam started")

    def configure(self, config):
        with self.lock:
            self.camera.stop()
            self.camera.configure(config)
            self.camera.start()

            # Auto exposure
            self.camera.set_controls({"AeEnable": True})
            self.camera.set_controls({"ExposureValue": 0.8})  # Adjust this value to ensure details in shadows
            
            # Increase sharpness
            self.camera.set_controls({"Sharpness": 2.0})  # Adjust sharpness level as needed, range typically from -2.0 to 2.0

    def set_manual_focus(self, lens_position):
        with self.lock:
            self.camera.set_controls({
                "AfMode": controls.AfModeEnum.Manual, 
                "LensPosition": lens_position
            })

    def capture_frame(self, filename):
        with self.lock:
            try:
                frame = self.camera.capture_array()
                if frame is not None:
                    cv2.imwrite(filename, frame)
                return frame
            except Exception as e:
                print(f"An unexpected error occurred while capturing the frame: {type(e).__name__}, {str(e)}")
                return None

    def stop(self):
        print("stop")
        with self.lock:
            self.camera.stop()

if __name__ == "__main__":
    camera_manager = CameraManager()
    camera_manager.configure(camera_manager.high_res_config)  # Use high resolution for clarity

    # Experiment with lens positions
    for lens_position in range(0, 8, 1):  # Adjust the range and step as needed
        print(f"Setting lens position to {lens_position/2}")
        camera_manager.set_manual_focus(lens_position/2)
        time.sleep(1)  # Allow time for the camera to adjust
        frame = camera_manager.capture_frame(f"focus_{lens_position/2}.jpg")
        if frame is None:
            print(f"Lens position {lens_position/2} is not valid")

    camera_manager.stop()
