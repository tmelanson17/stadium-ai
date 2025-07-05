import cv2
import numpy as np

from typing import Optional, Sequence

from src.state.pokestate_defs import StadiumMode, ImageUpdate, PlayerID

def draw_mode(img: np.ndarray, mode: Optional[StadiumMode]) -> np.ndarray:
    """Draws the current stadium mode on the image.
    
    Args:
        img (np.ndarray): The image to draw on.
        mode (StadiumMode): The current stadium mode.
    
    Returns:
        np.ndarray: The image with the stadium mode drawn on it.
    """
    color_choose = (0, 255, 0)  # Green for Choose Move
    color_execute = (0, 0, 255)  # Red for Execute
    if mode == StadiumMode.CHOOSE_MOVE:
        cv2.putText(img, str(mode), (200, 30), cv2.FONT_HERSHEY_SIMPLEX, 2, color_choose, 2)
    elif mode == StadiumMode.EXECUTE:
        cv2.putText(img, str(mode), (200, 30), cv2.FONT_HERSHEY_SIMPLEX, 2, color_execute, 2)
    return img

def draw_updates(input_img: np.ndarray, updates: Sequence[ImageUpdate]) -> np.ndarray:
    """
    Draws the updates on the input image.
    
    Parameters:
    - input_img: The input image to draw on.
    - updates: A sequence of ImageUpdate objects containing the rectangles to draw.
    
    Returns:
    - The input image with the rectangles drawn on it.
    """
    for update in updates:
        p1, p2 = update.roi.to_coord()
        cv2.rectangle(input_img, p1, p2, (0, 255, 0), 2)
        cv2.putText(input_img, update.message_type.name, (update.roi.x1, update.roi.y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        # Add player ID text
        player_text = f"Player: {update.player_id.name}"
        cv2.putText(input_img, player_text, (update.roi.x1, update.roi.y1 - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    return input_img