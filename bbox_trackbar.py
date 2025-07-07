import cv2 as cv
import numpy as np

#cap = cv.imread("data/box_2.jpg")
cap = cv.VideoCapture(0) #"data/freebattle_small.mkv")
cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv.CAP_PROP_FPS, 30)
if not cap.isOpened():
 print("Cannot open camera")
 exit()

window_capture_name = 'Video Capture'
window_detection_name = 'Object Detection'

ret, frame = cap.read()

max_width = frame.shape[1]
max_height = frame.shape[0]

bbox_left_name = "Left"
bbox_left = 0
bbox_right_name = "Right"
bbox_right = max_width
bbox_top_name = "Top"
bbox_top = 0
bbox_bottom_name = "Bottom"
bbox_bottom = max_height
 

def on_left_trackbar(val):
 global bbox_left
 global bbox_right
 bbox_left = val
 bbox_left = min(bbox_right - 1, bbox_left)
 cv.setTrackbarPos(bbox_left_name, window_detection_name, bbox_left)

def on_right_trackbar(val):
 global bbox_left
 global bbox_right
 bbox_right = val
 bbox_right = max(bbox_left + 1, bbox_right)
 cv.setTrackbarPos(bbox_right_name, window_detection_name, bbox_right)

def on_top_trackbar(val):
 global bbox_top
 global bbox_bottom
 bbox_top = val
 bbox_top = min(bbox_bottom - 1, bbox_top)
 cv.setTrackbarPos(bbox_top_name, window_detection_name, bbox_top)

def on_bottom_trackbar(val):
 global bbox_top
 global bbox_bottom
 bbox_bottom = val
 bbox_bottom = max(bbox_top + 1, bbox_bottom)
 cv.setTrackbarPos(bbox_bottom_name, window_detection_name, bbox_bottom)
 
 
 
cv.namedWindow(window_capture_name)
cv.namedWindow(window_detection_name)
 
 
 
cv.createTrackbar(bbox_left_name, window_detection_name , bbox_left, max_width, on_left_trackbar)
cv.createTrackbar(bbox_right_name, window_detection_name , bbox_right, max_width, on_right_trackbar)
cv.createTrackbar(bbox_top_name, window_detection_name , bbox_top, max_height, on_top_trackbar)
cv.createTrackbar(bbox_bottom_name, window_detection_name , bbox_bottom, max_height, on_bottom_trackbar)
 
 
while True:
 
 ret, frame_bbox = cap.read()
 #frame_bbox = np.copy(cap)
 if frame_bbox is None:
     break
 
 
 frame_bbox[bbox_top:bbox_bottom, bbox_left:bbox_right, 2] = 255
 
 
 cv.imshow(window_capture_name, frame_bbox)
 
 
 key = cv.waitKey(30)
 if key == ord('q') or key == 27:
     break
