import numpy as np
import cv2

import display_data
from game_state_machine import GameState, GameStateMachine
from cv.retrieve_player_state import split_image, filter_box_battle, filter_text, read_box
from cv.retrieve_text_box import TesseractQueue
from cv.hp_reader import HPReader
from state import game_state

def find_hp(img, p1):
    if p1:
        hp_boxes = display_data.get_p1_hp_range(img)
    else:
        hp_boxes = display_data.get_p2_hp_range(img)

    hp=0
    for i,hp_box in enumerate(hp_boxes):
        text = filter_text(hp_box, display_data.min_text, display_data.max_text)

        if text is None:
            continue
        cv2.imwrite(f"box_number_{i}.png", text)
        hp_digit = reader.single_infer(text)
        hp = hp*10 + hp_digit

    print(hp)
    print("===")
    return hp
 
if __name__ == "__main__":
 cap = cv2.VideoCapture(0) # "data/freebattle_small.mkv")
 cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
 cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
 cap.set(cv2.CAP_PROP_FPS, 30)
 if not cap.isOpened():
  print("Cannot open camera")
  exit()
 machine = GameStateMachine()
 queue = TesseractQueue()
 box_fitter = display_data.BoxFitter()
 box_active = False
 reader = HPReader("cv/hp_cnn.pt")
 DECISION_DELAY=30
 decision_frame=0
 state = game_state.create_game_state()
 while True:
  # Capture frame-by-frame
  ret, frame = cap.read()
  
  # if frame is read correctly ret is True
  if not ret: 
   print("Can't receive frame (stream end?). Exiting ...")
   break
 
  img = frame
 
  #img_top_left, img_top_right, img_bottom = split_image(frame)
  #mask, result = filter_box_battle(img_top_left, display_data.p1_min_blue, display_data.p1_max_blue)
  ##mask, result = filter_box_battle(img_top_right, display_data.p2_min_green, display_data.p2_max_green)
  #if mask is not None:
  # text = filter_text(result, display_data.min_text, display_data.max_text)
  #else:
  # text = frame
 
  ## Display the resulting frame
  #cv2.imshow('text', text)
  #if mask is not None:
  #    frame[:frame.shape[0]//2, :frame.shape[1]//2, 0] = mask
  #    frame[:frame.shape[0]//2, :frame.shape[1]//2, 1] = mask
  #    frame[:frame.shape[0]//2, :frame.shape[1]//2, 2] = mask
  #    cv2.imshow('mask', frame)
  #else:
  #    cv2.imshow('mask', frame)
 
  machine.check_state(display_data.get_main_crop(img))
  # BLUE if starting
  if machine.state == GameState.STARTING:
   img[:,:,0] = 255
  # RED if deciding
  elif machine.state == GameState.DECISION:
   img[:,:,2] = 255
  # GREEN if executing
  elif machine.state == GameState.EXECUTION:
   img[:,:,1] = 255
  if machine.state == GameState.STARTING or machine.state == GameState.EXECUTION:
    if box_fitter.check_lines(img):
      quote_text_box = display_data.crop_bbox(img, display_data.quote_bbox)
      color = display_data.message_box_color(quote_text_box)
      text = filter_text(quote_text_box, display_data.min_text, display_data.max_text)
      display_data.set_bbox(img, display_data.quote_bbox, text)
      turn = game_state.Turn.P1 if color == display_data.Color.P1 else game_state.Turn.P2
      if not box_active:
          box_active=True
          queue.add_image_to_processing(text, turn)
    else:
      box_active=False
  else:
      box_active=False
  results = queue.check()
  for r in results:
      text, turn = r
      if turn == game_state.Turn.P1:
          state.update_p1_status(text[0], text[1])
          state.update_p1_boosts(text[0], text[1])
      else:
          state.update_p2_status(text[0], text[1])
          state.update_p2_boosts(text[0], text[1])
    
 
  if machine.state == GameState.DECISION:
    decision_frame+=1
  else:
    decision_frame=0
  #if decision_frame < DECISION_DELAY + 2 and decision_frame > DECISION_DELAY:
  #  print("P1:")
  #  find_hp(img, p1=True)
  #  print("P2:")
  #  find_hp(img, p1=False)
 
     
  #rng = display_data.either_in_range(img)
  #sbl = display_data.sobel_filter(img)
    #img[
  #        display_data.p1_bbox[0][0]:display_data.p1_bbox[1][0],
  #        display_data.p1_bbox[0][1]:display_data.p1_bbox[1][1], 0] = 0
  #img[
  #        display_data.p2_bbox[0][0]:display_data.p2_bbox[1][0],
  #        display_data.p2_bbox[0][1]:display_data.p2_bbox[1][1], 2] = 0
 
  
  cv2.imshow("img", img)
  #hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
  #cv2.imshow("v", hsv[:,:,2])
  #cv2.imshow("sobel", sbl)
 
  if cv2.waitKey(1) == ord('q'):
    break
  
 # When everything done, release the capture
 cap.release()
 cv2.destroyAllWindows()
