import asyncio
import cv2

from argparse import ArgumentParser

from src.display.draw import draw_updates, draw_mode
from src.state.pokestate import print_battle_state
from src.screen_parsing.box_detection import BoxDetection
from src.screen_parsing.stadium_mode import StadiumModeParser
from src.state.pokestate_defs import ImageUpdate
from src.state_reader.state_reader import UpdateQueue
from src.params.yaml_parser import load_battle_state_from_yaml

def parse_args():
    parser = ArgumentParser(description="Run on input video feed and monitor game state.")
    parser.add_argument('--image_path', type=str, help='Path to the image file')
    # Add option to play from camera
    parser.add_argument('--camera', action='store_true', help='Use camera input instead of image file')
    # TODO: Add debug mode
    parser.add_argument('--debug', action='store_true', help='Enable debug mode [NOT IMPLEMENTED]')
    return parser.parse_args()


def check_args(args):
    if not args.image_path and not args.camera:
        raise ValueError("Either image path or camera option must be provided.")

async def main(args):
    # Load video capture from file or camera
    if args.camera:
        cap = cv2.VideoCapture(0)  # Use 0 for the default camera
    else:
        image_path = args.image_path
        cap = cv2.VideoCapture(image_path)

    if not cap.isOpened():
        raise ValueError("Could not open video source.")

    box_detection = BoxDetection()
    battle_state = load_battle_state_from_yaml('config/battle5.yaml')
    stadium_mode_parser = StadiumModeParser()

    # update_queue = UpdateQueue(battle_state)

    # Read a frame from the video source
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Exiting...")
            break

        updates = box_detection.update(frame)
        _ = stadium_mode_parser.parse(updates)
        # for update in updates:
        #     if isinstance(update, ImageUpdate):
        #         # Add the update to the queue for processing
        #         await update_queue.put(update)
        #     else:
        #         print(f"Unexpected update type: {type(update)}")

        # if await update_queue.done():
        #     # Process the updates in the queue
        #     battle_state = await update_queue.get_state()
        #     print("Battle State Updated:")
        #     print_battle_state(battle_state)
        #     update_queue.reset()


        # Display the image in a window
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
        asyncio.run(main(args))
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)