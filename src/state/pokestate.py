from dataclasses import dataclass
import enum
from typing import Optional, List

import numpy as np
import src.state.gen1_moves as moves
import src.state.gen1_dex as dex
from src.state.pokestate_defs import Status

@dataclass
class MoveState:
    known : bool
    name : Optional[str]
    pp : int
    pp_max : int
    disabled : bool

    def insert_numpy(self, result: np.ndarray, start_idx: int = 0):
        result[start_idx] = 1 if self.known else 0
        result[start_idx + 1] = self.pp
        result[start_idx + 2] = self.pp_max
        result[start_idx + 3] = 1 if self.disabled else 0
        if self.name is not None:
            result[start_idx + 4 + moves.get_move_index_by_name(self.name)] = 1

    def to_numpy(self) -> np.ndarray:
        result = np.zeros(4 + len(moves.GEN1_MOVES), dtype=np.float32)
        self.insert_numpy(result)
        return result

    @staticmethod
    def length() -> int:
        return 4 + len(moves.GEN1_MOVES)
    
        
    @staticmethod
    def from_numpy(obs: np.ndarray, start_idx: int = 0) -> 'MoveState':
        """
        Convert a numpy observation array section back into a MoveState
        
        Args:
            obs: Numpy observation array
            start_idx: Starting index for this MoveState in the array
            
        Returns:
            MoveState object reconstructed from the array
        """
        known = bool(obs[start_idx] > 0.5)  # Convert from float to bool with threshold
        pp = int(obs[start_idx + 1])
        pp_max = int(obs[start_idx + 2])
        disabled = bool(obs[start_idx + 3] > 0.5)
        
        # Find the move name by checking which index is set
        name = None
        if known:
            move_indices = obs[start_idx + 4:start_idx + 4 + len(moves.GEN1_MOVES)]
            if np.any(move_indices > 0.5):
                move_idx = np.argmax(move_indices)
                name = moves.get_move_name_by_index(move_idx)
        return MoveState(
            known=known,
            name=name,
            pp=pp,
            pp_max=pp_max,
            disabled=disabled
        )

