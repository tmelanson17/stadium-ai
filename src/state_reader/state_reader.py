from asyncio import Queue
from copy import copy
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar, Generic, Optional, Callable, AnyStr, Any, Tuple

import asyncio
import numpy as np
import time

from src.state_reader.condition_reader import read_text_from_roi
# from src.state.pokestate import BattleState
from src.state_reader.phrases import is_update_message, Messages

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
    stadium_mode: StadiumMode
    player_id: PlayerID

    
''' 
    Creates a class that repeatedly executes "loop" as an asynchronous task.
    This will execute until the task is cancelled.
'''  
Input = TypeVar('Input')
class ContinuousTask(Generic[Input]):
    def __init__(self, queue: Queue[Input], task_fn: Callable[[Input], None]):
        self._task_fn = task_fn 
        self._queue = queue
        self._loop = asyncio.create_task(self.run())

    async def run(self):
        try:
            while not self._queue.empty():
                item = await self._queue.get()
                self._task_fn(item)
                self._queue.task_done()
                await asyncio.sleep(0.1)  # Adjust the sleep time as needed
        except asyncio.CancelledError:
            print("ContinuousTask cancelled.")
            while not self._queue.empty():
                item = await self._queue.get()
                self._queue.task_done()
        finally:
            print("ContinuousTask finished.")

    async def put(self, item: Input):
        '''
        Puts an item into the queue for processing.
        '''
        await self._queue.put(item)
    
    async def close(self):
        '''
        Cancels the task and waits for it to finish.
        '''
        if self._loop:
            self._loop.cancel()
            try:
                await self._loop
            except asyncio.CancelledError:
                pass
    
    async def join(self):
        '''
        Waits for all items in the queue to be processed.
        '''
        await self._queue.join()
        print("All items processed.")

@dataclass
class BattleState:
    p1_hp: int = 0
    p1_condition: Optional[str] = None
    p2_hp : int = 0
    p2_condition: Optional[str] = None

    def __init__(self):
        self.p1_hp = 100
        self.p2_hp = 100
        self.p1_condition = None
        self.p2_condition = None

''' 
    Updates the BattleState [TODO] asynchronously.
    Can pass updates to the BattleState, then call get_state() to retrieve the current state.
'''
class BattleStateUpdate:
    def __init__(self):
        # TODO: Update with real battle state
        self.state = BattleState() 

    def handle_update(self, attribute: str, value: Any):
        print(f"Updating {attribute} to {value}")
        self.state.__setattr__(attribute, value)
    
    def get_state(self) -> BattleState:
        return self.state
'''

    Stub for BattleCondition reader.
    Used for the EXECUTE stage
'''
class BattleConditionReader:
    '''
        Update the battle condition based on the condition message.
    '''
    def update_condition(self, battle_state: BattleStateUpdate, message: Messages, pid: PlayerID) -> None:
        '''
        Updates the battle condition based on the message and player ID.
        This is a stub method that should be implemented with actual logic.
        '''
        print(f"Updating condition for {pid} with message: {message}")
        # Here you would implement the logic to update the battle state
        # based on the message and player ID.
        # For now, we just print the message.
        if message == Messages.STARTPSN:
            print(f"Player {pid} is badly poisoned.")
            battle_state.handle_update(f"{pid.name.lower()}_condition", "badly poisoned")
        

    
    '''
        Reads the battle condition from the image within the specified ROI.
        Returns a string representation of the condition or None if not applicable.
    '''
    def handle_condition_update(self, battle_state: BattleStateUpdate, update: ImageUpdate) -> None:
        '''
        Reads the battle condition from the image within the specified ROI.
        '''
        if update.stadium_mode != StadiumMode.EXECUTE:
            print(f"Skipping condition update for {update.stadium_mode}")
            return
        if update.player_id == PlayerID.INVALID:
            print("Invalid player ID, skipping condition update.")
            return
        player_id = update.player_id.name.lower()
        updates = read_text_from_roi(
            update.image, 
            update.roi.to_coord(), 
            threshold=3
        )
        for text in updates:
            if text is None:
                print("Skipping None text update.")
                continue
            print(f"Condition detected for {player_id}: {text.value}")
            if text.value is not None and is_update_message(text):
                battle_state.handle_update(f"{player_id}_condition", text.value)
        


'''
    Stub for reading the player HP.
'''
class PlayerHPReader:
    def update_hp(self, battle_state: BattleStateUpdate, update: ImageUpdate) -> None:
        '''
        Reads the player HP from the image within the specified ROI.
        Returns an integer representation of the HP or None if not applicable.
        '''
        if update.stadium_mode != StadiumMode.CHOOSE_MOVE:
            print(f"Skipping HP update for {update.stadium_mode}")
            return None
        if update.player_id == PlayerID.INVALID:
            print("Invalid player ID, skipping HP update.")
            return None
        player_id = update.player_id.name.lower()
        battle_state.handle_update(f"{player_id}_hp", 100)  # Stub value, replace with actual logic

    
'''
    StateReader is responsible for maintaining the internal state of the battle.
    It processes ImageUpdates and updates the BattleState accordingly.
    TODO: Add more complex state-dependent logic.
'''
class StateReader:
    def __init__(self):
        self.state = BattleStateUpdate()
        self.condition_reader = BattleConditionReader()
        self.hp_reader = PlayerHPReader()

    def handle_update(self, update: ImageUpdate):
        # This method should handle the update and modify the internal state accordingly
        time.sleep(1)
        if update.stadium_mode == StadiumMode.EXECUTE:
            self.condition_reader.handle_condition_update(self.state, update)
        elif update.stadium_mode == StadiumMode.CHOOSE_MOVE:
            self.hp_reader.update_hp(self.state, update)
        

    def get_state(self) -> BattleState:
        return self.state.get_state()


'''
    Main interface for managing the queue of ImageUpdates.
'''
class UpdateQueue():
    def __init__(self):
        self.queue: Queue[ImageUpdate] = Queue()
        self.state_reader: StateReader = StateReader()
        self.processor = ContinuousTask(self.queue, self.state_reader.handle_update)

    async def put(self, item : ImageUpdate):
        await self.queue.put(item)

    # Waits for all items in the queue to be processed, then returns the current state
    async def get_state(self) -> BattleState:
        await self.processor.join()  # Wait for all items to be processed
        return self.state_reader.get_state()
    
    async def close(self):
        '''
        Closes the queue and cancels the processing task.
        '''
        await self.processor.close()
