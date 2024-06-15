import cv2
import numpy as np
from attrs import define
import display_data
from img_histogram import histogram, find_threshold

# TODO: Filter top half of the image so 
def filter_box_battle(frame, min_color, max_color):
    blue_limit = int(find_threshold(histogram(frame, 0), 0.75))
    red_limit = int(find_threshold(histogram(frame, 2), 0.3))
    green_limit = int(find_threshold(histogram(frame, 1), 0.3))
    mask = cv2.inRange(frame, (blue_limit, 0, 0), (255, red_limit, green_limit))

    ## preparing the mask to overlay 
    #mask = cv2.inRange(frame, min_color, max_color) 

    # erode mask
    kernel = np.ones((3,3),np.uint8)
    mask_eroded = cv2.erode(mask,kernel,iterations = 1)
    if not np.any(mask_eroded):
        return None, frame

    # Find the indices where the mask is True (1)
    coords = np.argwhere(mask_eroded)

    # Find the bounding box of the mask
    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0)

    # Crop the image using the bounding box coordinates
    cropped_image = frame[y_min:y_max+1, x_min:x_max+1]

    return mask, cropped_image

def filter_text(box, min_text, max_text):
    v = cv2.cvtColor(box, cv2.COLOR_BGR2HSV)[:,:,2]
    #mask = cv2.inRange(box, min_text, max_text)
    v[v < display_data.min_text_v] = 0
    
    
    if np.average(v) < 0.1:
        return None

    return v

def split_box(text):
    #text = cv2.resize(text, (0,0), fx=4, fy=4)
    #text = cv2.erode(text, np.ones((3,3), np.uint8), iterations=1)
    dimensions = text.shape
    result_name_part = text[int(dimensions[0]*display_data.pokemon_name[0]):int(dimensions[0]*display_data.pokemon_name[1]), :]
    result_hp_part = text[int(dimensions[0]*display_data.hp[0][0]):int(dimensions[0]*display_data.hp[0][1]), 
                                int(dimensions[1]*display_data.hp[1][0]):int(dimensions[1]*display_data.hp[1][1])]
    result_status_part = text[int(dimensions[0]*display_data.status[0][0]):int(dimensions[0]*display_data.status[0][1]), 
                                int(dimensions[1]*display_data.status[1][0]):int(dimensions[1]*display_data.status[1][1])]
    return result_name_part, result_status_part, result_hp_part

def read_box(text_box):
    name_part, status_part, hp_part = split_box(text_box)
    # Configure single-line reading only
    psm_config = r"--psm 8 --oem 0" 
    hp_config = psm_config + r" --user-patterns patterns/hp.pattern -c tessedit_char_whitelist=0123456789/"
    name_config = psm_config + r" --user-patterns patterns/name.pattern, -c tessedit_char_whitelist=QWERTYUIOPASDFGHJKLZXCVBNM"
    status_config = psm_config + r" --user-patterns patterns/status.pattern  -c tessedit_char_whitelist=QWERTYUIOPASDFGHJKLZXCVBNM"
    
    # Tesseract image reading
    name = pytesseract.image_to_string(name_part, config=name_config)
    hp_stat = pytesseract.image_to_string(hp_part, config=hp_config)
    status = pytesseract.image_to_string(status_part, config=status_config)
    return name, status, hp_stat

def split_image(img):
    img_top_left = img[:img.shape[0]//2, :img.shape[1]//2]
    img_top_right = img[:img.shape[0]//2, img.shape[1]//2:]
    img_bottom = img[img.shape[0]//2:, :]
    return img_top_left, img_top_right, img_bottom


if __name__ == "__main__":
    img = cv2.imread("data/example_battle.png")
    print("Loaded image")
    img_top_left, img_top_right, img_bottom = split_image(img)
    mask, result = filter_box_battle(img_top_left, display_data.p1_min_blue, display_data.p1_max_blue)
    #mask, result = filter_box_battle(img_top_right, display_data.p2_min_green, display_data.p2_max_green)
    text = filter_text(result, display_data.min_text, display_data.max_text)
    result_name_part, result_status_part, result_hp_part = split_box(text)
    print("Reading box")
    name, hp, status = read_box(text)
    print("Parsed box")
    
    print("Name: ", name)
    print("HP: ", hp)
    print("Status: ", status)
    cv2.imshow("Name", result_name_part)
    cv2.imshow("HP", result_hp_part)
    cv2.imshow("Status", result_status_part)
    cv2.imshow("text box", text)
    cv2.waitKey(0)
    
