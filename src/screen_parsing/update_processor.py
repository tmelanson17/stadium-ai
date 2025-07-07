from typing import Sequence

from src.state.pokestate_defs import ImageUpdate, MessageType
from .stadium_mode import StadiumMode, PlayerID

'''
    Takes a list of updates and the StadiumMode and packages them into a more manageable set of updates.
    - If in CHOOSE_MOVE mode, only the first HP readings are allowed.
    - If in EXECUTE mode, only status messages will be sent through.
'''
class UpdateProcessor:
    def __init__(self, mode: StadiumMode):
        """
        Initialize the UpdateProcessor with a specific StadiumMode.
        
        Args:
            mode: The current StadiumMode to process updates for.
        """
        self.mode = mode
        self.hp1_update = None
        self.hp2_update = None
        self.status_update_frame = -1
        self.done = False

    def update_mode(self, mode: StadiumMode):
        """
        Update the current StadiumMode and reset previous updates.
        Args:
        Args:
            mode: The new StadiumMode to set.
        """
        # If mode has changed, reset previous updates
        if mode == StadiumMode.CHOOSE_MOVE and self.mode != StadiumMode.CHOOSE_MOVE:
            self.hp1_update = None
            self.hp2_update = None
            self.status_update = None
            self.status_update_frame = -1
            self.done = False
        elif mode == StadiumMode.EXECUTE and self.mode != StadiumMode.EXECUTE:
            self.hp1_update = None
            self.hp2_update = None
            self.status_update = None
            self.status_update_frame = -1
            self.done = False
        self.mode = mode

    def process_updates(self, updates: Sequence[ImageUpdate], i_frame: int) -> Sequence[ImageUpdate]:
        if self.mode == StadiumMode.CHOOSE_MOVE:
            for update in updates:
                if update and update.message_type == MessageType.HP:
                    if update.player_id == PlayerID.P1 and self.hp1_update is None:
                        self.hp1_update = update
                    elif update.player_id == PlayerID.P2 and self.hp2_update is None:
                        self.hp2_update = update
            if self.hp1_update and self.hp2_update and not self.done:
                # Return both HP updates if both are available
                return_values = [self.hp1_update, self.hp2_update]
                self.done = True
                return return_values
            else:
                return []
        elif self.mode == StadiumMode.EXECUTE:
            updates_filtered = [update for update in updates if update and update.message_type == MessageType.CONDITION]
            return_values = []
            if updates_filtered:
                if self.status_update_frame == -1 or i_frame - self.status_update_frame > 5:
                    self.status_update = updates_filtered[0]
                    self.done  = True
                    return_values = [self.status_update]
                self.status_update_frame = i_frame
            return return_values
        else:
            return []
        