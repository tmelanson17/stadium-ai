from typing import Sequence, Optional
import cv2
import numpy as np

from src.state.pokestate_defs import StadiumMode, ImageUpdate, MessageType, PlayerID

BATTLE_BEGIN_THRESHOLD = 160

class StadiumModeParser: 
    """Parses the stadium mode from the box updates.
    """
    def __init__(self):
        self.prev_mode = StadiumMode.PREVIEW

    def check_battle_begin(self, frame) -> bool:
        """
        Check if the battle has begun by looking for a mostly white frame.
        Args:
            frame (np.ndarray): The current video frame.
        Returns:
            bool: True if the battle has begun, False otherwise.
        """
        if self.prev_mode != StadiumMode.PREVIEW:
            return True
        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Compute the mean pixel value
        mean_val = np.mean(gray)
        # Check if the mean value is above a certain threshold
        return mean_val > BATTLE_BEGIN_THRESHOLD


    def parse(self, box_updates: Sequence[ImageUpdate]) -> Optional[StadiumMode]:
        """Parses the stadium mode from the box updates.
        
        Args:
            box_updates (Sequence[ImageUpdate]): Sequence of box updates.

        Returns:
            StadiumMode: The current stadium mode.
        """
        mode = None
        if self.prev_mode == StadiumMode.PREVIEW:
            # Should autmatically transition once the battle begins
            mode = StadiumMode.EXECUTE
        else:
            for update in box_updates:
                img_h, img_w, _ = update.image.shape
                # Check if the update is an HP MessageType and P2
                if update.message_type == MessageType.HP and update.player_id == PlayerID.P2:
                    if update.roi.y1 < img_h / 2 and update.roi.x1 > img_w / 2:
                        # If on the top half of the screen, it's the Execute mode
                        mode = StadiumMode.EXECUTE
                        break
                    elif update.roi.y1 >= img_h / 2 and update.roi.x1 > img_w / 2:
                        # If on the bottom half of the screen, it's the Choose Move mode
                        mode = StadiumMode.CHOOSE_MOVE
                        break
                # If the condition message exists, set the mode to Execute
                elif update.message_type == MessageType.CONDITION:
                    mode = StadiumMode.EXECUTE
                    break
        if mode is not None and mode != self.prev_mode:
            print(f"Stadium mode changed from {self.prev_mode} to {mode}")
            self.prev_mode = mode
            return self.prev_mode
        else:
            return None