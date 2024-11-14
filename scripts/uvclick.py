import cv2
import numpy as np

# Global variables to store clicked points
annotations = []
current_plate = None
current_annotation_type = None
plate_names = ["A: 50% DCM in Heptane", 
               "B: 50% EtOAc in Heptane", 
               "C: DCM", 
               "D: 50% EtOAc in DCM", 
               "E: EtOAc", 
               "F: 10% MeOH in DCM"]

# Color mapping for annotation types
annotation_colors = {
    "baseline": (0, 0, 255),       # Red for baseline
    "solvent_line": (255, 0, 0),   # Blue for solvent line
    "spots": (0, 255, 0)           # Green for spots
}

# Mouse callback function to capture points
def click_event(event, x, y, flags, param):
    global current_plate, current_annotation_type, annotations

    if event == cv2.EVENT_LBUTTONDOWN:  # Left click to select points
        if current_plate is not None and current_annotation_type:
            current_plate[current_annotation_type].append((x, y))
            print(f"{current_annotation_type} point selected for Plate {plate_names[len(annotations) - 1]}: ({x}, {y})")

            # Get the color for the current annotation type
            color = annotation_colors.get(current_annotation_type, (255, 255, 255))  # Default to white

            # Draw a small circle with the specified color
            cv2.circle(param, (x, y), 2, color, -1)  # Circle radius set to 2
            cv2.imshow("Image", param)

def calculate_ratios(annotations):
    results = []

    for i, plate in enumerate(annotations):
        baseline = plate.get("baseline")
        solvent_line = plate.get("solvent_line")
        spots = plate.get("spots", [])

        if not baseline or not solvent_line:
            print(f"Error: Plate {i + 1} is missing baseline or solvent line.")
            continue

        plate_results = {"spots": []}

        # Extract the y-coordinates of the baseline and solvent line
        baseline_y = baseline[0][1]  # Use the y-coordinate of the baseline point
        solvent_y = solvent_line[0][1]  # Use the y-coordinate of the solvent line point

        # Calculate distances and ratios for each spot
        for j, spot in enumerate(spots):
            spot_y = spot[1]  # Use the y-coordinate of the spot
            spot_to_baseline = abs(spot_y - baseline_y)  # Vertical distance from baseline
            solvent_to_baseline = abs(solvent_y - baseline_y)  # Vertical distance from baseline to solvent line

            if solvent_to_baseline == 0:
                print(f"Error: Solvent to baseline distance is zero for Plate {i + 1}.")
                continue

            ratio = spot_to_baseline / solvent_to_baseline
            plate_results["spots"].append({"spot": f"Spot {j + 1}", "ratio": ratio})

        results.append(plate_results)

    return results

def main():
    global current_plate, current_annotation_type, annotations

    # Load the image
    image_path = "./sorted_images/uv/100917.jpg"  # Replace with your image path
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image at {image_path}")
        return

    # Clone the image to redraw without losing the original
    clone = image.copy()

    # Instructions
    print("Instructions:")
    print("1. Press 'n' to start annotating a predefined plate.")
    print("2. Press 'b' to annotate baseline for the current plate.")
    print("3. Press 's' to annotate solvent line for the current plate.")
    print("4. Press 'o' to annotate spots for the current plate.")
    print("5. Press 'q' to finish and calculate ratios.")

    # Display the image and set up the mouse callback
    cv2.imshow("Image", image)
    cv2.setMouseCallback("Image", click_event, param=clone)

    plate_index = 0
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Quit
            break
        elif key == ord('n'):  # Start a new plate
            if plate_index < len(plate_names):
                print(f"Started annotating Plate {plate_names[plate_index]}.")
                current_plate = {"baseline": [], "solvent_line": [], "spots": []}
                annotations.append(current_plate)
                plate_index += 1
            else:
                print("All predefined plates have been annotated.")
        elif key == ord('b'):  # Annotate baseline
            if current_plate:
                current_annotation_type = "baseline"
                print(f"Annotating baseline for Plate {plate_names[plate_index - 1]}. Click on the baseline.")
            else:
                print("Error: Start a plate first ('n').")
        elif key == ord('s'):  # Annotate solvent line
            if current_plate:
                current_annotation_type = "solvent_line"
                print(f"Annotating solvent line for Plate {plate_names[plate_index - 1]}. Click on the solvent line.")
            else:
                print("Error: Start a plate first ('n').")
        elif key == ord('o'):  # Annotate spots
            if current_plate:
                current_annotation_type = "spots"
                print(f"Annotating spots for Plate {plate_names[plate_index - 1]}. Click on spots.")
            else:
                print("Error: Start a plate first ('n').")

    # Calculate and display ratios
    results = calculate_ratios(annotations)
    if results:
        for i, plate_data in enumerate(results):
            print(f"\nPlate {plate_names[i]}:")
            print(f"  Baseline: {annotations[i]['baseline']}")
            print(f"  Solvent Line: {annotations[i]['solvent_line']}")
            for spot_data in plate_data["spots"]:
                print(f"  {spot_data['spot']}: Ratio: {spot_data['ratio']:.2f}")

    # Clean up
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
