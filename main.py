import cv2
import numpy as np

from argparse import ArgumentParser
from multiprocessing import shared_memory

from src.display.draw import draw_updates, draw_mode
from src.params.yaml_parser import load_battle_state_from_yaml
from src.rabbitmq.send import publish_message_to_topic
from src.rabbitmq.topics import IMAGE_UPDATE, CONFIG
from src.state.pokestate import print_battle_state
from src.screen_parsing.box_detection import BoxDetection
from src.screen_parsing.stadium_mode import StadiumModeParser
from src.screen_parsing.update_processor import UpdateProcessor
from src.state.pokestate_defs import ImageUpdate
from src.utils.shared_image_list import SharedImageList
from src.utils.serialization import serialize_image_update

def parse_args():
    parser = ArgumentParser(description="Run on input video feed and monitor game state.")
    parser.add_argument('--image_path', type=str, help='Path to the image file')
    # Add option to play from camera
    parser.add_argument('--camera', action='store_true', help='Use camera input instead of image file')
    # TODO: Add debug mode
    parser.add_argument('--debug', action='store_true', help='Enable debug mode [NOT IMPLEMENTED]')
    parser.add_argument('--n-shmem-frames', type=int, default=20, help='Number of frames to keep in shared memory')
    return parser.parse_args()


def check_args(args):
    if not args.image_path and not args.camera:
        raise ValueError("Either image path or camera option must be provided.")

def main(args):
    # Load video capture from file or camera
    if args.camera:
        cap = cv2.VideoCapture(0)  # Use 0 for the default camera
    else:
        image_path = args.image_path
        cap = cv2.VideoCapture(image_path)

    if not cap.isOpened():
        raise ValueError("Could not open video source.")

    box_detection = BoxDetection()
    stadium_mode_parser = StadiumModeParser()
    update_processor = UpdateProcessor(stadium_mode_parser.prev_mode)

    ret, initial_frame = cap.read()  # Read the first frame to initialize shared memory
    if not ret:
        raise ValueError("Could not read from video source.")
    
    camera_config = {
        'name': "video_frames",
        'width': str(initial_frame.shape[1]),
        'height': str(initial_frame.shape[0]),
        'channel': str(initial_frame.shape[2]),
        'dtype': str(initial_frame.dtype),
        'n_shmem_frames': str(args.n_shmem_frames),
    }
    shm = SharedImageList(camera_config=camera_config, create=True)
    publish_message_to_topic('camera_config', camera_config)
    idx=0

    # Read a frame from the video source
    while True:
        frame = shm.get_new_frame()
        ret, _ = cap.read(frame)
        if not ret:
            print("Exiting...")
            break

        updates = box_detection.update(frame)
        stadium_mode = stadium_mode_parser.parse(updates)
        if stadium_mode is not None:
            update_processor.update_mode(stadium_mode)
        processed_updates = update_processor.process_updates(updates, idx)
        for update in processed_updates:
            if isinstance(update, ImageUpdate):
                # Add the update to the queue for processing
                publish_message_to_topic(IMAGE_UPDATE, serialize_image_update(update, shm))
                # print(f"Published ImageUpdate: {update.message_type} for player {update.player_id}")
            else:
                print(f"Unexpected update type: {type(update)}")

        # if await update_queue.done():
        #     # Process the updates in the queue
        #     battle_state = await update_queue.get_state()
        #     print("Battle State Updated:")
        #     print_battle_state(battle_state)
        #     update_queue.reset()


        # Display the image in a window
        idx += 1
        output_frame = frame.copy()
        draw_updates(output_frame, updates)
        output_frame = draw_mode(output_frame, stadium_mode_parser.prev_mode)
        cv2.imshow('Image', output_frame)

        # Wait for 1 ms and check if 'q' is pressed to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    args = parse_args()
    try:
        check_args(args)
        main(args)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)