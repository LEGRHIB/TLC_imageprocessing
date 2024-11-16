import cv2

# Global variables to store clicked points
annotations_uv = []
annotations_stain = []
current_plate = None
current_annotation_type = None
plate_names = ["A: 50% DCM in Heptane", 
               "B: 50% EtOAc in Heptane", 
               "C: DCM", 
               "D: 50% EtOAc in DCM", 
               "E: EtOAc", 
               "F: 10% MeOH in DCM"]

# Conversion factors
pixels_to_cm_uv = 0.046  # Adjust based on UV image calibration
pixels_to_cm_stain = 0.048  # Adjust based on Stain image calibration

# Color mapping for annotation types
annotation_colors = {
    "baseline": (0, 0, 255),       # Red for baseline
    "solvent_line": (255, 0, 0),   # Blue for solvent line
    "spots": (0, 255, 0)           # Green for spots
}

# Mouse callback function to capture points
def click_event(event, x, y, flags, param):
    global current_plate, current_annotation_type

    if event == cv2.EVENT_LBUTTONDOWN:  # Left click to select points
        if current_plate is not None and current_annotation_type:
            current_plate[current_annotation_type].append((x, y))
            print(f"{current_annotation_type} point selected: ({x}, {y})")

            # Get the color for the current annotation type
            color = annotation_colors.get(current_annotation_type, (255, 255, 255))  # Default to white

            # Draw a small circle with the specified color
            cv2.circle(param, (x, y), 2, color, -1)
            cv2.imshow("Image", param)

# Calculate ratios for UV and Stain annotations
def calculate_ratios(annotations_uv, annotations_stain):
    results = []

    for i, (plate_uv, plate_stain) in enumerate(zip(annotations_uv, annotations_stain)):
        # Get UV annotations
        baseline_uv = plate_uv.get("baseline")
        solvent_line_uv = plate_uv.get("solvent_line")
        spots_uv = plate_uv.get("spots", [])

        if not baseline_uv or not solvent_line_uv:
            print(f"Error: Plate {i + 1} UV image is missing baseline or solvent line.")
            continue

        plate_results = {"components": [], "solvent_front_distance_cm": 0}

        # Use UV solvent front for all calculations
        baseline_y_uv = baseline_uv[0][1]
        solvent_y_uv = solvent_line_uv[0][1]
        solvent_front_distance_px_uv = abs(solvent_y_uv - baseline_y_uv)
        solvent_front_distance_cm = solvent_front_distance_px_uv * pixels_to_cm_uv
        plate_results["solvent_front_distance_cm"] = round(solvent_front_distance_cm, 1)

        # Combine UV and Stain spots (Stain spots are recalibrated to UV baseline and solvent line)
        all_spots = spots_uv[:]
        if plate_stain:
            baseline_stain = plate_stain.get("baseline")
            solvent_line_stain = plate_stain.get("solvent_line")
            spots_stain = plate_stain.get("spots", [])

            if baseline_stain and solvent_line_stain:
                # Adjust stain spots based on UV baseline and solvent line calibration
                stain_baseline_to_solvent_px = abs(solvent_line_stain[0][1] - baseline_stain[0][1])
                if stain_baseline_to_solvent_px > 0:
                    scaling_factor = solvent_front_distance_px_uv / stain_baseline_to_solvent_px
                else:
                    scaling_factor = 1  # Fallback to 1 if the stain baseline-to-solvent distance is invalid

                for spot in spots_stain:
                    spot_y_adjusted = baseline_y_uv + scaling_factor * (spot[1] - baseline_stain[0][1])
                    all_spots.append((spot[0], spot_y_adjusted))

        # Deduplicate spots based on y-coordinate proximity (0.1 cm tolerance)
        unique_spots = []
        for spot in sorted(all_spots, key=lambda s: s[1]):
            if not any(abs(spot[1] - unique[1]) <= 2 for unique in unique_spots):
                unique_spots.append(spot)

        # Calculate distances, Rf, and CV for unique spots and sort by distance_cm
        calculated_components = []
        for spot in unique_spots:
            spot_y = spot[1]
            spot_to_baseline_px = abs(spot_y - baseline_y_uv)
            spot_distance_cm = spot_to_baseline_px * pixels_to_cm_uv

            rf = spot_to_baseline_px / solvent_front_distance_px_uv
            cv = 1 / rf if rf != 0 else 0

            calculated_components.append({
                "distance_cm": round(spot_distance_cm, 1),
                "rf": round(rf, 2),
                "cv": round(cv, 1)
            })

        # Sort components by distance_cm in ascending order
        calculated_components = sorted(calculated_components, key=lambda x: x["distance_cm"])

        # Assign component numbers and append to plate results
        for idx, component in enumerate(calculated_components):
            component["component"] = f"Component {idx + 1}"
            plate_results["components"].append(component)

        results.append(plate_results)

    return results

