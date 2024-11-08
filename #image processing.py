# Import necessary libraries
import cv2
import numpy as np
import matplotlib.pyplot as plt

# Define the path to the image
image_path = '/workspaces/TLC_imageprocessing/TLC1.png'  # Ensure this is the correct path
image = cv2.imread(image_path)

# Check if the image was loaded
if image is None:
    print("Error: Image not loaded. Check the path and file name.")
else:
    # Convert the image to the HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the range for detecting low green pixels (TLC plates)
    lower_green = np.array([35, 30, 30])  # Adjust for clearer low green
    upper_green = np.array([85, 255, 255])  # Define the upper boundary for green

    # Create a mask for the TLC plate (low green pixels)
    plate_mask = cv2.inRange(hsv_image, lower_green, upper_green)

    # Apply morphological operations to clean up the mask
    kernel = np.ones((3, 3), np.uint8)
    plate_mask = cv2.morphologyEx(plate_mask, cv2.MORPH_CLOSE, kernel)  # Fill small holes
    plate_mask = cv2.morphologyEx(plate_mask, cv2.MORPH_OPEN, kernel)   # Remove small noise

    # Convert the image to grayscale and enhance contrast
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    equalized_image = cv2.equalizeHist(gray_image)
    masked_equalized = cv2.bitwise_and(equalized_image, equalized_image, mask=plate_mask)

    # Apply edge detection to create a black-and-white edge image
    edges = cv2.Canny(masked_equalized, 50, 150)

    # Display and save the black-and-white edges image
    plt.figure()
    plt.imshow(edges, cmap='gray')
    plt.title("Black Background with White Edges")
    plt.axis('off')
    plt.show()
    cv2.imwrite('/workspaces/TLC_imageprocessing/tlc_edges_black_white.jpg', edges)
    print("Black background with white edges image saved as 'tlc_edges_black_white.jpg' in /workspaces/TLC_imageprocessing/")

    # Find contours based on the edges detected
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw white contours (lines) on the original image
    image_with_contours = image.copy()
    cv2.drawContours(image_with_contours, contours, -1, (255, 255, 255), 2)  # White color, thickness=2

    # Convert BGR to RGB for displaying with matplotlib
    image_with_contours_rgb = cv2.cvtColor(image_with_contours, cv2.COLOR_BGR2RGB)

    # Display and save the image with white line contours
    plt.figure(figsize=(10, 5))
    plt.imshow(image_with_contours_rgb)
    plt.title('TLC Plates with White Line Contours')
    plt.axis('off')
    plt.show()
    cv2.imwrite('/workspaces/TLC_imageprocessing/tlc_white_line_contours_enhanced.jpg', image_with_contours)
    print("Final image with contours saved as 'tlc_white_line_contours_enhanced.jpg' in /workspaces/TLC_imageprocessing/")
