import random

from typing import Optional, List

from src.controller.base import Agent
from src.state.pokestate import BattleState, PokemonState, MoveState
from src.state.pokestate_defs import PlayerID, Status

def _get_active_mon(battle_state: BattleState, player_id: PlayerID) -> PokemonState:
    """
    Get the index of the active Pokémon for the specified player.
    """
    if player_id == PlayerID.P1:
        return battle_state.get_player_active_mon()
    else:
        return battle_state.get_opponent_active_mon()

def _is_available_move(move: Optional[MoveState]) -> bool:
    """
    Check if the specified move is available for use.
    """
    if move is None:
        return False
    return not move.disabled and move.pp > 0
    

# TODO: Need to handle in play mon being in order from team preview.
def _get_active_mons(battle_state: BattleState, player_id: PlayerID) -> List[PokemonState]:
    """
    Get the list of active Pokémon for the specified player.
    """
    if player_id == PlayerID.P1:
        return battle_state.player_team.pk_list
    else:
        return battle_state.opponent_team.pk_list


class RandomAgent(Agent):
    """
    A random agent that selects a random action from the available options.
    """
    def __init__(self, player_id: PlayerID = PlayerID.P1):
        self.player_id = player_id

    def choose_action(self, battle_state: BattleState) -> str:
        """
        Select a random action from the available actions.
        """
        active_mon = _get_active_mon(battle_state, self.player_id)
        actions = []
        if not active_mon.status == Status.FAINTED and active_mon.hp > 0:
            if active_mon.move1 and _is_available_move(active_mon.move1):
                actions.append("move 0")
            if active_mon.move2 and _is_available_move(active_mon.move2):
                actions.append("move 1")
            if active_mon.move3 and _is_available_move(active_mon.move3):
                actions.append("move 2")
            if active_mon.move4 and _is_available_move(active_mon.move4):
                actions.append("move 3")
        for i, pokemon in enumerate(_get_active_mons(battle_state, self.player_id)):
            if pokemon.in_play and pokemon != active_mon and pokemon.hp > 0 and pokemon.status != Status.FAINTED:
                actions.append(f"switch {i}")
        if not actions:
            raise ValueError("No valid actions available.")
        return random.choice(actions)
    
            