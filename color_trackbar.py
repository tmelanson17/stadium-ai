import cv2 as cv
import numpy as np

#cap = cv.imread("data/box_2.jpg")
cap = cv.VideoCapture(0) #"data/freebattle_small.mkv")
if not cap.isOpened():
 print("Cannot open camera")
 exit()

window_capture_name = 'Video Capture'
window_detection_name = 'Object Detection'

ret, frame = cap.read()

max_B = 180
max_G = 255
max_R = 255

low_B_name = "H min"
low_B = 0
high_B_name = "H max"
high_B = max_B
low_G_name = "S min"
low_G = 0
high_G_name = "S max"
high_G = max_G
low_R_name = "V min"
low_R = 0
high_R_name = "V max"
high_R = max_R
 
def on_min_B_trackbar(val):
 global low_B
 global high_B
 low_B = val
 low_B = min(high_B - 1, low_B)
 cv.setTrackbarPos(low_B_name, window_detection_name, low_B)
 
def on_min_G_trackbar(val):
 global low_G
 global high_G
 low_G = val
 low_G = min(high_G - 1, low_G)
 cv.setTrackbarPos(low_G_name, window_detection_name, low_G)
 
def on_min_R_trackbar(val):
 global low_R
 global high_R
 low_R = val
 low_R = min(high_R - 1, low_R)
 cv.setTrackbarPos(low_R_name, window_detection_name, low_R)
 
def on_max_B_trackbar(val):
 global low_B
 global high_B
 high_B = val
 high_B = max(low_B + 1, high_B)
 cv.setTrackbarPos(high_B_name, window_detection_name, high_B)
 
def on_max_G_trackbar(val):
 global low_G
 global high_G
 high_G = val
 high_G = max(low_G + 1, high_G)
 cv.setTrackbarPos(high_G_name, window_detection_name, high_G)
 
def on_max_R_trackbar(val):
 global low_R
 global high_R
 high_R = val
 high_R = max(low_R + 1, high_R)
 cv.setTrackbarPos(high_R_name, window_detection_name, high_R)
 
 
cv.namedWindow(window_capture_name)
cv.namedWindow(window_detection_name)
 
 
 
cv.createTrackbar(low_B_name, window_detection_name , low_B, max_B, on_min_B_trackbar)
cv.createTrackbar(low_G_name, window_detection_name , low_G, max_G, on_min_G_trackbar)
cv.createTrackbar(low_R_name, window_detection_name , low_R, max_R, on_min_R_trackbar)
cv.createTrackbar(high_B_name, window_detection_name , high_B, max_B, on_max_B_trackbar)
cv.createTrackbar(high_G_name, window_detection_name , high_G, max_G, on_max_G_trackbar)
cv.createTrackbar(high_R_name, window_detection_name , high_R, max_R, on_max_R_trackbar)
 
 
while True:
 
 ret, frame = cap.read()
 if frame is None:
     break
 
 
 hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
 detect = cv.inRange(hsv, (low_B, low_G, low_R), (high_B, high_G, high_R))

 
 
 cv.imshow(window_capture_name, frame)
 cv.imshow(window_detection_name, detect)
 
 
 key = cv.waitKey(30)
 if key == ord('q') or key == 27:
     break
