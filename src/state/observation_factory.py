"""
ObservationFactory for converting BattleState objects into numpy arrays for AI training.

This module provides functionality to encode a complete BattleState into a fixed-size
numpy array that can be consumed by machine learning models.
"""

import numpy as np
from typing import Optional, List, Dict

from src.state.pokestate import BattleState, TeamState, PokemonState, MoveState
from src.state.pokestate_defs import Status
import src.state.gen1_moves as moves
import src.state.gen1_dex as dex


class ObservationFactory:
    """Factory class for converting BattleState objects into numpy observation arrays."""
    
    def __init__(self):
        """Initialize the observation factory with move and Pokemon mappings."""
        # Create mappings for efficient encoding
        self.move_to_index = {move.name: idx for idx, move in enumerate(moves.GEN1_MOVES)}
        self.pokemon_to_index = {name: idx for idx, name in enumerate(dex.GEN1_POKEMON.keys())}
        self.type_to_index = {type_name: idx for idx, type_name in enumerate(dex.TYPES)}
        self.status_to_index = {status: status.value for status in Status}
        
        # Calculate observation dimensions
        self.move_encoding_size = len(moves.GEN1_MOVES)
        self.pokemon_encoding_size = len(dex.GEN1_POKEMON)
        self.type_encoding_size = len(dex.TYPES)
        self.pokemon_state_size = self._calculate_pokemon_state_size()
        self.team_state_size = 6 * self.pokemon_state_size  # 6 Pokemon per team
        self.battle_state_size = 2 + 2 * self.team_state_size  # 2 active indices + 2 teams
        
    def _calculate_pokemon_state_size(self) -> int:
        """Calculate the size needed to encode a single Pokemon state."""
        size = 0
        
        # Boolean flags (10 booleans)
        size += 10  # active, known, revealed, in_play, trapped, two_turn_move, confused, substitute, reflect, light_screen
        
        # Scalar values (7 scalars)
        size += 7  # level, hp, sleep_turns, atk_boost, def_boost, special_boost, speed_boost
        
        # Status (one-hot encoded)
        size += len(Status)
        
        # Species (one-hot encoded)
        size += self.pokemon_encoding_size
        
        # Types (two one-hot encoded vectors for dual types)
        size += 2 * self.type_encoding_size
        
        # Moves (4 moves, each with its own encoding)
        size += 4 * self._calculate_move_state_size()
        
        return size
    
    def _calculate_move_state_size(self) -> int:
        """Calculate the size needed to encode a single move state."""
        size = 0
        
        # Boolean flags (2 booleans)
        size += 2  # known, disabled
        
        # PP values (2 scalars)
        size += 2  # pp, pp_max (normalized to 0-1 range)
        
        # Move identity (one-hot encoded)
        size += self.move_encoding_size
        
        return size
    
    def encode_move_state(self, move_state: Optional[MoveState]) -> np.ndarray:
        """Encode a single move state into a numpy array."""
        size = self._calculate_move_state_size()
        encoding = np.zeros(size, dtype=np.float32)
        
        if move_state is None:
            return encoding
        
        offset = 0
        
        # Boolean flags
        encoding[offset] = float(move_state.known)
        encoding[offset + 1] = float(move_state.disabled)
        offset += 2
        
        # PP values (normalized to 0-1 range based on max PP of 40 in Gen 1)
        encoding[offset] = move_state.pp / 40.0
        encoding[offset + 1] = move_state.pp_max / 40.0
        offset += 2
        
        # Move identity (one-hot encoded)
        if move_state.known and move_state.name and move_state.name in self.move_to_index:
            move_idx = self.move_to_index[move_state.name]
            encoding[offset + move_idx] = 1.0
        
        return encoding
    
    def encode_pokemon_state(self, pokemon: PokemonState) -> np.ndarray:
        """Encode a single Pokemon state into a numpy array."""
        encoding = np.zeros(self.pokemon_state_size, dtype=np.float32)
        offset = 0
        
        # Boolean flags
        encoding[offset] = float(pokemon.active)
        encoding[offset + 1] = float(pokemon.known)
        encoding[offset + 2] = float(pokemon.revealed)
        encoding[offset + 3] = float(pokemon.in_play)
        encoding[offset + 4] = float(pokemon.trapped)
        encoding[offset + 5] = float(pokemon.two_turn_move)
        encoding[offset + 6] = float(pokemon.confused)
        encoding[offset + 7] = float(pokemon.substitute)
        encoding[offset + 8] = float(pokemon.reflect)
        encoding[offset + 9] = float(pokemon.light_screen)
        offset += 10
        
        # Scalar values
        encoding[offset] = pokemon.level / 100.0  # Normalize level to 0-1 range
        encoding[offset + 1] = pokemon.hp / 100.0  # HP is already a percentage
        encoding[offset + 2] = min(pokemon.sleep_turns / 7.0, 1.0)  # Max sleep turns in Gen 1 is 7
        # Stat boosts range from -6 to +6, normalize to 0-1 range
        encoding[offset + 3] = (pokemon.atk_boost + 6) / 12.0
        encoding[offset + 4] = (pokemon.def_boost + 6) / 12.0
        encoding[offset + 5] = (pokemon.special_boost + 6) / 12.0
        encoding[offset + 6] = (pokemon.speed_boost + 6) / 12.0
        offset += 7
        
        # Status (one-hot encoded)
        status_idx = self.status_to_index[pokemon.status]
        encoding[offset + status_idx] = 1.0
        offset += len(Status)
        
        # Species (one-hot encoded)
        if pokemon.known and pokemon.species and pokemon.species in self.pokemon_to_index:
            species_idx = self.pokemon_to_index[pokemon.species]
            encoding[offset + species_idx] = 1.0
        offset += self.pokemon_encoding_size
        
        # Type 1 (one-hot encoded)
        if pokemon.known and pokemon.type1 and pokemon.type1 in self.type_to_index:
            type1_idx = self.type_to_index[pokemon.type1]
            encoding[offset + type1_idx] = 1.0
        offset += self.type_encoding_size
        
        # Type 2 (one-hot encoded)
        if pokemon.known and pokemon.type2 and pokemon.type2 in self.type_to_index:
            type2_idx = self.type_to_index[pokemon.type2]
            encoding[offset + type2_idx] = 1.0
        offset += self.type_encoding_size
        
        # Moves (4 moves)
        for move in [pokemon.move1, pokemon.move2, pokemon.move3, pokemon.move4]:
            move_encoding = self.encode_move_state(move)
            encoding[offset:offset + len(move_encoding)] = move_encoding
            offset += len(move_encoding)
        
        return encoding
    
    def encode_team_state(self, team: TeamState) -> np.ndarray:
        """Encode a team state into a numpy array."""
        encoding = np.zeros(self.team_state_size, dtype=np.float32)
        
        # Encode each Pokemon in the team
        for i in range(6):  # Always encode 6 Pokemon slots
            pokemon = team.pk_list[i] if i < len(team.pk_list) else PokemonState()
            pokemon_encoding = self.encode_pokemon_state(pokemon)
            start_idx = i * self.pokemon_state_size
            end_idx = start_idx + self.pokemon_state_size
            encoding[start_idx:end_idx] = pokemon_encoding
        
        return encoding
    
    def encode_battle_state(self, battle_state: BattleState) -> np.ndarray:
        """
        Encode a complete battle state into a numpy array.
        
        Args:
            battle_state: The BattleState object to encode
            
        Returns:
            A numpy array representing the complete battle state
        """
        encoding = np.zeros(self.battle_state_size, dtype=np.float32)
        offset = 0
        
        # Active Pokemon indices (normalized to 0-1 range)
        encoding[offset] = battle_state.player_active_mon / 5.0  # 0-5 normalized to 0-1
        encoding[offset + 1] = battle_state.opponent_active_mon / 5.0
        offset += 2
        
        # Player team
        player_team_encoding = self.encode_team_state(battle_state.player_team)
        encoding[offset:offset + self.team_state_size] = player_team_encoding
        offset += self.team_state_size
        
        # Opponent team
        opponent_team_encoding = self.encode_team_state(battle_state.opponent_team)
        encoding[offset:offset + self.team_state_size] = opponent_team_encoding
        
        return encoding
    
    def decode_move_state(self, encoding: np.ndarray) -> MoveState:
        """Decode a move state from a numpy array."""
        offset = 0
        
        # Boolean flags
        known = bool(encoding[offset] > 0.5)
        disabled = bool(encoding[offset + 1] > 0.5)
        offset += 2
        
        # PP values (denormalize from 0-1 range)
        pp = int(round(encoding[offset] * 40.0))
        pp_max = int(round(encoding[offset + 1] * 40.0))
        offset += 2
        
        # Move identity (find the one-hot encoded move)
        move_name = None
        if known:
            move_encoding = encoding[offset:offset + self.move_encoding_size]
            move_idx = np.argmax(move_encoding)
            if move_encoding[move_idx] > 0.5:  # Check if there's actually a move encoded
                # Find move name by index
                for name, idx in self.move_to_index.items():
                    if idx == move_idx:
                        move_name = name
                        break
        
        return MoveState(
            known=known,
            name=move_name,
            pp=pp,
            pp_max=pp_max,
            disabled=disabled
        )
    
    def decode_pokemon_state(self, encoding: np.ndarray) -> PokemonState:
        """Decode a Pokemon state from a numpy array."""
        offset = 0
        
        # Boolean flags
        active = bool(encoding[offset] > 0.5)
        known = bool(encoding[offset + 1] > 0.5)
        revealed = bool(encoding[offset + 2] > 0.5)
        in_play = bool(encoding[offset + 3] > 0.5)
        trapped = bool(encoding[offset + 4] > 0.5)
        two_turn_move = bool(encoding[offset + 5] > 0.5)
        confused = bool(encoding[offset + 6] > 0.5)
        substitute = bool(encoding[offset + 7] > 0.5)
        reflect = bool(encoding[offset + 8] > 0.5)
        light_screen = bool(encoding[offset + 9] > 0.5)
        offset += 10
        
        # Scalar values (denormalize)
        level = int(round(encoding[offset] * 100.0))
        hp = encoding[offset + 1] * 100.0  # HP is already a percentage
        sleep_turns = int(round(encoding[offset + 2] * 7.0))
        # Stat boosts: denormalize from 0-1 range back to -6 to +6
        atk_boost = int(round(encoding[offset + 3] * 12.0)) - 6
        def_boost = int(round(encoding[offset + 4] * 12.0)) - 6
        special_boost = int(round(encoding[offset + 5] * 12.0)) - 6
        speed_boost = int(round(encoding[offset + 6] * 12.0)) - 6
        offset += 7
        
        # Status (find the one-hot encoded status)
        status_encoding = encoding[offset:offset + len(Status)]
        status_idx = np.argmax(status_encoding)
        status = Status(status_idx) if status_encoding[status_idx] > 0.5 else Status.NONE
        offset += len(Status)
        
        # Species (find the one-hot encoded species)
        species: Optional[str] = None
        if known:
            species_encoding = encoding[offset:offset + self.pokemon_encoding_size]
            species_idx = np.argmax(species_encoding)
            if species_encoding[species_idx] > 0.5:
                # Find species name by index
                species_names = list(self.pokemon_to_index.keys())
                for name, idx in self.pokemon_to_index.items():
                    if idx == species_idx:
                        species = str(name)
                        break
        offset += self.pokemon_encoding_size
        
        # Type 1 (find the one-hot encoded type)
        type1: Optional[str] = None
        if known:
            type1_encoding = encoding[offset:offset + self.type_encoding_size]
            type1_idx = np.argmax(type1_encoding)
            if type1_encoding[type1_idx] > 0.5:
                type1 = dex.TYPES[type1_idx]
        offset += self.type_encoding_size
        
        # Type 2 (find the one-hot encoded type)
        type2: Optional[str] = None
        if known:
            type2_encoding = encoding[offset:offset + self.type_encoding_size]
            type2_idx = np.argmax(type2_encoding)
            if type2_encoding[type2_idx] > 0.5:
                type2 = dex.TYPES[type2_idx]
        offset += self.type_encoding_size
        
        # Moves (4 moves)
        move_size = self._calculate_move_state_size()
        move1 = self.decode_move_state(encoding[offset:offset + move_size])
        offset += move_size
        move2 = self.decode_move_state(encoding[offset:offset + move_size])
        offset += move_size
        move3 = self.decode_move_state(encoding[offset:offset + move_size])
        offset += move_size
        move4 = self.decode_move_state(encoding[offset:offset + move_size])
        
        return PokemonState(
            active=active,
            known=known,
            revealed=revealed,
            in_play=in_play,
            level=level,
            name=species,  # Using species as name for simplicity
            species=species,
            type1=type1,
            type2=type2,
            hp=hp,
            status=status,
            trapped=trapped,
            two_turn_move=two_turn_move,
            confused=confused,
            sleep_turns=sleep_turns,
            substitute=substitute,
            reflect=reflect,
            light_screen=light_screen,
            atk_boost=atk_boost,
            def_boost=def_boost,
            special_boost=special_boost,
            speed_boost=speed_boost,
            move1=move1 if move1.known else None,
            move2=move2 if move2.known else None,
            move3=move3 if move3.known else None,
            move4=move4 if move4.known else None
        )
    
    def decode_team_state(self, encoding: np.ndarray) -> TeamState:
        """Decode a team state from a numpy array."""
        pk_list = []
        
        # Decode each Pokemon in the team
        for i in range(6):  # Always decode 6 Pokemon slots
            start_idx = i * self.pokemon_state_size
            end_idx = start_idx + self.pokemon_state_size
            pokemon_encoding = encoding[start_idx:end_idx]
            pokemon = self.decode_pokemon_state(pokemon_encoding)
            pk_list.append(pokemon)
        
        # Build in_play list based on which Pokemon are marked as in_play
        in_play = [i for i, pokemon in enumerate(pk_list) if pokemon.in_play]
        
        return TeamState(pk_list=pk_list, in_play=in_play)
    
    def decode_battle_state(self, observation: np.ndarray) -> BattleState:
        """
        Decode a complete battle state from a numpy array.
        
        Args:
            observation: The numpy array representing the battle state
            
        Returns:
            A BattleState object decoded from the observation
        """
        if len(observation) != self.battle_state_size:
            raise ValueError(f"Observation size {len(observation)} does not match expected size {self.battle_state_size}")
        
        offset = 0
        
        # Active Pokemon indices (denormalize from 0-1 range)
        player_active_mon = int(round(observation[offset] * 5.0))
        opponent_active_mon = int(round(observation[offset + 1] * 5.0))
        offset += 2
        
        # Player team
        player_team_encoding = observation[offset:offset + self.team_state_size]
        player_team = self.decode_team_state(player_team_encoding)
        offset += self.team_state_size
        
        # Opponent team
        opponent_team_encoding = observation[offset:offset + self.team_state_size]
        opponent_team = self.decode_team_state(opponent_team_encoding)
        
        return BattleState(
            player_active_mon=player_active_mon,
            opponent_active_mon=opponent_active_mon,
            player_team=player_team,
            opponent_team=opponent_team
        )
    
    def get_observation_shape(self) -> tuple:
        """
        Get the shape of the observation array.
        
        Returns:
            Tuple representing the shape of the observation array
        """
        return (self.battle_state_size,)
    
    def get_observation_info(self) -> Dict[str, int]:
        """
        Get detailed information about the observation structure.
        
        Returns:
            Dictionary with information about observation dimensions
        """
        return {
            "total_size": self.battle_state_size,
            "active_indices_size": 2,
            "team_state_size": self.team_state_size,
            "pokemon_state_size": self.pokemon_state_size,
            "move_state_size": self._calculate_move_state_size(),
            "move_encoding_size": self.move_encoding_size,
            "pokemon_encoding_size": self.pokemon_encoding_size,
            "type_encoding_size": self.type_encoding_size,
            "status_encoding_size": len(Status)
        }


