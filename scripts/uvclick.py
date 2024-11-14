import cv2
import numpy as np

# Global variables to store points for multiple plates
plates = []  # List to hold plates (each plate is a dictionary with 'baseline', 'solvent_line', and 'spots')
current_plate = {"baseline": None, "solvent_line": None, "spots": []}  # Temp storage for the current plate

# Mouse callback function
def click_event(event, x, y, flags, param):
    global plates, current_plate
    image = param

    if event == cv2.EVENT_LBUTTONDOWN:  # Left click for points
        print(f"Point selected: {x}, {y}")
        if current_plate["baseline"] is None:
            current_plate["baseline"] = (x, y)
            print("Baseline selected.")
            cv2.circle(image, (x, y), 5, (0, 0, 255), -1)  # Red for baseline
        elif current_plate["solvent_line"] is None:
            current_plate["solvent_line"] = (x, y)
            print("Solvent line selected.")
            cv2.circle(image, (x, y), 5, (255, 0, 0), -1)  # Blue for solvent line
        else:
            current_plate["spots"].append((x, y))
            print(f"Spot selected ({len(current_plate['spots'])}): {x}, {y}")
            cv2.circle(image, (x, y), 5, (0, 255, 0), -1)  # Green for spots

        cv2.imshow("Image", image)

    elif event == cv2.EVENT_RBUTTONDOWN:  # Right click to finalize a plate
        print("Finalizing current plate.")
        plates.append(current_plate)
        current_plate = {"baseline": None, "solvent_line": None, "spots": []}
        print(f"Total plates defined so far: {len(plates)}")

def calculate_ratios(plates):
    ratios = []
    for plate in plates:
        baseline = plate["baseline"]
        solvent_line = plate["solvent_line"]
        spots = plate["spots"]

        if baseline is None or solvent_line is None or len(spots) == 0:
            print("Incomplete data for one plate. Skipping...")
            continue

        # Calculate solvent line to baseline distance
        solvent_to_baseline = np.linalg.norm(np.array(solvent_line) - np.array(baseline))
        if solvent_to_baseline == 0:
            print("Error: Solvent to baseline distance is zero. Skipping...")
            continue

        # Calculate each spot's ratio
        plate_ratios = []
        for spot in spots:
            spot_to_baseline = np.linalg.norm(np.array(spot) - np.array(baseline))
            ratio = spot_to_baseline / solvent_to_baseline
            plate_ratios.append(ratio)

        ratios.append(plate_ratios)
    return ratios

def main():
    global plates, current_plate

    # Load the image
    image_path = "./sorted_images/uv/100917.jpg"  # Replace with your image path
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image at {image_path}")
        return

    # Clone the image to redraw without losing original
    clone = image.copy()

    # Display the image and set up the mouse callback
    cv2.imshow("Image", clone)
    cv2.setMouseCallback("Image", click_event, param=clone)

    print("Instructions:")
    print("1. Left-click to select baseline, solvent line, and spots for a plate.")
    print("2. Right-click to finalize the plate and move to the next one.")
    print("3. Press 'q' to finish.")

    # Wait for user to complete
    cv2.waitKey(0)

    # Calculate ratios for all plates
    ratios = calculate_ratios(plates)

    # Print results
    for i, plate_ratios in enumerate(ratios):
        print(f"Plate {i + 1} Ratios:")
        for j, ratio in enumerate(plate_ratios):
            print(f"  Spot {j + 1}: {ratio:.2f}")

    # Clean up
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
