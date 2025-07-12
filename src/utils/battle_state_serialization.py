"""
BattleState Serialization Module

This module provides serialization/deserialization functionality for BattleState objects
used in the Pokemon Stadium AI system. The main purpose is to convert BattleState
instances to/from JSON-compatible dictionaries for storage, transmission, or caching.

Key Features:
- Converts all BattleState data including teams, Pokemon, and moves to JSON format
- Preserves all battle state metadata (active Pokemon, stats, conditions)
- Supports both convenience functions and class-based approach
- Handles nested structures (BattleState -> TeamState -> PokemonState -> MoveState)

Usage:
    # Quick serialization
    data = serialize_battle_state(battle_state)
    restored = deserialize_battle_state(data)
    
    # Advanced usage with persistent serializer
    serializer = BattleStateSerializer()
    data = serializer.to_dict(battle_state)
    restored = serializer.from_dict(data)
"""

from typing import Dict, List, Optional, Any
import json

from src.state.pokestate import BattleState, TeamState, PokemonState, MoveState
from src.state.pokestate_defs import Status, MessageType, PlayerID


class BattleStateSerializer:
    """
    Serializes BattleState objects to/from JSON format.
    """
    
    def to_dict(self, battle_state: BattleState) -> Dict[str, Any]:
        """
        Convert BattleState to JSON-serializable dictionary.
        
        Args:
            battle_state: BattleState instance to serialize
        
        Returns:
            Dictionary containing serialized BattleState data
        """
        return {
            "player_active_mon": battle_state.player_active_mon,
            "opponent_active_mon": battle_state.opponent_active_mon,
            "player_team": self._serialize_team_state(battle_state.player_team),
            "opponent_team": self._serialize_team_state(battle_state.opponent_team)
        }
    
    def from_dict(self, data: Dict[str, Any]) -> BattleState:
        """
        Convert dictionary back to BattleState instance.
        
        Args:
            data: Dictionary containing serialized BattleState data
            
        Returns:
            BattleState instance reconstructed from dictionary
        """
        return BattleState(
            player_active_mon=data["player_active_mon"],
            opponent_active_mon=data["opponent_active_mon"],
            player_team=self._deserialize_team_state(data["player_team"]),
            opponent_team=self._deserialize_team_state(data["opponent_team"])
        )
    
    def _serialize_team_state(self, team_state: TeamState) -> Dict[str, Any]:
        """Serialize TeamState to dictionary."""
        return {
            "pk_list": [self._serialize_pokemon_state(pokemon) for pokemon in team_state.pk_list]
        }
    
    def _deserialize_team_state(self, data: Dict[str, Any]) -> TeamState:
        """Deserialize dictionary to TeamState."""
        return TeamState(
            pk_list=[self._deserialize_pokemon_state(pokemon_data) for pokemon_data in data["pk_list"]]
        )
    
    def _serialize_pokemon_state(self, pokemon: PokemonState) -> Dict[str, Any]:
        """Serialize PokemonState to dictionary."""
        return {
            "active": pokemon.active,
            "known": pokemon.known,
            "revealed": pokemon.revealed,
            "in_play": pokemon.in_play,
            "level": pokemon.level,
            "name": pokemon.name,
            "species": pokemon.species,
            "type1": pokemon.type1,
            "type2": pokemon.type2,
            "hp": pokemon.hp,
            "status": pokemon.status.value,
            "trapped": pokemon.trapped,
            "two_turn_move": pokemon.two_turn_move,
            "confused": pokemon.confused,
            "sleep_turns": pokemon.sleep_turns,
            "substitute": pokemon.substitute,
            "reflect": pokemon.reflect,
            "light_screen": pokemon.light_screen,
            "atk_boost": pokemon.atk_boost,
            "def_boost": pokemon.def_boost,
            "special_boost": pokemon.special_boost,
            "speed_boost": pokemon.speed_boost,
            "move1": self._serialize_move_state(pokemon.move1) if pokemon.move1 else None,
            "move2": self._serialize_move_state(pokemon.move2) if pokemon.move2 else None,
            "move3": self._serialize_move_state(pokemon.move3) if pokemon.move3 else None,
            "move4": self._serialize_move_state(pokemon.move4) if pokemon.move4 else None
        }
    
    def _deserialize_pokemon_state(self, data: Dict[str, Any]) -> PokemonState:
        """Deserialize dictionary to PokemonState."""
        return PokemonState(
            active=data["active"],
            known=data["known"],
            revealed=data["revealed"],
            in_play=data["in_play"],
            level=data["level"],
            name=data["name"],
            species=data["species"],
            type1=data["type1"],
            type2=data["type2"],
            hp=data["hp"],
            status=Status(data["status"]),
            trapped=data["trapped"],
            two_turn_move=data["two_turn_move"],
            confused=data["confused"],
            sleep_turns=data["sleep_turns"],
            substitute=data["substitute"],
            reflect=data["reflect"],
            light_screen=data["light_screen"],
            atk_boost=data["atk_boost"],
            def_boost=data["def_boost"],
            special_boost=data["special_boost"],
            speed_boost=data["speed_boost"],
            move1=self._deserialize_move_state(data["move1"]) if data["move1"] else None,
            move2=self._deserialize_move_state(data["move2"]) if data["move2"] else None,
            move3=self._deserialize_move_state(data["move3"]) if data["move3"] else None,
            move4=self._deserialize_move_state(data["move4"]) if data["move4"] else None
        )
    
    def _serialize_move_state(self, move: MoveState) -> Dict[str, Any]:
        """Serialize MoveState to dictionary."""
        return {
            "known": move.known,
            "name": move.name,
            "pp": move.pp,
            "pp_max": move.pp_max,
            "disabled": move.disabled
        }
    
    def _deserialize_move_state(self, data: Dict[str, Any]) -> MoveState:
        """Deserialize dictionary to MoveState."""
        return MoveState(
            known=data["known"],
            name=data["name"],
            pp=data["pp"],
            pp_max=data["pp_max"],
            disabled=data["disabled"]
        )
    
    def to_json(self, battle_state: BattleState, indent: Optional[int] = None) -> str:
        """
        Convert BattleState to JSON string.
        
        Args:
            battle_state: BattleState instance to serialize
            indent: JSON indentation level (None for compact, 2 for pretty)
        
        Returns:
            JSON string representation of the BattleState
        """
        return json.dumps(self.to_dict(battle_state), indent=indent)
    
    def from_json(self, json_str: str) -> BattleState:
        """
        Convert JSON string back to BattleState instance.
        
        Args:
            json_str: JSON string containing serialized BattleState data
            
        Returns:
            BattleState instance reconstructed from JSON
        """
        data = json.loads(json_str)
        return self.from_dict(data)


