import matplotlib.pyplot as plt
import numpy as np
import cv2

# Define the contour points from the cv2.findContours() results
contour = np.array([[[33, 372]], [[33, 377]], [[38, 377]], [[38, 373]], [[37, 372]]])
# Create a blank image
image_height, image_width = 480, 640
image = np.zeros((image_height, image_width, 3), dtype=np.uint8)

# Draw the contour on the image
cv2.drawContours(image, [contour], -1, (255, 255, 255), 1)

# Draw bounding rectangles around the contour
x, y, w, h = cv2.boundingRect(contour)
cv2.rectangle(image, (x-5, y-5), (x + w+5, y + h+5), (0, 255, 0), 2)

area = cv2.contourArea(contour)

# Plot the image with the contour and bounding box
plt.figure(figsize=(8, 6))
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
plt.title('Contour and Bounding Box Visualization on 640x480 Frame. area:' + str(area))
plt.show()
