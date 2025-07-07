"""
Battle message parsing and state updating system.

This module provides functions to:
1. Parse battle messages from text using OCR
2. Convert recognized messages into state changes
3. Apply those changes to the battle state

Key Functions:
- parse_update_message: Parse a string message into state changes
- enact_changes: Apply parsed changes to a BattleState
- process_battle_messages: Complete pipeline from image to state updates

Example Usage:
    # Parse a single message
    changes = parse_update_message("It became confused!", battle_state, opponent=True)
    enact_changes(battle_state, changes, opponent=True)
    
    # Process messages from image
    messages = process_battle_messages(image, roi, battle_state, opponent=False)
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Union

from src.state_reader.phrases import parse_update_message
from src.state_reader.tesseract import read_text_from_roi
from src.state_reader.state_updater import enact_changes
from src.state.pokestate import BattleState

CONDITION_TESSERACT_CONFIG = "--oem 1 --psm 6 -l eng"

def update_state(
   raw_text: List[Optional[str]],
   battle_state: BattleState,
   opponent: bool = False
) -> None:
    """
    Update the battle state based on recognized text from an image.
    
    Args:
        raw_text: List of recognized text lines from the image
        battle_state: The current battle state to update
        opponent: Whether the opponent executed the move (True) or player (False)
        
    Returns:
        None
    """
    for text in raw_text:
        if text is None:
            continue
        print(f"Processing text: {text}")
        changes = parse_update_message(text, battle_state, opponent=opponent)
        if changes:
            enact_changes(battle_state, changes, opponent=opponent)


def read_status(
    image: np.ndarray,
    roi: Tuple[Tuple[int, int], Tuple[int, int]],
): 
    """
    Wraps the tesseract ROI reader with the status reading config
    """
    return read_text_from_roi(
        image,
        roi,
        tesseract_config=CONDITION_TESSERACT_CONFIG,
        preprocess=True
    )