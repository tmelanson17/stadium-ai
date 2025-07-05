from asyncio import Queue
from copy import copy
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar, Generic, Optional, Callable, Awaitable, Tuple

import asyncio
import numpy as np
import time

from src.state.pokestate import BattleState, PokemonState, create_default_battle_state
from src.state.pokestate_defs import PlayerID, MessageType, ImageUpdate
from src.state_reader.condition_reader import read_text_from_roi
from src.state_reader.phrases import parse_update_message, Messages
from src.state_reader.state_updater import enact_changes
from src.state_reader.hp_reader import get_hp
    
''' 
    Creates a class that repeatedly executes "loop" as an asynchronous task.
    This will execute until the task is cancelled.
'''  
Input = TypeVar('Input')
class ContinuousTask(Generic[Input]):
    def __init__(self, queue: Queue[Input], task_fn: Callable[[Input], Awaitable[None]]):
        self._task_fn = task_fn 
        self._queue = queue
        self._loop = asyncio.create_task(self.run())

    async def run(self):
        try:
            while not self._queue.empty():
                item = await self._queue.get()
                await self._task_fn(item)
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
'''
    Wrapper for BattleState to handle updates and locking.
'''
class BattleStateUpdate:
    def __init__(self, battle_state: Optional[BattleState] = None):
        if battle_state is None:
            self._state = create_default_battle_state()
        else:
            self._state = battle_state
        self._lock = asyncio.Lock()

    async def lock_state(self):
        await self._lock.acquire()

    def unlock_state(self):
        self._lock.release()

    def get_active_pokemon(self, player_id: PlayerID) -> PokemonState:
        if player_id == PlayerID.P1:
            return self._state.player_team.pk_list[self._state.player_active_mon]
        elif player_id == PlayerID.P2:
            return self._state.opponent_team.pk_list[self._state.opponent_active_mon]
        else:
            raise ValueError(f"Invalid player ID: {player_id}")

    def get_state(self) -> BattleState:
        return self._state


'''

    Stub for BattleCondition reader.
    Used for the EXECUTE stage
'''
class BattleConditionReader:
    '''
        Update the battle condition based on the condition message.
    '''
    async def update_condition(self, battle_state: BattleStateUpdate, message: str, pid: PlayerID) -> None:
        opponent = pid != PlayerID.P1
        await battle_state.lock_state()
        state = battle_state.get_state()
        change = parse_update_message(message, state, opponent)
        if change is None:
            print(f"No change parsed from message: {message}")
        else:
            print(f"Applying change: {change} for player {pid}")
            # Apply the changes to the battle state
            enact_changes(state, change, opponent)
        battle_state.unlock_state()
        

    
    '''
        Reads the battle condition from the image within the specified ROI.
        Returns a string representation of the condition or None if not applicable.
    '''
    async def handle_condition_update(self, battle_state: BattleStateUpdate, update: ImageUpdate) -> None:
        '''
        Reads the battle condition from the image within the specified ROI.
        '''
        if update.message_type != MessageType.CONDITION:
            print(f"Skipping condition update for {update.message_type}")
            return
        if update.player_id == PlayerID.INVALID:
            print("Invalid player ID, skipping condition update.")
            return
        updates = read_text_from_roi(
            update.image, 
            update.roi.to_coord(), 
        )
        for text in updates:
            if text is None:
                print("Skipping None text update.")
                continue
            print(f"Condition detected for {update.player_id.value}: {text}")
            await self.update_condition(battle_state, text, update.player_id)
        


'''
    Stub for reading the player HP.
'''
class PlayerHPReader:
    async def update_hp(self, battle_state: BattleStateUpdate, update: ImageUpdate) -> None:
        '''
        Reads the player HP from the image within the specified ROI.
        Returns an integer representation of the HP or None if not applicable.
        '''
        if update.message_type != MessageType.HP:
            print(f"Skipping HP update for {update.message_type}")
            return None
        if update.player_id == PlayerID.INVALID:
            print("Invalid player ID, skipping HP update.")
            return None
        hp = get_hp(update.image, update.roi.to_coord())
        await battle_state.lock_state()
        # TODO: Have some filtering on the read HP
        state = battle_state.get_state()
        opponent = update.player_id != PlayerID.P1
        enact_changes(state, ("actor","hp",hp), opponent)
        battle_state.unlock_state()

    
'''
    StateReader is responsible for maintaining the internal state of the battle.
    It processes ImageUpdates and updates the BattleState accordingly.
    TODO: Add more complex state-dependent logic.
'''
class StateReader:
    def __init__(self, initial_state: Optional[BattleState] = None):
        self.state = BattleStateUpdate(initial_state)
        self.condition_reader = BattleConditionReader()
        self.hp_reader = PlayerHPReader()

    async def handle_update(self, update: ImageUpdate):
        # This method should handle the update and modify the internal state accordingly
        time.sleep(1)
        if update.message_type == MessageType.CONDITION:
            await self.condition_reader.handle_condition_update(self.state, update)
        elif update.message_type == MessageType.HP:
            await self.hp_reader.update_hp(self.state, update)
        

    def get_state(self) -> BattleState:
        return self.state.get_state()


'''
    Main interface for managing the queue of ImageUpdates.
'''
class UpdateQueue():
    def __init__(self, battle_state: Optional[BattleState] = None):
        self.queue: Queue[ImageUpdate] = Queue()
        self.state_reader: StateReader = StateReader(battle_state)
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
