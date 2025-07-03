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


def levenshtein_distance(s: str, t: str) -> int:
    """
    Calculate the Levenshtein distance between two strings.
    
    Args:
        s: First string
        t: Second string
        
    Returns:
        The Levenshtein distance between the strings
    """
    m = len(s)
    n = len(t)
    # Create a matrix to store distances
    d = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize first row and column
    for i in range(1, m + 1):
        d[i][0] = i
    for j in range(1, n + 1):
        d[0][j] = j
    
    # Fill the matrix
    for j in range(1, n + 1):
        for i in range(1, m + 1):
            if s[i-1] == t[j-1]:
                substitution_cost = 0
            else:
                substitution_cost = 1
                
            d[i][j] = min(
                d[i-1][j] + 1,                      # deletion
                d[i][j-1] + 1,                      # insertion
                d[i-1][j-1] + substitution_cost     # substitution
            )
    
    return d[m][n]


def read_text_from_roi(
    image: np.ndarray,
    roi: Tuple[Tuple[int, int], Tuple[int, int]],
    threshold: int = 5,
    tesseract_config: str = "--oem 1 --psm 6 -l eng",
    preprocess: bool = True
) -> List[Optional[Messages]]:
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
            matches.append(find_closest_phrase(text, threshold)) 

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


def find_closest_phrase(
    text: str, 
    threshold: int = 5
) -> Optional[Messages]:
    """
    Find the closest matching phrase using Levenshtein distance.
    
    Args:
        text: The text to match against
        phrases: List of candidate phrases
        threshold: Maximum distance allowed for a match
        
    Returns:
        The closest matching phrase if distance <= threshold, None otherwise
    """
    if not text:
        return None
    
    # Normalize text for comparison (uppercase, strip whitespace)
    normalized_text = text.upper().strip()
    
    min_distance = threshold + 1
    best_match = None
    
    for phrase in Messages:
        # Normalize phrase for comparison
        normalized_phrase = phrase.value.upper().strip()
        
        # Calculate Levenshtein distance
        distance = levenshtein_distance(normalized_text, normalized_phrase)
        
        if distance < min_distance:
            min_distance = distance
            best_match = phrase
    
    # Return match only if within threshold
    return best_match if min_distance <= threshold else None

