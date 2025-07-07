from typing import Sequence

from src.state.pokestate_defs import ImageUpdate, MessageType
from .stadium_mode import StadiumMode

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
        self.previous_updates = []

    def update_mode(self, mode: StadiumMode):
        """
        Update the current StadiumMode and reset previous updates.
        
        Args:
            mode: The new StadiumMode to set.
        """
        # If mode has changed, reset previous updates
        if mode != self.mode:
            self.mode = mode
            self.previous_updates = [] 

    def process_updates(self, updates: Sequence[ImageUpdate]) -> Sequence[ImageUpdate]:
        if self.mode == StadiumMode.CHOOSE_MOVE:
            self.updates = updates if len(self.previous_updates) == 0 else []
        elif self.mode == StadiumMode.EXECUTE:
            self.updates = [update for update in updates if update and update.message_type == MessageType.CONDITION]
        else:
            self.updates = []
        
        if len(self.updates) > 0:
            self.previous_updates = self.updates
        return self.updates