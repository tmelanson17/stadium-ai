import cv2
import numpy as np

from typing import Tuple, TypeAlias, List, Optional
# TODO: Move preprocessing functions to a common module
from src.state_reader.tesseract import preprocess_for_ocr, remove_large_contours, read_text_from_roi
from src.state_reader.phrases import get_closest_pokemon_name 
from src.state.pokestate import BattleState

# Portions of screen
POKEMON_NAME = (0, 0.4)
STATUS = ((0.38, 0.65), (0.4, 1.0))
# HP = ((0.1, 0.5), (0.75, 0.95))
HP = ((0.1, 0.5), (0.72, 1.0))
SIMILARITY_THRESHOLD = 0.2
NUMBERS = [
    cv2.imread(f"numbers/processed_{i}.jpg", cv2.IMREAD_GRAYSCALE)
    for i in range(10)
]

# HP_TESSERACT_CONFIG="--oem 1 --psm 13 -l eng --user-patterns patterns/hp.pattern -c tessedit_char_whitelist=0123456789"
NAME_TESSERACT_CONFIG="--oem 1 --psm 13 -l eng -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# TODO : Move this to a more central location, as this is used often.
BBox: TypeAlias = Tuple[Tuple[int, int], Tuple[int, int]]

def detect_numbers(
    roi: np.ndarray) -> List[str]:
    """
    Match numbers in the image to the specified region of interest (ROI).

    Args:
        roi: Region of interest as a subset of the image.

    Returns:
        Numbers detected, combined into a string
    """
    # Detect keypoints and descriptors in the source image
    roi_negative = cv2.bitwise_not(roi)
    shapes_in_image, _= cv2.findContours(roi_negative, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    regions_of_interest = [cv2.boundingRect(cnt) for cnt in shapes_in_image if cv2.contourArea(cnt) > 100]
    regions_of_interest = sorted(regions_of_interest, key=lambda x: x[0])  # Sort by x-coordinate
    detected_numbers = []
    for box in regions_of_interest:
        if box is None or len(box) != 4:
            print(f"Skipping invalid box: {box}")
            continue
        character = roi_negative[box[1]:box[1]+box[3], box[0]:box[0]+box[2]]
        max_similarity = 0
        argmax_similarity = -1
        for i, img in enumerate(NUMBERS):
            character_resized = cv2.resize(character, (img.shape[1], img.shape[0]))
            score = cv2.matchTemplate(character_resized, img, cv2.TM_CCOEFF_NORMED)
            if score.max() > max_similarity:
                argmax_similarity = i
                max_similarity = score.max()
        if max_similarity > SIMILARITY_THRESHOLD:  # Threshold for a good match
            detected_numbers.append(argmax_similarity)

    return map(str, detected_numbers)

def get_hp_section(hp_bbox: BBox) -> BBox:
    """
    Crop the image to the HP component of the hp bbox
    
    Args:
        image: Input image as a numpy array.
        hp_bbox: Bounding box of HP block as ((x1, y1), (x2, y2)).
        
    Returns:
        Cropped image as a numpy array.
    """
    (x1, y1), (x2, y2) = hp_bbox
    x1 += int(HP[0][0] * (x2 - x1))
    x2 -= int((1 - HP[0][1]) * (x2 - x1))
    y1 += int(HP[1][0] * (y2 - y1))
    y2 -= int((1 - HP[1][1]) * (y2 - y1))
    return ((x1, y1), (x2, y2))

i=0
def get_hp(image: np.ndarray, roi: BBox) -> int:
    """
        Retrieves a raw hp value from the image
        by looking at a hard-coded sectoin of the HP ROI box
        (since the size of the HP box is mostly static).
    """
    global i
    ((x1, y1), (x2, y2)) = get_hp_section(roi)
    preprocessed = preprocess_for_ocr(image[y1:y2, x1:x2], resize_scale=4, use_otsu=True, blur_kernel=5, morph_kernel=1)
    denoised = remove_large_contours(preprocessed, min_area=10, min_aspect_ratio=0.2)
    cv2.imwrite(f"debug/hp_section_{i}.png", image[y1:y2, x1:x2])
    cv2.imwrite(f"debug/hp_section_denoised_{i}.png", denoised)
    i+=1
    hp_strings = detect_numbers(denoised)
    hp_string = ''.join(hp_strings)
    # hp_strings = [line.strip() for line in hp_strings if line is not None]
    # hp_string = ''.join(filter(str.isdigit, ' '.join(hp_strings)))
    # Clean any non-numeric characters
    if len(hp_string) == 0:
        return -1
    return int(hp_string)

name_i = 0
def get_pokemon_name(image: np.ndarray, roi: BBox, battle_state: BattleState, opponent: bool = False) -> Optional[str]:
    """
    Extract the Pokemon name from the specified region of interest (ROI).

    Args:
        image: Input image as a numpy array.
        roi: Region of interest as a bounding box ((x1, y1), (x2, y2)).

    Returns:
        Extracted Pokemon name as a string.
    """
    global name_i
    (x1, y1), (x2, y2) = roi
    # Adjust the ROI to focus on the Pokemon name section
    y1 += int(POKEMON_NAME[0] * (y2 - y1))
    y2 -= int((1 - POKEMON_NAME[1]) * (y2 - y1))
    preprocess = preprocess_for_ocr(image[y1:y2, x1:x2], use_otsu=True, blur_kernel=1)
    cv2.imwrite(f"debug/pokemon_name_section_{name_i}.png", image[y1:y2, x1:x2])

    names = read_text_from_roi(
        image, roi=((x1, y1), (x2, y2)),
        tesseract_config=NAME_TESSERACT_CONFIG,
        preprocess=False
    )
    names = [name.strip() for name in names if name is not None and len(name.strip()) > 0]
    if not names:
        return None

    # Get the closest matching Pokemon name from the messages
    closest_name = get_closest_pokemon_name(names, battle_state, opponent)
    return closest_name
