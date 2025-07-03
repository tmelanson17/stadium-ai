import cv2
import numpy as np
import os

from typing import Tuple, Optional, List

from src.state_reader.tesseract import read_text_from_roi, preprocess_for_ocr
from src.state_reader.condition_reader import CONDITION_TESSERACT_CONFIG, update_state
from src.state_reader.hp_reader import HP_TESSERACT_CONFIG, get_hp_section, get_hp

from test.state_reader.test_utils import create_example_battle_state, create_move_state

# Example usage and test function
def test_condition_reader():
    """
    Test function demonstrating usage.
    """
    battle_state = create_example_battle_state(active_p1_name="BULBY")
    p1_mon = battle_state.player_team.pk_list[battle_state.player_active_mon]
    p1_mon.move1 = create_move_state("Vine Whip")

    def test_image(name: str, roi: Tuple[Tuple[int, int], Tuple[int, int]], img: np.ndarray, config: str):
        (x1, y1), (x2, y2) = roi
        tesseract_input = preprocess_for_ocr(img[y1:y2, x1:x2])
        cv2.imwrite(f"{name}.png", tesseract_input)
        raw_output = read_text_from_roi(img, roi, tesseract_config=config, preprocess=True)
        print(f"Raw {name} message detected: {raw_output}")
        return raw_output
        
    
    # Load test image (you would replace this with your actual image)
    i=0
    for img_name in os.listdir(os.path.join('test', 'data')):
        i+=1 
        if i > 1:
            break
        if not img_name.endswith('.png'):
            continue
        full_path = os.path.join('test', 'data', img_name)
        print(f"Testing with image: {full_path}")
        image = cv2.imread(full_path)
        assert image is not None, "Image not found. Please check the path."
        
        # Example ROI coordinates (top-left and bottom-right corners)
        status_roi = ((76, 230), (406, 296))    # Status condition area
        status_output = test_image("status_condition", status_roi, image, CONDITION_TESSERACT_CONFIG)
        # hp_box_roi = ((30, 20), (138, 78))
        hp_box_roi = ((340, 20), (450, 78))
        ((x1, y1), (x2, y2)) = hp_box_roi
        cv2.imwrite("hp_box.png", image[y1:y2, x1:x2])
        hp_roi = get_hp_section(hp_box_roi)
        _ = test_image("hp", hp_roi, image, HP_TESSERACT_CONFIG)
        print(f"HP detected: {get_hp(image, hp_box_roi)}")

        # Test status update
        update_state(status_output, battle_state)
        print(f"Updated Battle State:")
        print(f"Player 1 confused: {battle_state.player_team.pk_list[battle_state.player_active_mon].confused}")


if __name__ == "__main__":
    test_condition_reader()