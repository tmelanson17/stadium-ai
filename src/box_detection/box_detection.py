import cv2
import numpy as np

from typing import List, Tuple, Sequence, Optional

from src.state.pokestate_defs import ImageUpdate, Rectangle, PlayerID, MessageType
from src.utils.box_average_filter import BoxAverageFilter

# Constants for box detection
# Ratios for different boxes
# These ratios are based on the expected width to height ratios of the boxes in the game
HP_BOX_RATIO = 2.3 # Width to height ratio
P1_BOX_RATIO = 1.68
FULL_BOX_RATIO = 1.0 # With pfp and 1P/2P
STATUS_BOX_RATIO = 7.4 # With status bar

# TODO: Determine if P1 or P2 before adjusting HP box location
HP_P_HEIGHT = 0.7 # Height of the HP box relative to the full P1 box
P_P1_LOCATION_V = 0.3 
P_P2_LOCATION_V = 0.0 # Vertical location of the HP box in P1 or P2 box
HP_FULL_HEIGHT = 0.4 # Height of the HP box relative to the full box
FULL_P1_LOCATION_V = 0.2 # Vertical location of the HP box in the full P1 box
FULL_P2_LOCATION_V = 0.40 # Vertical location of the HP box in the full P2 box


HP_LOCATION_IN_BOX = (0.325, 0.825)

