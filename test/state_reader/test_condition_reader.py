import cv2
import numpy as np
import os

from src.state_reader.condition_reader import read_text_from_roi, preprocess_for_ocr, update_state

from test.state_reader.test_utils import create_example_battle_state, create_move_state

# Example usage and test function
def test_condition_reader():
    """
    Test function demonstrating usage.
    """
    battle_state = create_example_battle_state(active_p1_name="BULBY")
    p1_mon = battle_state.player_team.pk_list[battle_state.player_active_mon]
    p1_mon.move1 = create_move_state("Vine Whip")
    
    # Load test image (you would replace this with your actual image)
    for img_name in os.listdir(os.path.join('test', 'data')):
        if not img_name.endswith('.png'):
            continue
        full_path = os.path.join('test', 'data', img_name)
        print(f"Testing with image: {full_path}")
        image = cv2.imread(full_path)
        assert image is not None, "Image not found. Please check the path."
        
        # Example ROI coordinates (top-left and bottom-right corners)
        status_roi = ((76, 230), (406, 296))    # Status condition area
        (x1, y1), (x2, y2) = status_roi

        tesseract_input = preprocess_for_ocr(image[y1:y2, x1:x2])
        cv2.imwrite('ROI.png', tesseract_input)
        
        # Test ROI
        raw_output = read_text_from_roi(image, status_roi)
        print(f"Raw message detected: {raw_output}")

        update_state(raw_output, battle_state)
        print(f"Updated Battle State:")
        print(f"Player 1 confused: {battle_state.player_team.pk_list[battle_state.player_active_mon].confused}")


if __name__ == "__main__":
    test_condition_reader()