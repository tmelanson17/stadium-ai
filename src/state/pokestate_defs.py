from dataclasses import dataclass
from enum import Enum
from typing import Tuple

import numpy as np

class Status(Enum):
    NONE = 0
    POISONED = 1
    BURNED = 2
    PARALYZED = 3
    SLEEP = 4
    FROZEN = 5
    FAINTED = 6

class PlayerID(Enum):
    P1 = 0
    P2 = 1
    CPU = 2
    INVALID = 3

    def __str__(self):
        return f"PlayerID.{self.name}"

class StadiumMode(Enum):
    CHOOSE_MOVE=0
    EXECUTE=1
    PREVIEW=2
    EXTERNAL=3
    INVALID=4

    def __str__(self):
        return f"StadiumMode.{self.name}"

class MessageType(Enum):
    CONDITION = 0
    HP = 1
    MOVE = 2
    INVALID = 3

    def __str__(self):
        return f"MessageType.{self.name}"

@dataclass 
class Rectangle:
    x1: int
    y1: int
    x2: int
    y2: int

    def __str__(self):
        return f"Rectangle({self.x1}, {self.y1}, {self.x2}, {self.y2})"

    def to_coord(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        '''
        Converts the rectangle to a tuple of ((x1, y1), (x2, y2))
        '''
        return ((self.x1, self.y1), (self.x2, self.y2))

'''
    POD for receiving data for analysis and state update
    Contents:
    - Image : Numpy array for the input frmae
    - ROI : cv2.Rectangle of the section to analyze
    - StadiumMode : Enum Which mode the game is in for that frame
    - player_id : ID of the player that is currently being analyzed. Imporatant for which side to update.
'''
@dataclass
class ImageUpdate:
    image: np.ndarray
    roi: Rectangle
    message_type: MessageType
    player_id: PlayerID