@dataclass
class PokemonState:
    active: bool = False # Whether the pokemon is currently active in battle
    known: bool = False # Whether the Pokemon in this slot is known to the opponent
    revealed: bool = False # Whether the Pokemon in this slot has been revealed to the opponent
    in_play: bool = False # True if brought to the battle
    level: int = 0 # Level of the Pokemon
    name: Optional[str] = None # Nickname
    species: Optional[str] = None # Species name
    type1: Optional[str] = None # Species type 1,2
    type2: Optional[str] = None
    hp: float = 0.0 # Current HP of the Pokemon (%)
    status: Status = Status.NONE # Status condition of the Pokemon
    trapped: bool = False # Volatile conditions (listed one at a time)
    two_turn_move: bool = False # Whether the Pokemon is currently using a two-turn move
    confused: bool = False # Whether the Pokemon is currently confused
    sleep_turns: int = 0 # Number of turns asleep (0 if not asleep)
    substitute : bool = False # Whether the Pokemon has a substitute active
    atk_boost : int = 0 # Number of boosts / debuffs
    def_boost : int = 0
    special_boost : int = 0
    speed_boost: int = 0 
    move1: Optional[MoveState] = None
    move2: Optional[MoveState] = None
    move3: Optional[MoveState] = None
    move4: Optional[MoveState] = None

    def insert_numpy(self, result: np.ndarray, start_idx: int = 0):
        result[start_idx] = 1 if self.active else 0
        result[start_idx + 1] = 1 if self.known else 0
        result[start_idx + 2] = 1 if self.revealed else 0
        result[start_idx + 3] = 1 if self.in_play else 0
        result[start_idx + 4] = self.level
        result[start_idx + 5] = (self.hp * 255) // 100  # Scale HP to 0-255 range
        result[start_idx + 6] = self.status.value
        result[start_idx + 7] = 1 if self.trapped else 0
        result[start_idx + 8] = 1 if self.two_turn_move else 0
        result[start_idx + 9] = 1 if self.confused else 0
        result[start_idx + 10] = self.sleep_turns
        result[start_idx + 11] = 1 if self.substitute else 0
        result[start_idx + 12] = self.atk_boost
        result[start_idx + 13] = self.def_boost
        result[start_idx + 14] = self.special_boost
        result[start_idx + 15] = self.speed_boost
        if self.species:
            result[start_idx + 16 + dex.get_species_index_by_name(self.species)] = 1
        if self.type1:
            result[start_idx + 16 + len(dex.GEN1_POKEMON) + dex.get_type_index_by_name(self.type1)] = 1
        if self.type2:
            result[start_idx + 16 + len(dex.GEN1_POKEMON) + dex.get_type_index_by_name(self.type2)] = 1
        

        if self.move1:
            self.move1.insert_numpy(result, start_idx + 16 + len(dex.GEN1_POKEMON) + len(dex.TYPES))
        if self.move2:
            self.move2.insert_numpy(result, start_idx + 16 + len(dex.GEN1_POKEMON) + len(dex.TYPES) + MoveState.length())
        if self.move3:
            self.move3.insert_numpy(result, start_idx + 16 + len(dex.GEN1_POKEMON) + len(dex.TYPES) + MoveState.length()*2)
        if self.move4:
            self.move4.insert_numpy(result, start_idx + 16 + len(dex.GEN1_POKEMON) + len(dex.TYPES) + MoveState.length()*3)

    def to_numpy(self) -> np.ndarray:
        result = np.zeros(PokemonState.length(), dtype=np.float32)
        self.insert_numpy(result)
        return result
    
    @staticmethod
    def length() -> int:
        return 16 + MoveState.length() * 4 + len(dex.GEN1_POKEMON) + len(dex.TYPES)
    
    @staticmethod
    def from_numpy(obs: np.ndarray, start_idx: int = 0) -> 'PokemonState':
        """
        Convert a numpy observation array section back into a PokemonState
        
        Args:
            obs: Numpy observation array
            start_idx: Starting index for this PokemonState in the array
            
        Returns:
            PokemonState object reconstructed from the array
        """
        active = bool(obs[start_idx] > 0.5)
        known = bool(obs[start_idx + 1] > 0.5)
        revealed = bool(obs[start_idx + 2] > 0.5)
        in_play = bool(obs[start_idx + 3] > 0.5)
        level = int(obs[start_idx + 4])
        hp = float(obs[start_idx + 5]) * (100/255)  # Convert back to percentage
        status_value = int(obs[start_idx + 6])
        status = Status(status_value) if 0 <= status_value <= 6 else Status.NONE
        trapped = bool(obs[start_idx + 7] > 0.5)
        two_turn_move = bool(obs[start_idx + 8] > 0.5)
        confused = bool(obs[start_idx + 9] > 0.5)
        sleep_turns = int(obs[start_idx + 10])
        substitute = bool(obs[start_idx + 11] > 0.5)
        atk_boost = int(obs[start_idx + 12])
        def_boost = int(obs[start_idx + 13])
        special_boost = int(obs[start_idx + 14])
        speed_boost = int(obs[start_idx + 15])
        
        # Get species
        species = None
        species_indices = obs[start_idx + 16:start_idx + 16 + len(dex.GEN1_POKEMON)]
        if np.any(species_indices > 0.5):
            species_idx = np.argmax(species_indices)
            species = dex.get_species_name_by_index(species_idx)
            
        # Get types
        type1 = None
        type2 = None
        type_offset = start_idx + 16 + len(dex.GEN1_POKEMON)
        type_indices = obs[type_offset:type_offset + len(dex.TYPES)]
        type_max_indices = np.where(type_indices > 0.5)[0]
        if len(type_max_indices) >= 1:
            type1 = dex.get_type_name_by_index(type_max_indices[0])
        if len(type_max_indices) >= 2:
            type2 = dex.get_type_name_by_index(type_max_indices[1])
            
        # Get moves
        move_offset = start_idx + 16 + len(dex.GEN1_POKEMON) + len(dex.TYPES)
        move1 = MoveState.from_numpy(obs, move_offset)
        move2 = MoveState.from_numpy(obs, move_offset + MoveState.length())
        move3 = MoveState.from_numpy(obs, move_offset + MoveState.length() * 2)
        move4 = MoveState.from_numpy(obs, move_offset + MoveState.length() * 3)
        
        return PokemonState(
            active=active,
            known=known,
            revealed=revealed,
            in_play=in_play,
            level=level,
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
            atk_boost=atk_boost,
            def_boost=def_boost,
            special_boost=special_boost,
            speed_boost=speed_boost,
            move1=move1,
            move2=move2,
            move3=move3,
            move4=move4
        )


