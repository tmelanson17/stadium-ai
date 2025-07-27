import cv2
import numpy as np
import pytesseract
import sys

# Ensure pytesseract is configured correctly for Windows
if sys.platform.startswith('win'):
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

from typing import Tuple, Optional, List

i=0

def read_text_from_roi(
    image: np.ndarray,
    roi: Tuple[Tuple[int, int], Tuple[int, int]],
    tesseract_config: str = "--oem 1 --psm 6 -l eng",
    preprocess: bool = True,
    use_otsu: bool = False,
    remove_noise: bool = False,
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
    global i
    cv2.imwrite(f"debug/gray_image_{i}.png", roi_image)
    
    if roi_image.size == 0:
        print("Warning: ROI is empty or invalid")
        return []
    
    # Preprocess the ROI image for better OCR results
    if preprocess:
        roi_image = preprocess_for_ocr(roi_image, use_otsu=use_otsu)

    if remove_noise:
        # Remove large contours from the image to clean it up
        roi_image = remove_large_contours(roi_image)

    cv2.imwrite(f"debug/processed_image_{i}.png", roi_image)
    i += 1

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


def preprocess_for_ocr(image: np.ndarray, use_otsu: bool = False, resize_scale=2, blur_kernel: int = 3, morph_kernel: int = 3) -> np.ndarray:
    """
    Preprocess image to improve OCR accuracy.
    
    Args:
        image: Input image
        resize_scale: Scale factor for resizing the image
        blur_kernel: Kernel size for Gaussian blur
        morph_kernel: Kernel size for morphological operations

    Returns:
        Preprocessed image
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Normalize the image to account for lighting variations + ensure 0-255 range
    normalized = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
    
    
    # Scale up the image for better OCR (Tesseract works better on larger text)
    height, width = normalized.shape
    resized = cv2.resize(
        normalized,
        (width * resize_scale, height * resize_scale),
    )
    
    # Apply Gaussian blur to reduce noise
    if blur_kernel > 1:
        blurred = cv2.GaussianBlur(resized, (blur_kernel, blur_kernel), 0)
    else:
        blurred = resized
    # Skip blurring for now, as it may not be necessary
    # blurred = resized
    
    # Apply threshold to get binary image
    # TODO: Option for binary thresholding for the white text on black background
    if use_otsu:
        # Use Otsu's method for adaptive thresholding
        _, binary = cv2.threshold(
            blurred, 
            0, 
            255, 
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )
    else:
        # Use fixed thresholding
        _, binary = cv2.threshold(
            blurred, 
            150,
            255, 
            cv2.THRESH_BINARY_INV 
        )
    # Pad the image with a border to avoid issues with Tesseract
    binary = cv2.copyMakeBorder(
        binary, 10, 10, 10, 10, 
        cv2.BORDER_CONSTANT, 
        value=(255,)
    )
    # Using adaptive threshold for better results with varying lighting
    # binary = cv2.adaptiveThreshold(
    #     blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, 5. 
    # )

    # Apply morphological operations to clean up
    if morph_kernel > 1:
        kernel = np.ones((morph_kernel, morph_kernel), np.uint8)
        # cleaned = cv2.dilate(binary, kernel, iterations=1)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    else:
        cleaned = binary
    
    return cleaned


def remove_large_contours(gray: np.ndarray, min_area: int = 500, max_area: int = 50000, min_aspect_ratio: float = 0.5) -> np.ndarray:
    """
    Remove large contours from the image.
    
    Args:
        image: Input image
        min_area: Minimum area of contours to keep
        max_area: Maximum area of contours to keep
        
    Returns:
        Image with large contours removed
    """
    if len(gray.shape) == 3:
        res = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    else:
        res = gray.copy()

    negative_gray = cv2.bitwise_not(res)

    contours, _ = cv2.findContours(negative_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)
        aspect_ratio = cv2.boundingRect(contour)[2] / cv2.boundingRect(contour)[3]
        if area < min_area or area > max_area or aspect_ratio < min_aspect_ratio or aspect_ratio > 1 / min_aspect_ratio:
            cv2.drawContours(res, [contour], -1, (255,), thickness=cv2.FILLED)
    
    return res