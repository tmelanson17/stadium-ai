import cv2
import numpy as np
from enum import Enum

class Color(Enum):
    P1 = 0
    P2 = 1
    CPU = 2

# HSV values===
# Blue values
p1_min_blue = (101, 109, 49)
p1_max_blue = (137, 255, 209)
# Green values
p2_min_green = (50, 60, 6)
p2_max_green = (75, 255, 107)
# Yellow values
cpu_min_yellow = (14, 20, 23)
cpu_max_yellow = (83, 207, 208)
#============

# Text Values
min_text_v = 195
min_text = (158, 158, 158)
max_text = (255, 255, 255)

# Portions of screen
pokemon_name = (0, 0.4)
status = ((0.38, 0.65), (0.4, 1.0))
hp = ((0.75, 1.0), (0.15, 0.98))

# Hard-coded regions
p1_bbox = ((65, 48),(140,208))
p2_bbox = ((334,514),(410,673))
quote_bbox = ((361, 120),(440,615))
p1_hp_v_range = (122,141)
p1_hp_h_range = ((73,92),(90,111),(110,129))
p2_hp_v_range = (391,409)
p2_hp_h_range = ((538,555),(555,575),(574,594))

# 0 if P1 , 1 if P2
def message_box_color(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    blue = np.sum(cv2.inRange(hsv, p1_min_blue, p1_max_blue))
    green = np.sum(cv2.inRange(hsv, p2_min_green, p2_max_green))
    yellow = np.sum(cv2.inRange(hsv, cpu_min_yellow, cpu_max_yellow))
    if blue > green and blue > yellow:
        return Color.P1
    elif green > yellow and green > blue:
        return Color.P2
    elif yellow > green and yellow > blue:
        return Color.CPU
    else:
        return Color.P1

def either_in_range(img):
    p1_box = cv2.inRange(img, p1_min_blue, p1_max_blue)
    p2_box = cv2.inRange(img, p2_min_green, p2_max_green)
    intersection = cv2.bitwise_or(p1_box, p2_box)
    return intersection

def get_portion_bboxes(text_box):
    dim = text_box.shape
    return (
        ((int(dim[0]*pokemon_name[0]), 0),(int(dim[0]*pokemon_name[1]), dim[1])),
         ((int(dim[0]*status[0][0]), int(dim[1]*status[1][0])), (int(dim[0]*status[0][1]), int(dim[1]*status[1][1]))),
         ((int(dim[0]*hp[0][0]), int(dim[1]*hp[1][0])), (int(dim[0]*hp[0][1]), int(dim[1]*hp[1][1]))),
         )


def crop_bbox(img, bbox):
    return img[bbox[0][0]:bbox[1][0], 
               bbox[0][1]:bbox[1][1]]

def set_bbox(img, bbox, values):
    if len(img.shape) == 3 and type(values) != int and len(values.shape) < 3:
        values = cv2.cvtColor(values, cv2.COLOR_GRAY2BGR)
    if img.shape == values.shape:
        img[bbox[0][0]:bbox[1][0],
            bbox[0][1]:bbox[1][1]] = values[bbox[0][0]:bbox[1][0], bbox[0][1]:bbox[1][1]]
    else:
        img[bbox[0][0]:bbox[1][0],
            bbox[0][1]:bbox[1][1]] = values

def get_p1_hp_range(img):
    hp_images = list()
    for i in range(3):
        hp_images.append(crop_bbox(img, ((p1_hp_v_range[0], p1_hp_h_range[i][0]),
                                         (p1_hp_v_range[1], p1_hp_h_range[i][1]))))
    return hp_images

def get_p2_hp_range(img):
    hp_images = list()
    for i in range(3):
        hp_images.append(crop_bbox(img, ((p2_hp_v_range[0], p2_hp_h_range[i][0]),
                                         (p2_hp_v_range[1], p2_hp_h_range[i][1]))))
    return hp_images



def sobel_filter(frame):
    # Sobel filtering
    scale = 1
    delta = 0
    ddepth = cv2.CV_16S
    frame = cv2.GaussianBlur(frame, (3, 3), 0)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Gradient-Y
    # grad_y = cv2.Scharr(gray,ddepth,0,1)
    grad_x = cv2.Sobel(gray, ddepth, 1, 0, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)
    grad_y = cv2.Sobel(gray, ddepth, 0, 1, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)


    abs_grad_x = cv2.convertScaleAbs(grad_x)
    abs_grad_y = cv2.convertScaleAbs(grad_y)


    grad = np.maximum(abs_grad_x, abs_grad_y)
    grad[grad < 255] = 0
    return grad



def check_point_equal(x1 : float, y1 : float, x2 : float, y2: float, thresh : float):
   return (x1-x2)**2 + (y1-y2)**2 < thresh**2

def check_line_equal(line1 : tuple[float], line2 : tuple[float], thresh : float):
    x1,y1,x2,y2 = line1
    xp1,yp1,xp2,yp2 = line2
    return (
            check_point_equal(x1,y1,xp1,yp1,thresh) and check_point_equal(x2,y2,xp2,yp2,thresh)
            ) or (
            check_point_equal(x1,y1,xp2,yp2,thresh) and check_point_equal(x2,y2,xp1,yp1,thresh)
            )

class BoxFitter:
    def __init__(self, thresh=10):
        self.lines = (
                (quote_bbox[0][1], quote_bbox[0][0], quote_bbox[1][1], quote_bbox[0][0]),
                (quote_bbox[0][1], quote_bbox[1][0], quote_bbox[1][1], quote_bbox[1][0]),
                )
        self.thresh = thresh
        self.n_points=2


    def check_lines(self, img):
        edges = sobel_filter(img)
        hough_lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=40, maxLineGap=8)
        if hough_lines is None or len(hough_lines) < self.n_points:
            return False
        #for l in hough_lines:
        #    cv2.line(img, (l[0][0], l[0][1]), (l[0][2], l[0][3]), (0,0,255), 3, cv2.LINE_AA)
        match_all_lines = True
        for line in self.lines:
            matching_line = False
            for l in hough_lines:
                if check_line_equal(line, l[0], self.thresh):
                    matching_line = True
                    break

            if not matching_line:
                match_all_lines = False
                break
        return match_all_lines