def main():
    global current_plate, current_annotation_type, annotations_uv, annotations_stain

    # Load the UV and stain images
    uv_image_path = "./sorted_images/uv/102038UV.jpg"  # Replace with your UV image path
    stain_image_path = "./sorted_images/stain/102038TAIN.jpg"  # Replace with your stain image path

    uv_image = cv2.imread(uv_image_path)
    stain_image = cv2.imread(stain_image_path)

    if uv_image is None or stain_image is None:
        print("Error: Could not load UV or stain images.")
        return

    # Clone the images to redraw without losing the original
    uv_clone = uv_image.copy()
    stain_clone = stain_image.copy()

    # Instructions
    print("Instructions:")
    print("1. Press 'n' to start annotating a predefined plate.")
    print("2. Press 'b' to annotate baseline for the current plate.")
    print("3. Press 's' to annotate solvent line for the current plate.")
    print("4. Press 'o' to annotate spots for the current plate.")
    print("5. Press 't' to switch to the stain image after annotating all UV images.")
    print("6. Press 'q' to finalize and calculate ratios.")

    # Display the UV image and set up the mouse callback
    cv2.imshow("Image", uv_image)
    cv2.setMouseCallback("Image", click_event, param=uv_clone)

    plate_index = 0
    uv_annotation_done = False
    using_stain = False

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') and uv_annotation_done:  # Quit after UV and stain annotations
            print("Finalizing and calculating results...")
            break
        elif key == ord('n'):  # Start a new plate
            if not using_stain and plate_index < len(plate_names):
                print(f"Started annotating Plate {plate_names[plate_index]} (UV).")
                current_plate = {"baseline": [], "solvent_line": [], "spots": []}
                annotations_uv.append(current_plate)
                plate_index += 1
            elif using_stain and plate_index < len(plate_names):
                print(f"Started annotating Plate {plate_names[plate_index]} (Stain).")
                current_plate = {"baseline": [], "solvent_line": [], "spots": []}
                annotations_stain.append(current_plate)
                plate_index += 1
            else:
                if not using_stain:
                    print("All predefined plates have been annotated for UV. Press 't' to switch to the stain image.")
                    uv_annotation_done = True
                else:
                    print("All predefined plates have been annotated for Stain. Press 'q' to finalize and calculate ratios.")
        elif key == ord('b'):  # Annotate baseline
            if current_plate:
                current_annotation_type = "baseline"
                print("Annotating baseline. Click on the baseline.")
            else:
                print("Error: Start a plate first ('n').")
        elif key == ord('s'):  # Annotate solvent line
            if current_plate:
                current_annotation_type = "solvent_line"
                print("Annotating solvent line. Click on the solvent line.")
            else:
                print("Error: Start a plate first ('n').")
        elif key == ord('o'):  # Annotate spots
            if current_plate:
                current_annotation_type = "spots"
                print("Annotating spots. Click on spots.")
            else:
                print("Error: Start a plate first ('n').")
        elif key == ord('t') and uv_annotation_done:  # Switch to stain image
            print("Switched to stain image. Annotate stain images now.")
            plate_index = 0
            current_plate = None
            using_stain = True
            cv2.imshow("Image", stain_image)
            cv2.setMouseCallback("Image", click_event, param=stain_clone)

    # Calculate and display ratios
    try:
        results = calculate_ratios(annotations_uv, annotations_stain)
    except Exception as e:
        print(f"Error during ratio calculation: {e}")
        results = []

    if not results:
        print("No annotations were made. Please ensure all plates are annotated.")
        cv2.destroyAllWindows()
        return

    # Deduplicate results and display
    for plate_data in results:
        unique_spots = []
        for component in plate_data["components"]:
            if not any(abs(component["distance_cm"] - unique["distance_cm"]) <= 0.1 for unique in unique_spots):
                unique_spots.append(component)
        plate_data["components"] = unique_spots

    for i, plate_data in enumerate(results):
        print(f"\nPlate {plate_names[i]}:")
        print(f"  Solvent Front Distance: {plate_data['solvent_front_distance_cm']} cm")
        for component_data in plate_data["components"]:
            print(f"  {component_data['component']}: Distance: {component_data['distance_cm']} cm, Rf: {component_data['rf']}, CV: {component_data['cv']}")

    # Clean up
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
