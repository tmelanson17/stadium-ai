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
import pytesseract
from typing import List, Tuple, Optional, Union

from src.state_reader.phrases import Messages, parse_update_message
from src.state_reader.state_updater import enact_changes
from src.state.pokestate import BattleState


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

def read_text_from_roi(
    image: np.ndarray,
    roi: Tuple[Tuple[int, int], Tuple[int, int]],
    tesseract_config: str = "--oem 1 --psm 6 -l eng",
    preprocess: bool = True
) -> List[Optional[str]]:
    """
    Read text from a specific region of interest (ROI) in an image using Tesseract,
    then find the closest match from a list of phrases.
    
    Args:
        image: Input image as numpy array (BGR format from cv2)
        roi: Region of interest as ((x1, y1), (x2, y2)) where (x1,y1) is top-left 
             and (x2,y2) is bottom-right
        phrases: List of phrases to match against
        threshold: Maximum Levenshtein distance allowed for a match
        tesseract_config: Tesseract configuration string
        preprocess: Whether to apply preprocessing to improve OCR accuracy
        
    Returns:
        The closest matching phrase if distance <= threshold, None otherwise
    """
    
    # Extract ROI from image
    (x1, y1), (x2, y2) = roi
    roi_image = image[y1:y2, x1:x2]
    
    if roi_image.size == 0:
        print("Warning: ROI is empty or invalid")
        return []
    
    # Preprocess the ROI image for better OCR results
    if preprocess:
        roi_image = preprocess_for_ocr(roi_image)
    
    # Read text using Tesseract
    try:
        raw_text = pytesseract.image_to_string(roi_image, config=tesseract_config)
        # Clean up the text
        lines = raw_text.strip().splitlines()
        matches = []
        for text in lines:
            print(f"PyTesseract result: {text}")
        
            if not text:
                continue
           
            # Find closest match
            matches.append(text) 

        return matches
        
    except Exception as e:
        print(f"Error reading text with Tesseract: {e}")
        return []


def preprocess_for_ocr(image: np.ndarray) -> np.ndarray:
    """
    Preprocess image to improve OCR accuracy.
    
    Args:
        image: Input image
        
    Returns:
        Preprocessed image
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # # Apply Gaussian blur to reduce noise
    # blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    # Skip blurring for now, as it may not be necessary
    blurred = gray
    
    # Apply threshold to get binary image
    binary = cv2.threshold(
        blurred, 
        0, # Adjust threshold value as needed 
        255, 
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]
    # Using adaptive threshold for better results with varying lighting
    # binary = cv2.adaptiveThreshold(
    #     blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, 5. 
    # )
    
    
    # Scale up the image for better OCR (Tesseract works better on larger text)
    scale_factor = 3
    height, width = binary.shape
    resized = cv2.resize(
        binary, 
        (width * scale_factor, height * scale_factor), 
        interpolation=cv2.INTER_NEAREST
    )

    # Apply morphological operations to clean up
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(resized, cv2.MORPH_CLOSE, kernel)
    # cleaned = resized
    
    return cleaned