def create_observation_factory() -> ObservationFactory:
    """
    Create and return a new ObservationFactory instance.
    
    Returns:
        A new ObservationFactory instance
    """
    return ObservationFactory()


if __name__ == "__main__":
    # Example usage
    from src.state.pokestate import create_default_battle_state
    
    # Create factory and test with default battle state
    factory = create_observation_factory()
    battle_state = create_default_battle_state()
    
    # Get observation info
    info = factory.get_observation_info()
    print("Observation Factory Information:")
    print("=" * 50)
    for key, value in info.items():
        print(f"{key}: {value}")
    
    print(f"\nObservation shape: {factory.get_observation_shape()}")
    
    # Encode the default battle state
    observation = factory.encode_battle_state(battle_state)
    print(f"\nObservation array shape: {observation.shape}")
    print(f"Observation array dtype: {observation.dtype}")
    print(f"Non-zero elements: {np.count_nonzero(observation)}")
    print(f"Min value: {observation.min()}")
    print(f"Max value: {observation.max()}")
    
    # Test encoding/decoding round-trip
    print("\nTesting encoding/decoding round-trip:")
    decoded_state = factory.decode_battle_state(observation)
    print(f"Round-trip successful: {type(decoded_state).__name__}")
    
    # Re-encode the decoded state and compare
    re_encoded = factory.encode_battle_state(decoded_state)
    print(f"Arrays match after round-trip: {np.allclose(observation, re_encoded, atol=1e-6)}")
    
    if not np.allclose(observation, re_encoded, atol=1e-6):
        diff = np.abs(observation - re_encoded)
        max_diff = np.max(diff)
        print(f"Maximum difference: {max_diff}")
        print(f"Number of differing elements: {np.sum(diff > 1e-6)}")
    else:
        print("Perfect round-trip encoding/decoding!")
    
    print("\nObservationFactory with encode/decode functionality completed successfully!")
