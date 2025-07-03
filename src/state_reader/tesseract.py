import cv2
import numpy as np
import pytesseract

from typing import Tuple, Optional, List

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
