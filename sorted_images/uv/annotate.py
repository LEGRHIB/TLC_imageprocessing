import cv2
import numpy as np

# Global variables to store clicked points
annotations = []
current_plate = None
current_annotation_type = None


# Mouse callback function to capture points
def click_event(event, x, y, flags, param):
    global current_plate, current_annotation_type, annotations

    if event == cv2.EVENT_LBUTTONDOWN:  # Left click to select points
        if current_plate is not None and current_annotation_type:
            current_plate[current_annotation_type].append((x, y))
            print(f"{current_annotation_type} point selected for Plate {len(annotations)}: ({x}, {y})")
            cv2.circle(param, (x, y), 5, (0, 255, 0), -1)  # Draw circle
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

        plate_results = {"plate": plate.get("plate_boundary"), "spots": []}

        # Calculate distances and ratios for each spot
        for spot in spots:
            spot_to_baseline = np.linalg.norm(np.array(spot) - np.array(baseline[0]))
            solvent_to_baseline = np.linalg.norm(np.array(solvent_line[0]) - np.array(baseline[0]))

            if solvent_to_baseline == 0:
                print(f"Error: Solvent to baseline distance is zero for Plate {i + 1}.")
                continue

            ratio = spot_to_baseline / solvent_to_baseline
            plate_results["spots"].append({"spot": spot, "ratio": ratio})

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
    print("1. Press 'n' to start a new plate.")
    print("2. Press 'b' to annotate baseline for the current plate.")
    print("3. Press 's' to annotate solvent line for the current plate.")
    print("4. Press 'o' to annotate spots for the current plate.")
    print("5. Press 'q' to finish and calculate ratios.")

    # Display the image and set up the mouse callback
    cv2.imshow("Image", image)
    cv2.setMouseCallback("Image", click_event, param=clone)

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Quit
            break
        elif key == ord('n'):  # Start a new plate
            current_plate = {"plate_boundary": [], "baseline": [], "solvent_line": [], "spots": []}
            annotations.append(current_plate)
            print(f"Started annotating Plate {len(annotations)}.")
        elif key == ord('b'):  # Annotate baseline
            if current_plate:
                current_annotation_type = "baseline"
                print(f"Annotating baseline for Plate {len(annotations)}. Click on the baseline.")
            else:
                print("Error: Start a plate first ('n').")
        elif key == ord('s'):  # Annotate solvent line
            if current_plate:
                current_annotation_type = "solvent_line"
                print(f"Annotating solvent line for Plate {len(annotations)}. Click on the solvent line.")
            else:
                print("Error: Start a plate first ('n').")
        elif key == ord('o'):  # Annotate spots
            if current_plate:
                current_annotation_type = "spots"
                print(f"Annotating spots for Plate {len(annotations)}. Click on spots.")
            else:
                print("Error: Start a plate first ('n').")

    # Calculate and display ratios
    results = calculate_ratios(annotations)
    if results:
        for i, plate_data in enumerate(results):
            print(f"\nPlate {i + 1}:")
            print(f"  Plate Boundary: {annotations[i]['plate_boundary']}")
            print(f"  Baseline: {annotations[i]['baseline']}")
            print(f"  Solvent Line: {annotations[i]['solvent_line']}")
            for spot_data in plate_data["spots"]:
                print(f"  Spot: {spot_data['spot']}, Ratio: {spot_data['ratio']:.2f}")

    # Clean up
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
