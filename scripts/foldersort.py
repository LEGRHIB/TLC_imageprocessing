import os
import cv2
import shutil

# Input and output folder paths
input_folder = "./images/tlc_images"
uv_folder = "./sorted_images/uv"
stain_folder = "./sorted_images/stain"

# Create output folders if they don’t exist
os.makedirs(uv_folder, exist_ok=True)
os.makedirs(stain_folder, exist_ok=True)

# Define a threshold for intensity classification
uv_threshold = 100  # Adjust based on visual properties of your images

# Iterate through all images in the input folder
for filename in os.listdir(input_folder):
    # Construct the full path of the image
    image_path = os.path.join(input_folder, filename)

    # Load the image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print(f"Could not load {filename}. Skipping...")
        continue

    # Calculate average intensity
    avg_intensity = image.mean()

    # Classify and move the image
    if avg_intensity < uv_threshold:
        # Move to UV folder
        shutil.move(image_path, os.path.join(uv_folder, filename))
        print(f"{filename} classified as UV and moved to {uv_folder}")
    else:
        # Move to Stain folder
        shutil.move(image_path, os.path.join(stain_folder, filename))
        print(f"{filename} classified as Stain and moved to {stain_folder}")
