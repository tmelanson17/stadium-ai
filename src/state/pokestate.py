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

    @staticmethod
    def length() -> int:
        return 4 + len(moves.GEN1_MOVES)
    
        
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
    # TODO: Convert to % when encoding for AI
    hp: int = 0 # Current HP of the Pokemon 
    hp_max: int = 0 # Max HP of the Pokemon
    status: Status = Status.NONE # Status condition of the Pokemon
    trapped: bool = False # Volatile conditions (listed one at a time)
    two_turn_move: bool = False # Whether the Pokemon is currently using a two-turn move
    confused: bool = False # Whether the Pokemon is currently confused
    sleep_turns: int = 0 # Number of turns asleep (0 if not asleep)
    substitute : bool = False # Whether the Pokemon has a substitute active
    reflect: bool = False # Gen 1 reflect
    light_screen: bool = False # Gen 1 light screen
    atk_boost : int = 0 # Number of boosts / debuffs
    def_boost : int = 0
    special_boost : int = 0
    speed_boost: int = 0 
    move1: Optional[MoveState] = None
    move2: Optional[MoveState] = None
    move3: Optional[MoveState] = None
    move4: Optional[MoveState] = None


    @staticmethod
    def length() -> int:
        return 18 + MoveState.length() * 4 + len(dex.GEN1_POKEMON) + len(dex.TYPES)
    

@dataclass
class TeamState:
    # List of Pokemon brought to the battle
    pk_list: List[PokemonState]

    # List of indices of Pokemon chosen in team preview, in the order they were selected
    in_play: List[int] 

    def length(self) -> int:
        return len(self.pk_list) * PokemonState.length()


@dataclass
class BattleState:
    player_active_mon: int # Index of active mon
    opponent_active_mon: int # Index of opponent active mon
    player_team: TeamState
    opponent_team: TeamState

    def get_player_active_mon(self) -> PokemonState:
        return self.player_team.pk_list[self.player_active_mon]

    def get_opponent_active_mon(self) -> PokemonState:
        return self.opponent_team.pk_list[self.opponent_active_mon]


    def length(self):
        return 2 + self.player_team.length() + self.opponent_team.length()
    

def create_default_battle_state() -> BattleState:
    """
    Create a default BattleState with empty teams and no active Pokemon.
    
    Returns:
        BattleState with empty teams and no active Pokemon.
    """
    return BattleState(
        player_active_mon=0,
        opponent_active_mon=0,
        player_team=TeamState(in_play=[], pk_list=[PokemonState() for _ in range(6)]),
        opponent_team=TeamState(in_play=[], pk_list=[PokemonState() for _ in range(6)])
    )

def print_battle_state(battle_state: BattleState, title: str = "Battle State") -> None:
    """
    Print the BattleState in a clear, formatted way for debugging and visualization.
    
    Args:
        battle_state: The BattleState to print
        title: Optional title for the printout
    """
    print("=" * 80)
    print(f"{title:^80}")
    print("=" * 80)
    
    def print_pokemon(pokemon: PokemonState, slot: int, is_active: bool = False) -> None:
        """Helper function to print a single Pokemon's state"""
        status_indicator = "🔴" if is_active else "⚪"
        species_name = pokemon.species or "Unknown"
        level_str = f"Lv.{pokemon.level}" if pokemon.level > 0 else "Lv.?"

        # Format HP with one decimal place, ensuring one digit before the decimal
        hp_str = f"{pokemon.hp:.1f}%" if pokemon.hp > 0 else "0.0%"
        
        # Status condition emoji
        status_emoji = {
            Status.NONE: "",
            Status.BURNED: "🔥",
            Status.FROZEN: "🧊", 
            Status.PARALYZED: "⚡",
            Status.POISONED: "☠️",
            Status.SLEEP: "💤",
            Status.FAINTED: "💀"
        }.get(pokemon.status, "")
        
        print(f"  {status_indicator} Slot {slot+1}: {species_name} {level_str} - HP: {hp_str} {status_emoji}")
        
        if pokemon.known and (pokemon.move1 or pokemon.move2 or pokemon.move3 or pokemon.move4):
            moves = []
            for move in [pokemon.move1, pokemon.move2, pokemon.move3, pokemon.move4]:
                if move and move.known and move.name:
                    pp_str = f"({move.pp}/{move.pp_max})"
                    disabled_str = " [DISABLED]" if move.disabled else ""
                    moves.append(f"{move.name} {pp_str}{disabled_str}")
            if moves:
                print(f"    Moves: {' | '.join(moves)}")
        
        # Show stat boosts if any
        boosts = []
        if pokemon.atk_boost != 0:
            boosts.append(f"Atk: {pokemon.atk_boost:+d}")
        if pokemon.def_boost != 0:
            boosts.append(f"Def: {pokemon.def_boost:+d}")
        if pokemon.special_boost != 0:
            boosts.append(f"Spc: {pokemon.special_boost:+d}")
        if pokemon.speed_boost != 0:
            boosts.append(f"Spd: {pokemon.speed_boost:+d}")
        if boosts:
            print(f"    Stat Boosts: {' | '.join(boosts)}")
            
        # Show conditions
        conditions = []
        if pokemon.trapped:
            conditions.append("Trapped")
        if pokemon.confused:
            conditions.append("Confused")
        if pokemon.substitute:
            conditions.append("Substitute")
        if pokemon.reflect:
            conditions.append("Reflect")
        if pokemon.light_screen:
            conditions.append("Light Screen")
        if pokemon.two_turn_move:
            conditions.append("Two-turn Move")
        if pokemon.sleep_turns > 0:
            conditions.append(f"Sleep ({pokemon.sleep_turns} turns)")
        if conditions:
            print(f"    Conditions: {' | '.join(conditions)}")
    
    # Player team
    print("\n🔵 PLAYER TEAM:")
    print("-" * 40)
    for i, pokemon in enumerate(battle_state.player_team.pk_list):
        is_active = (i == battle_state.player_active_mon)
        print_pokemon(pokemon, i, is_active)
    
    # Opponent team  
    print("\n🔴 OPPONENT TEAM:")
    print("-" * 40)
    for i, pokemon in enumerate(battle_state.opponent_team.pk_list):
        is_active = (i == battle_state.opponent_active_mon)
        print_pokemon(pokemon, i, is_active)
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    state = create_default_battle_state()
    print_battle_state(state, "Default Battle State")
    
    # Example with some data
    state.player_team.pk_list[0].species = "Charizard"
    state.player_team.pk_list[0].level = 50
    state.player_team.pk_list[0].hp = 85.5
    state.player_team.pk_list[0].status = Status.BURNED
    state.player_team.pk_list[0].known = True
    state.player_team.pk_list[0].move1 = MoveState(known=True, name="Flamethrower", pp=15, pp_max=15, disabled=False)
    
    state.opponent_team.pk_list[0].species = "Blastoise"
    state.opponent_team.pk_list[0].level = 50
    state.opponent_team.pk_list[0].hp = 92.3
    state.opponent_team.pk_list[0].known = True
    
    print_battle_state(state, "Example Battle State")