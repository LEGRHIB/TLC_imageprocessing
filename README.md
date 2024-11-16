# TLC_imageprocessing
This project automates TLC analysis by capturing and processing TLC plate images, saving time and improving accuracy. We utilize image recognition techniques to measure distances on TLC plates and automatically store the data in an MES.
# Project Description
This project aims to automate the TLC (Thin Layer Chromatography) process by enhancing image capture and data analysis. The primary goal is to reduce manual tasks, improve accuracy, and streamline the workflow by automating key steps, including capturing TLC images under UV light, measuring the distance of sample spots, and storing results in a Manufacturing Execution System (MES). We aim to create a system that is efficient and reliable for lab environments.
## Short term
## uvclick.py Usage Instructions

This application provides an interactive interface for annotating TLC images and calculating spot-to-baseline ratios. It is designed to simplify the process for operators by allowing them to pick key points on the image, with the application handling pixel-based ratio calculations.

### Steps for Annotation:

1. **Load an Image**:
   - Place your image in the specified path (default: `./sorted_images/uv/100917.jpg`).
   - Run the script to load and display the image.

2. **Start Annotation**:
   - Press `n` to start annotating a new TLC plate.

3. **Annotate Key Features**:
   - **Baseline**: Press `b` and click on the baseline of the plate.
   - **Solvent Line**: Press `s` and click on the solvent line.
   - **Spots**: Press `o` and click on the spots of interest.

   Points will be color-coded for clarity:
   - Red for the baseline.
   - Blue for the solvent line.
   - Green for spots.

4. **Finish Annotation**:
   - Press `q` to calculate ratios and display the results in the terminal.

     ## Update Summary
Addition of Stain Images:
Stain images are incorporated to detect additional spots that may not be visible in UV images.
The operator annotates baseline, solvent line, and spots for both UV and stain images.
Integration of UV and Stain Data:
Spots from stain images are recalibrated to align with the UV baseline and solvent line.
UV and stain spots are combined into a single dataset for processing.
Deduplication of Spots:
Spots detected in both UV and stain images are automatically merged if they are within a 0.1 cm tolerance to avoid duplication.
Automatic Component Ordering:
All spots are sorted by their distance from the baseline.
Components are automatically numbered in ascending order of their distance.
Operator Workflow:
The operator annotates UV images first, switches to stain images, and annotates any additional spots.
The app handles deduplication, recalibration, and component ordering automatically

### Output:

- The application computes the ratio of the distance from each spot to the baseline divided by the distance from the solvent line to the baseline.
- Results are displayed as a list of spots and their respective ratios for each plate.

### Alignment with Goals:

This tool is aligned with the short-term goal of enabling operators to:
- Interactively annotate TLC images via a simple interface.
- Automate the calculation of spot-to-baseline ratios using pixel distances.
- Visualize annotations directly on the image for immediate feedback and accuracy.
## long term:
# Steps:
# 1-Image Capture:

Capture TLC images under normal light and UV light using a camera setup.
# 2-TLC Plate Detection:
Detect six TLC plates in each image and segment them for further analysis.

# 3-Baseline and Solvent Front Detection:
Identify and mark the baseline and the solvent front line on each TLC plate.

# 4-Distance Measurement:
Measure distances from the baseline to the solvent front and from the baseline to the sample spots on each plate.

# 5-UV Light Detection:
Detect and highlight sample spots visible under UV light.

# 6-Data Storage:
Automatically save the processed results (spot measurements, distances from baseline and solvent front, etc.) in the Manufacturing Execution System (MES).
# 7-User Interface:
Implement a simple interface for users to upload images and view processed results.

# 8-Automation and Integration:
Integrate the system with the lab's current workflow, ensuring compatibility with existing MES.