@dataclass
class TeamState:
    pk_list: List[PokemonState]

    def insert_numpy(self, result: np.ndarray, start_idx: int = 0):
        for i, pk in enumerate(self.pk_list):
            pk.insert_numpy(result, start_idx + i * PokemonState.length())

    def to_numpy(self) -> np.ndarray:
        result = np.zeros(self.length(), dtype=np.float32)
        self.insert_numpy(result)
        return result
    
    def length(self) -> int:
        return len(self.pk_list) * PokemonState.length()

        
    @staticmethod
    def from_numpy(obs: np.ndarray, start_idx: int = 0, team_size: int = 6) -> 'TeamState':
        """
        Convert a numpy observation array section back into a TeamState
        
        Args:
            obs: Numpy observation array
            start_idx: Starting index for this TeamState in the array
            team_size: Number of Pokemon in the team
            
        Returns:
            TeamState object reconstructed from the array
        """
        pokemon_list = []
        for i in range(team_size):
            pokemon_idx = start_idx + i * PokemonState.length()
            pokemon = PokemonState.from_numpy(obs, pokemon_idx)
            pokemon_list.append(pokemon)
            
        return TeamState(pk_list=pokemon_list)


@dataclass
class BattleState:
    player_active_mon: int # Index of active mon
    opponent_active_mon: int # Index of opponent active mon
    player_team: TeamState
    opponent_team: TeamState


    def insert_numpy(self, result: np.ndarray, start_idx: int = 0):
        result[start_idx+1] = self.player_active_mon
        result[start_idx+2] = self.opponent_active_mon
        self.player_team.insert_numpy(result, start_idx+3)
        self.opponent_team.insert_numpy(result, start_idx+3+self.player_team.length())


    def to_numpy(self) -> np.ndarray:
        result = np.zeros(self.length(), dtype=np.float32)
        self.insert_numpy(result, 0)
        return result


    def length(self):
        return 2 + self.player_team.length() + self.opponent_team.length()
    

    @staticmethod
    def from_numpy(obs: np.ndarray, start_idx: int = 0, team_size: int = 6) -> 'BattleState':
        """
        Convert a numpy observation array back into a BattleState
        
        Args:
            obs: Numpy observation array
            start_idx: Starting index for this BattleState in the array
            team_size: Number of Pokemon in each team
            
        Returns:
            BattleState object reconstructed from the array
        """
        player_active_mon = int(obs[start_idx+1])
        opponent_active_mon = int(obs[start_idx+2])
        
        player_team_idx = start_idx + 3
        player_team = TeamState.from_numpy(obs, player_team_idx, team_size)
        
        opponent_team_idx = start_idx + 3 + team_size * PokemonState.length()
        opponent_team = TeamState.from_numpy(obs, opponent_team_idx, team_size)
        
        return BattleState(
            player_active_mon=player_active_mon,
            opponent_active_mon=opponent_active_mon,
            player_team=player_team,
            opponent_team=opponent_team
        )


if __name__ == "__main__":
    # TODO: Create a default BattleState with example teams / mons
    state = BattleState(    
        player_active_mon=0,
        opponent_active_mon=0,
        player_team=TeamState(pk_list=[PokemonState() for _ in range(6)]),
        opponent_team=TeamState(pk_list=[PokemonState() for _ in range(6)])
    )