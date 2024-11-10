#image processing
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.filters import threshold_otsu

# Load the image
image_path = '../images/TLC1.png'  # Ensure this is the correct path
image = cv2.imread(image_path)

# Convert the image to the HSV color space
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Define the refined range for detecting low green pixels (TLC plates)
lower_green = np.array([35, 30, 30])  # Adjust for clearer low green
upper_green = np.array([85, 255, 255])  # Define the upper boundary for green

# Create a mask for the TLC plate (low green pixels)
plate_mask = cv2.inRange(hsv_image, lower_green, upper_green)

# Apply morphological operations to clean up the mask
kernel = np.ones((3, 3), np.uint8)
plate_mask = cv2.morphologyEx(plate_mask, cv2.MORPH_CLOSE, kernel)  # Fill small holes
plate_mask = cv2.morphologyEx(plate_mask, cv2.MORPH_OPEN, kernel)   # Remove small noise

# Enhance contrast using adaptive histogram equalization on the masked area
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
equalized_image = cv2.equalizeHist(gray_image)
masked_equalized = cv2.bitwise_and(equalized_image, equalized_image, mask=plate_mask)

# Apply edge detection (try Canny on contrast-enhanced image)
edges = cv2.Canny(masked_equalized, 50, 150)

# Find contours based on the edges detected
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Draw white contours (lines) on the original image
image_with_contours = image.copy()
cv2.drawContours(image_with_contours, contours, -1, (255, 255, 255), 2)  # White color, thickness=2

# Convert BGR to RGB for displaying with matplotlib
image_with_contours_rgb = cv2.cvtColor(image_with_contours, cv2.COLOR_BGR2RGB)

# Plotting the results
plt.figure(figsize=(10, 5))

# Display the original image with white lines around contours
plt.subplot(1, 2, 1)
plt.imshow(image_with_contours_rgb)
plt.title('TLC Plates with White Line Contours')
plt.axis('off')

# Display the dilated edges detected
plt.subplot(1, 2, 2)
plt.imshow(edges, cmap='gray')
plt.title('Detected Edges')
plt.axis('off')

# Show all plots
plt.tight_layout()
plt.show()

# Optionally, save the final image with contours
cv2.imwrite('/mnt/data/tlc_white_line_contours_enhanced.jpg', image_with_contours)

