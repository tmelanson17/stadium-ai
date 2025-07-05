import yaml
import random
import sys
import os
from typing import Dict, List, Any, Optional

from src.state.pokestate import BattleState, TeamState, PokemonState, MoveState
from src.state.pokestate_defs import Status
import src.state.gen1_dex as dex
import src.state.gen1_moves as moves


def load_battle_state_from_yaml(yaml_path: str) -> BattleState:
    """
    Load a BattleState from a YAML file.
    
    Args:
        yaml_path: Path to the YAML file containing battle configuration
        
    Returns:
        BattleState object loaded from the YAML file
        
    Raises:
        ValueError: If required data is missing or invalid
        FileNotFoundError: If the YAML file doesn't exist
    """
    with open(yaml_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    
    return parse_battle_state_from_dict(data)


def parse_battle_state_from_dict(data: Dict[str, Any]) -> BattleState:
    """
    Parse a BattleState from a dictionary (typically loaded from YAML).
    
    Args:
        data: Dictionary containing battle configuration
        
    Returns:
        BattleState object
    """
    if 'Team 1' not in data or 'Team 2' not in data:
        raise ValueError("YAML must contain 'Team 1' and 'Team 2' sections")
    
    # Parse both teams
    team1_data = data['Team 1']
    team2_data = data['Team 2']
    
    player_team = parse_team_from_dict(team1_data)
    opponent_team = parse_team_from_dict(team2_data)
    
    # Create BattleState with first Pokemon active by default
    return BattleState(
        player_active_mon=0,
        opponent_active_mon=0,
        player_team=player_team,
        opponent_team=opponent_team
    )


def parse_team_from_dict(team_data: List[Dict[str, Any]]) -> TeamState:
    """
    Parse a TeamState from a list of Pokemon data.
    
    Args:
        team_data: List of dictionaries, each containing Pokemon configuration
        
    Returns:
        TeamState object
    """
    if len(team_data) != 6:
        raise ValueError(f"Team must have exactly 6 Pokemon, got {len(team_data)}")
    
    pokemon_list = []
    for i, pokemon_data in enumerate(team_data):
        pokemon = parse_pokemon_from_dict(pokemon_data, is_first=(i == 0))
        pokemon_list.append(pokemon)
    
    return TeamState(pk_list=pokemon_list)


def parse_pokemon_from_dict(pokemon_data: Dict[str, Any], is_first: bool = False) -> PokemonState:
    """
    Parse a PokemonState from a dictionary.
    
    Args:
        pokemon_data: Dictionary containing Pokemon configuration
        is_first: Whether this is the first Pokemon in the team (will be active)
        
    Returns:
        PokemonState object
    """
    # Required fields
    if 'species' not in pokemon_data:
        raise ValueError("Pokemon must have a 'species' field")
    
    species_name = pokemon_data['species']
    nickname = pokemon_data.get('nickname', species_name)
    
    # Get species data from dex
    try:
        dex_num, type1, type2, base_stats = dex.get_pokemon_by_name(species_name)
    except ValueError as e:
        raise ValueError(f"Unknown Pokemon species: {species_name}") from e
    
    # Parse moves
    moves_data = pokemon_data.get('moves', [])
    if len(moves_data) < 3:
        raise ValueError(f"Pokemon must have at least 3 moves, got {len(moves_data)}")
    if len(moves_data) > 4:
        raise ValueError(f"Pokemon can have at most 4 moves, got {len(moves_data)}")
    
    # Parse each move
    move_states = []
    for move_name in moves_data:
        move_state = parse_move_from_name(move_name)
        move_states.append(move_state)
    
    # Fill remaining move slots with None
    while len(move_states) < 4:
        move_states.append(None)
    
    # Get level (default to 50 for competitive play)
    level = pokemon_data.get('level', 50)
    
    # Create PokemonState
    return PokemonState(
        active=is_first,  # First Pokemon in team is active
        known=True,       # Assume all Pokemon are known for simplicity
        revealed=is_first, # First Pokemon is revealed
        in_play=True,     # All Pokemon are brought to battle
        level=level,
        name=nickname,
        species=species_name,
        type1=type1,
        type2=type2 if type2 else None,
        hp=100.0,         # Start at full HP
        status=Status.NONE,
        trapped=False,
        two_turn_move=False,
        confused=False,
        sleep_turns=0,
        substitute=False,
        reflect=False,
        light_screen=False,
        atk_boost=0,
        def_boost=0,
        special_boost=0,
        speed_boost=0,
        move1=move_states[0],
        move2=move_states[1],
        move3=move_states[2],
        move4=move_states[3]
    )


def parse_move_from_name(move_name: str) -> MoveState:
    """
    Parse a MoveState from a move name.
    
    Args:
        move_name: Name of the move
        
    Returns:
        MoveState object
    """
    # Get move data from moves module
    move_data = moves.get_move_by_name(move_name)
    if move_data is None:
        raise ValueError(f"Unknown move: {move_name}")
    
    return MoveState(
        known=True,
        name=move_name,
        pp=move_data.pp,
        pp_max=move_data.pp,
        disabled=False
    )
