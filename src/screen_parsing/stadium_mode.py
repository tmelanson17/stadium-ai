from typing import Sequence, Optional

from src.state.pokestate_defs import StadiumMode, ImageUpdate, MessageType, PlayerID

class StadiumModeParser: 
    """Parses the stadium mode from the box updates.
    """
    def __init__(self):
        self.prev_mode = StadiumMode.INVALID

    def parse(self, box_updates: Sequence[ImageUpdate]) -> Optional[StadiumMode]:
        """Parses the stadium mode from the box updates.
        
        Args:
            box_updates (Sequence[ImageUpdate]): Sequence of box updates.

        Returns:
            StadiumMode: The current stadium mode.
        """
        mode = None
        for update in box_updates:
            img_h, _, _ = update.image.shape
            # Check if the update is an HP MessageType and P2
            if update.message_type == MessageType.HP and update.player_id == PlayerID.P2:
                if update.roi.y1 < img_h / 2:
                    # If on the top half of the screen, it's the Execute mode
                    mode = StadiumMode.EXECUTE
                    break
                else:
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