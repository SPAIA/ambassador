from picamera2 import Picamera2
from libcamera import controls
import cv2
picam2 = Picamera2()
picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous, "AfSpeed": controls.AfSpeedEnum.Fast})
camera_config = picam2.create_still_configuration(main={"size": (3280,2464), "format": "XRGB8888"})
picam2.configure(camera_config)
picam2.start()
print("go")
picam2.set_controls({"AfMode":controls.AfModeEnum.Continuous, "AfRange":controls.AfRangeEnum.Macro})
try:
    frame = picam2.capture_array()
except Exception as e:
    print(
        f"An unexpected error occurred while capturing the frame: {type(e).__name__}, {str(e)}"
    )

cv2.imwrite("continuous.jpg", frame)
picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 8.0})
try:
    frame = picam2.capture_array()
except Exception as e:
    print(
        f"An unexpected error occurred while capturing the frame: {type(e).__name__}, {str(e)}"
    )

cv2.imwrite("8.jpg", frame)
picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition":5})
try:
    frame = picam2.capture_array()
except Exception as e:
    print(
        f"An unexpected error occurred while capturing the frame: {type(e).__name__}, {str(e)}"
    )

cv2.imwrite("5.jpg", frame)
picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 2.0})
try:
    frame = picam2.capture_array()
except Exception as e:
    print(
        f"An unexpected error occurred while capturing the frame: {type(e).__name__}, {str(e)}"
    )

cv2.imwrite("2.jpg", frame)
picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 1})
try:
    frame = picam2.capture_array()
except Exception as e:
    print(
        f"An unexpected error occurred while capturing the frame: {type(e).__name__}, {str(e)}"
    )

cv2.imwrite("1.jpg", frame)
print("wrote")