def serialize_battle_state(battle_state: BattleState) -> Dict[str, Any]:
    """
    Convenience function to serialize a BattleState to a dictionary.
    
    Args:
        battle_state: BattleState instance to serialize
        
    Returns:
        Dictionary containing serialized BattleState data
    """
    serializer = BattleStateSerializer()
    return serializer.to_dict(battle_state)


def deserialize_battle_state(data: Dict[str, Any]) -> BattleState:
    """
    Convenience function to deserialize a dictionary to a BattleState.
    
    Args:
        data: Dictionary containing serialized BattleState data
        
    Returns:
        BattleState instance
    """
    serializer = BattleStateSerializer()
    return serializer.from_dict(data)


def battle_state_to_json(battle_state: BattleState, indent: Optional[int] = None) -> str:
    """
    Convenience function to serialize a BattleState to JSON string.
    
    Args:
        battle_state: BattleState instance to serialize
        indent: JSON indentation level (None for compact, 2 for pretty)
        
    Returns:
        JSON string representation of the BattleState
    """
    serializer = BattleStateSerializer()
    return serializer.to_json(battle_state, indent)


def battle_state_from_json(json_str: str) -> BattleState:
    """
    Convenience function to deserialize a JSON string to a BattleState.
    
    Args:
        json_str: JSON string containing serialized BattleState data
        
    Returns:
        BattleState instance
    """
    serializer = BattleStateSerializer()
    return serializer.from_json(json_str)