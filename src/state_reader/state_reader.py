from asyncio import Queue
from copy import copy
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict

import numpy as np

from src.state.pokestate import BattleState, PokemonState, create_default_battle_state
from src.state.pokestate_defs import PlayerID, MessageType, ImageUpdate
from src.state_reader.condition_reader import read_text_from_roi
from src.state_reader.phrases import parse_update_message, Messages
from src.state_reader.state_updater import enact_changes
from src.state_reader.hp_reader import get_hp
from src.utils.shared_image_list import SharedImageList
from src.utils.serialization import deserialize_image_update
from src.rabbitmq.receive import listen
from src.rabbitmq.topics import CONFIG, IMAGE_UPDATE
    
'''
    Wrapper for BattleState to handle updates and locking.
'''
class BattleStateUpdate:
    def __init__(self, battle_state: Optional[BattleState] = None):
        if battle_state is None:
            self._state = create_default_battle_state()
        else:
            self._state = battle_state

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
    updated: bool = False
    
    '''
        Update the battle condition based on the condition message.
    '''
    def update_condition(self, battle_state: BattleStateUpdate, message: str, pid: PlayerID) -> None:
        opponent = pid != PlayerID.P1
        state = battle_state.get_state()
        change = parse_update_message(message, state, opponent)
        if change is None:
            print(f"No change parsed from message: {message}")
        else:
            print(f"Applying change: {change} for player {pid}")
            # Apply the changes to the battle state
            enact_changes(state, change, opponent)
            self.updated = True
        

    
    '''
        Reads the battle condition from the image within the specified ROI.
        Returns a string representation of the condition or None if not applicable.
    '''
    def handle_condition_update(self, battle_state: BattleStateUpdate, update: ImageUpdate) -> None:
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
            self.update_condition(battle_state, text, update.player_id)
        


'''
    Stub for reading the player HP.
'''
class PlayerHPReader:
    updated: bool = False
    
    def update_hp(self, battle_state: BattleStateUpdate, update: ImageUpdate) -> None:
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
        print(f"Updating HP for {update.player_id.value}...")
        hp = get_hp(update.image, update.roi.to_coord())
        print(f"Read HP: {hp} for player {update.player_id.value}")
        if hp < 0:
            print("Invalid HP read, skipping update.")
            return
        # TODO: Have some filtering on the read HP
        state = battle_state.get_state()
        opponent = update.player_id != PlayerID.P1
        enact_changes(state, ("actor","hp",hp), opponent)
        self.updated = True

    
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
        self.shm = None

    def handle_update(self, update: ImageUpdate):
        # This method should handle the update and modify the internal state accordingly
        if update.message_type == MessageType.CONDITION:
            self.condition_reader.handle_condition_update(self.state, update)
        elif update.message_type == MessageType.HP:
            self.hp_reader.update_hp(self.state, update)
        
    def handle_update_wrapper(self, update_dict: Dict[str, str]):
        '''
        Wrapper for handling updates from a dictionary.
        This is useful for deserializing updates from JSON or other formats.
        '''
        if self.shm is None:
            raise ValueError("SharedImageList not initialized. Call handle_camera_config first.")
        update = deserialize_image_update(update_dict, self.shm)
        if update is None:
            print("Failed to deserialize ImageUpdate, skipping.")
            return
        self.handle_update(update)

    def handle_camera_config(self, config: Dict[str, str]):
        self.shm = SharedImageList(config, create=False)
         

    def get_state(self) -> BattleState:
        return self.state.get_state()

    def updated(self) -> bool:
        '''
        Returns True if any updates were made to the state.
        '''
        return self.condition_reader.updated and self.hp_reader.updated
    
    def reset(self):
        '''
        Resets the state reader to its initial state.
        '''
        self.condition_reader.updated = False
        self.hp_reader.updated = False

from argparse import ArgumentParser

# Parse the args for a battle state config to start the StateReader
def parse_args():
    parser = ArgumentParser(description="Reads state from continuous updates")
    parser.add_argument('--config', type=str, default='config/example.yaml', help='Path to the configuration YAML file')
    return parser.parse_args()
    
    

if __name__ == "__main__":
    from src.params.yaml_parser import load_battle_state_from_yaml
    args = parse_args()
    battle_state = load_battle_state_from_yaml(args.config)
    reader = StateReader(battle_state)
    callbacks = {
        CONFIG: reader.handle_camera_config,
        IMAGE_UPDATE: reader.handle_update_wrapper        
    }
    listen(callbacks)
