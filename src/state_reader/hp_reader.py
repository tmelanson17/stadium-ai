import numpy as np

from typing import Tuple, TypeAlias
from src.state_reader.tesseract import read_text_from_roi

# Portions of screen
POKEMON_NAME = (0, 0.4)
STATUS = ((0.38, 0.65), (0.4, 1.0))
HP = ((0.15, 0.5), (0.7, 0.95))

HP_TESSERACT_CONFIG="--oem 1 --psm 12 -l eng --user-patterns patterns/hp.pattern -c tessedit_char_whitelist=0123456789"

# TODO : Move this to a more central location, as this is used often.
BBox: TypeAlias = Tuple[Tuple[int, int], Tuple[int, int]]

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

def get_hp(image: np.ndarray, roi: BBox) -> int:
    """
        Retrieves a raw hp value from the image
        by looking at a hard-coded sectoin of the HP ROI box
        (since the size of the HP box is mostly static).
    """
    hp_section = get_hp_section(roi)
    hp_strings = read_text_from_roi(image, hp_section, tesseract_config=HP_TESSERACT_CONFIG)
    hp_strings = [line.strip() for line in hp_strings if line is not None]
    # Clean any non-numeric characters
    hp_string = ''.join(filter(str.isdigit, ' '.join(hp_strings)))
    return int(hp_string)