def _apply_morphology(input_img: np.ndarray, kernel_size: Tuple[int, int]=(3, 3)) -> np.ndarray:
    """
    Apply morphological operations to the input image to enhance contours.
    
    Parameters:
    - input_img: The input image to apply morphology on.
    - kernel_size: Size of the kernel for morphological operations.
    
    Returns:
    - The processed image after applying morphological operations.
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
    morphed_img = cv2.morphologyEx(input_img, cv2.MORPH_CLOSE, kernel)
    morphed_img = cv2.dilate(morphed_img, kernel, iterations=1)
    return morphed_img

def _filter_unique_contours(contours: List[np.ndarray], min_iou: float=0.3) -> List[np.ndarray]:
    # Filter out contours with similar locations and sizes
    unique_contours = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        duplicate = False
        for unique_cnt in unique_contours:
            ux, uy, uw, uh = cv2.boundingRect(unique_cnt)
            # Get IoU (Intersection over Union) to check if the contours overlap significantly
            intersection_area = max(0, min(x + w, ux + uw) - max(x, ux)) * max(0, min(y + h, uy + uh) - max(y, uy))
            union_area = (w * h) + (uw * uh) - intersection_area
            iou = intersection_area / union_area if union_area > 0 else 0
            if iou > min_iou:  # If IoU is greater than 0.5, consider it a duplicate
                duplicate = True
                break
        if not duplicate:
            unique_contours.append(cnt)
    return unique_contours

def _get_hp_box_location(x, y, w, h, height_ratio, relative_y) -> Rectangle:
    """
    Calculate the HP box location based on the bounding box of the P1 or P2 box.
    
    Parameters:
    - x, y: Top-left corner of the bounding box
    - w, h: Width and height of the bounding box
    - p1: Boolean indicating if it is P1 (True) or P2 (False)
    
    Returns:
    - hp_box_x, hp_box_y: Coordinates of the HP box location
    """
    hp_box_width = w 
    hp_box_height = h * height_ratio
    hp_box_x = x      
    hp_box_y = y + int(relative_y * h)

    return Rectangle(hp_box_x, hp_box_y, hp_box_x + hp_box_width, hp_box_y + int(hp_box_height))

"""
Get the HP box location for a player. Creates an internal state of the location of each player's HP box, as well as the status box.
Uses an AverageFilter to smooth out the location of the boxes over time and determine outliers.
"""
class BoxDetection:

    def __init__(self):
        self.p1_hp_boxes = BoxAverageFilter(window_size=10)  # Filter for P1 HP boxes
        self.p2_hp_boxes = BoxAverageFilter(window_size=10)  # Filter for P2 HP boxes
        self.status_boxes = BoxAverageFilter(window_size=10)  # Filter for status boxes

    def _get_update_box(self, input_img: np.ndarray, box: Optional[Rectangle], p1: bool, is_hp_box: bool) -> Optional[ImageUpdate]:
        if box is not None:
            if is_hp_box:
                # If the box is an HP box, add it to the appropriate player's HP box filter
                if p1:
                    if not self.p1_hp_boxes.is_outlier(box, threshold=0.1):
                        self.p1_hp_boxes.add(box)
                        return ImageUpdate(input_img, self.p1_hp_boxes.get_average(), MessageType.HP, PlayerID.P1)
                    self.p1_hp_boxes.add(box)  # Reset if outlier detected
                else:
                    if not self.p2_hp_boxes.is_outlier(box, threshold=0.1):
                        self.p2_hp_boxes.add(box)
                        return ImageUpdate(input_img, self.p2_hp_boxes.get_average(), MessageType.HP, PlayerID.P2)
                    self.p2_hp_boxes.add(box)  # Reset if outlier detected
            else:
                # If the box is a status box, add it to the status box filter
                if not self.status_boxes.is_outlier(box, threshold=0.1):
                    self.status_boxes.add(box)
                    player_id = PlayerID.P1 if p1 else PlayerID.P2
                    return ImageUpdate(input_img, self.status_boxes.get_average(), MessageType.CONDITION, player_id)
                self.status_boxes.add(box)  # Reset if outlier detected
        return None

    def _detect_contours(self, input_img):
        img_gray = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
        normalized_img = cv2.normalize(img_gray, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        # equalized_img = cv2.equalizeHist(normalized_img)
        blurred = cv2.GaussianBlur(normalized_img, (5,5), 1.0)  # Apply median blur to the image
        # Perform Canny edge detection on the input image
        edges = cv2.Canny(blurred, threshold1=120, threshold2=300)

        morphed_img = _apply_morphology(edges, kernel_size=(3, 3))  # Apply morphology to enhance edges

        # Invert the edges image to get negative edges
        negative_edges = cv2.bitwise_not(morphed_img)
        
        # Find contours in the edges image
        contours, _ = cv2.findContours(negative_edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours based on area
        img_area = input_img.shape[0] * input_img.shape[1]
        contours_filtered = [cnt for cnt in contours if cv2.contourArea(cnt) > 0.01 * img_area and cv2.contourArea(cnt) < 0.5 * img_area]
        
        contours_unique = _filter_unique_contours(contours_filtered, min_iou=0.3)
        return contours_unique

    def update(self, input_img: np.ndarray) -> Sequence[ImageUpdate]:
        contours_unique = self._detect_contours(input_img)
        ratio_shift = 1.0 # Ratio shift to account for different screen sizes or resolutions
        hsv_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2HSV)
        updates = []
        for cnt in contours_unique:
            x, y, w, h = cv2.boundingRect(cnt)
            ratio = w / h
            # Filter any images that intersect with the center of the image
            x_center = input_img.shape[1] // 2
            y_center = input_img.shape[0] // 2
            if (x + w > x_center and x < x_center) and (y + h > y_center and y < y_center):
                continue

            # Determine if P1 or P2 box based on the color of the box
            average_hue = np.median(hsv_img[y:y+h, x:x+w, 0])  # Get average color in BGR 
            # If the box is blue, it is the P1 box
            # P1 will be marked in red colors, P2 in blue colors
            p1 = average_hue > 100 and average_hue < 180


            box = None
            is_hp_box = False
            if ratio > HP_BOX_RATIO * ratio_shift * 0.95 and ratio < HP_BOX_RATIO * ratio_shift * 1.05: # Draw a rectangle around the HP box
                # Draw point for HP box location
                box = _get_hp_box_location(x, y, w, h, 1.0, 0.0)
                is_hp_box = True
            elif ratio > P1_BOX_RATIO * ratio_shift * 0.9 and ratio < P1_BOX_RATIO * ratio_shift * 1.1:
                # Draw a rectangle around the P1 box
                box = _get_hp_box_location(x, y, w, h, HP_P_HEIGHT, P_P1_LOCATION_V if p1 else P_P2_LOCATION_V)
                is_hp_box = True
            elif ratio > FULL_BOX_RATIO * ratio_shift * 0.9 and ratio < FULL_BOX_RATIO * ratio_shift * 1.1:
                # Draw a rectangle around the full box
                box = _get_hp_box_location(x, y, w, h, HP_FULL_HEIGHT, FULL_P1_LOCATION_V if p1 else FULL_P2_LOCATION_V)
                is_hp_box = True
            elif ratio > STATUS_BOX_RATIO * ratio_shift * 0.9 and ratio < STATUS_BOX_RATIO * ratio_shift * 1.1:
                # Draw a rectangle around the status box
                box = Rectangle(x, y, x+w, y+h)


            update = self._get_update_box(input_img, box, p1, is_hp_box)
            if update is not None:
                updates.append(update)

        return updates


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