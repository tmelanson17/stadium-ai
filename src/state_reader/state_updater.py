"""
State updater module for applying parsed changes to the battle state.
"""
from typing import Optional, Tuple
from src.state.pokestate import BattleState, PokemonState
from src.state.pokestate_defs import Status


def enact_changes(battle_state: BattleState, changes: Optional[Tuple], opponent: bool = False) -> None:
    """
    Apply parsed changes to the battle state.
    
    Args:
        battle_state: The battle state to modify
        changes: A tuple describing the change to make (target, property, value)
                 - target: "actor" or "receiver" indicating who is affected
                 - property: the property to change (e.g., "status", "confused", "trapped")
                 - value: the new value for the property
        opponent: Whether the opponent executed the move (True) or player (False)
    """
    if changes is None:
        return
    
    target, property_name, value = changes
    
    # Determine which Pokemon are the actor and receiver
    player_pokemon = battle_state.player_team.pk_list[battle_state.player_active_mon]
    opponent_pokemon = battle_state.opponent_team.pk_list[battle_state.opponent_active_mon]
    
    if opponent:
        # Opponent executed the move
        actor_pokemon = opponent_pokemon
        receiver_pokemon = player_pokemon
    else:
        # Player executed the move
        actor_pokemon = player_pokemon
        receiver_pokemon = opponent_pokemon
    
    # Determine which Pokemon to modify
    if target == "actor":
        target_pokemon = actor_pokemon
    elif target == "receiver":
        target_pokemon = receiver_pokemon
    else:
        # Handle special cases like "self" or "opponent"
        if target == "self":
            target_pokemon = player_pokemon if not opponent else opponent_pokemon
        elif target == "opponent":
            target_pokemon = opponent_pokemon if not opponent else player_pokemon
        else:
            print(f"Warning: Unknown target '{target}' in changes")
            return
    
    # Apply the changes based on the property
    if property_name == "hp":
        target_pokemon.hp = max(0, min(100, value))
    elif property_name == "status":
        target_pokemon.status = value
    elif property_name == "confused":
        target_pokemon.confused = value
    elif property_name == "trapped":
        target_pokemon.trapped = value
    elif property_name == "two_turn_move":
        target_pokemon.two_turn_move = value
    elif property_name == "reflect":
        # TODO: Add reflect field to PokemonState if needed
        print(f"Warning: Reflect not implemented yet")
    elif property_name == "light_screen":
        # TODO: Add light_screen field to PokemonState if needed
        print(f"Warning: Light Screen not implemented yet")
    elif property_name == "switch":
        # Handle Pokemon switching
        if target == "actor":
            if opponent:
                battle_state.opponent_active_mon = value
            else:
                battle_state.player_active_mon = value
        else:
            print(f"Warning: Switch target '{target}' not supported")
    elif property_name in ["attack_boost", "defense_boost", "special_boost", "speed_boost"]:
        # Handle stat boosts
        if property_name == "attack_boost":
            target_pokemon.atk_boost = max(-6, min(6, target_pokemon.atk_boost + value))
        elif property_name == "defense_boost":
            target_pokemon.def_boost = max(-6, min(6, target_pokemon.def_boost + value))
        elif property_name == "special_boost":
            target_pokemon.special_boost = max(-6, min(6, target_pokemon.special_boost + value))
        elif property_name == "speed_boost":
            target_pokemon.speed_boost = max(-6, min(6, target_pokemon.speed_boost + value))
    else:
        print(f"Warning: Unknown property '{property_name}' in changes")


def apply_haze_effect(battle_state: BattleState) -> None:
    """
    Apply the Haze effect, which resets all stat boosts for both Pokemon.
    
    Args:
        battle_state: The battle state to modify
    """
    # Reset all stat boosts for both active Pokemon
    player_pokemon = battle_state.player_team.pk_list[battle_state.player_active_mon]
    opponent_pokemon = battle_state.opponent_team.pk_list[battle_state.opponent_active_mon]
    
    # Reset player Pokemon boosts
    player_pokemon.atk_boost = 0
    player_pokemon.def_boost = 0
    player_pokemon.special_boost = 0
    player_pokemon.speed_boost = 0
    
    # Reset opponent Pokemon boosts
    opponent_pokemon.atk_boost = 0
    opponent_pokemon.def_boost = 0
    opponent_pokemon.special_boost = 0
    opponent_pokemon.speed_boost = 0


def handle_pokemon_switch(battle_state: BattleState, new_index: int, is_opponent: bool = False) -> None:
    """
    Handle switching to a new Pokemon.
    
    Args:
        battle_state: The battle state to modify
        new_index: Index of the Pokemon to switch to
        is_opponent: Whether this is an opponent switch (True) or player switch (False)
    """
    if is_opponent:
        # Reset volatile conditions of the current Pokemon
        current_pokemon = battle_state.opponent_team.pk_list[battle_state.opponent_active_mon]
        reset_volatile_conditions(current_pokemon)
        
        # Switch to new Pokemon
        battle_state.opponent_active_mon = new_index
    else:
        # Reset volatile conditions of the current Pokemon
        current_pokemon = battle_state.player_team.pk_list[battle_state.player_active_mon]
        reset_volatile_conditions(current_pokemon)
        
        # Switch to new Pokemon
        battle_state.player_active_mon = new_index


def reset_volatile_conditions(pokemon: PokemonState) -> None:
    """
    Reset volatile conditions when a Pokemon switches out.
    
    Args:
        pokemon: The Pokemon whose volatile conditions should be reset
    """
    pokemon.confused = False
    pokemon.trapped = False
    pokemon.two_turn_move = False
    pokemon.atk_boost = 0
    pokemon.def_boost = 0
    pokemon.special_boost = 0
    pokemon.speed_boost = 0
    # Note: Status conditions like burn, poison, etc. persist when switching
