from picamera2 import Picamera2
import numpy as np
import cv2

def detect_motion():
    picam2 = Picamera2()
    preview_config = picam2.create_preview_configuration()
    picam2.configure(preview_config)
    picam2.start()

    # Initialize variables for motion detection
    first_frame = None
    while True:
        frame = picam2.capture_array()  # Capture frame as numpy array
        text = "Unoccupied"

        # Convert frame to grayscale and blur it
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if first_frame is None:
            first_frame = gray
            continue

        # Compute the absolute difference between the current frame and first frame
        frame_delta = cv2.absdiff(first_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        # Find contours on the thresholded image
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Loop over the contours
        for contour in contours:
            if cv2.contourArea(contour) < 200:  # Adjust size as needed for your context
                continue
            # If the contour is big enough, consider it motion
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            print(f"bug")
            text = "Occupied"

        # Display the resulting frame
        # cv2.imshow("Camera Feed", frame)
        # cv2.imshow("Thresh", thresh)
        # cv2.imshow("Frame Delta", frame_delta)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    picam2.stop()
    cv2.destroyAllWindows()

detect_motion()
