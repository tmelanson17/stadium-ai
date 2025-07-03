"""
Example usage of the battle message parsing and state updating system.
"""
import numpy as np
from src.state.pokestate import BattleState, TeamState, PokemonState, MoveState
from src.state_reader.phrases import Messages, parse_update_message
from src.state_reader.state_updater import enact_changes


def create_example_battle_state() -> BattleState:
    """Create an example battle state for testing."""
    
    # Create example moves
    move1 = MoveState(known=True, name="Tackle", pp=20, pp_max=20, disabled=False)
    move2 = MoveState(known=True, name="Thunderbolt", pp=15, pp_max=15, disabled=False)
    
    # Create example Pokemon
    player_pokemon = PokemonState(
        active=True,
        known=True,
        name="Pikachu",
        species="Pikachu",
        type1="Electric",
        hp=85.0,
        move1=move1,
        move2=move2
    )
    
    opponent_pokemon = PokemonState(
        active=True,
        known=True,
        name="Charmander",
        species="Charmander",
        type1="Fire",
        hp=90.0,
        move1=move1
    )

    opponent_bench_pokemon = PokemonState(
        active=False,
        known=False,
        name="SquadGoals",
        species="Squirtle",
        type1="Water",
        hp=100.0,
    )
    
    # Create teams
    player_team = TeamState(pk_list=[player_pokemon] + [PokemonState() for _ in range(5)])
    opponent_team = TeamState(pk_list=[opponent_pokemon, opponent_bench_pokemon] + [PokemonState() for _ in range(5)])
    
    return BattleState(
        player_active_mon=0,
        opponent_active_mon=0,
        player_team=player_team,
        opponent_team=opponent_team
    )


def demonstrate_message_parsing():
    """Demonstrate how message parsing and state updates work."""
    
    print("=== Battle Message Parsing and State Update Demo ===\n")
    
    # Create example battle state
    battle_state = create_example_battle_state()
    
    # Display initial state
    print("Initial State:")
    player_pokemon = battle_state.player_team.pk_list[battle_state.player_active_mon]
    opponent_pokemon = battle_state.opponent_team.pk_list[battle_state.opponent_active_mon]
    
    print(f"Player Pokemon: {player_pokemon.name}")
    print(f"  HP: {player_pokemon.hp}%")
    print(f"  Status: {player_pokemon.status}")
    print(f"  Confused: {player_pokemon.confused}")
    print(f"  Attack Boost: {player_pokemon.atk_boost}")
    
    print(f"\nOpponent Pokemon: {opponent_pokemon.name}")
    print(f"  HP: {opponent_pokemon.hp}%")
    print(f"  Status: {opponent_pokemon.status}")
    print(f"  Confused: {opponent_pokemon.confused}")
    print(f"  Attack Boost: {opponent_pokemon.atk_boost}")
    
    # Example 1: Player's Pokemon gets confused
    print("\n--- Example 1: Player's Pokemon becomes confused ---")
    confused_inexact = "It becom3 c?nsused!"
    changes = parse_update_message(confused_inexact, battle_state, opponent=True)
    print(f"Parsed changes: {changes}")
    enact_changes(battle_state, changes, opponent=True)
    
    print(f"After confusion:")
    print(f"  Player Pokemon confused: {player_pokemon.confused}")
    print(f"  Opponent Pokemon confused: {opponent_pokemon.confused}")
    
    # Example 2: Player's Pokemon attack increases
    print("\n--- Example 2: Player's Pokemon attack increases ---")
    attack_increase_message = "ATACK incr@ase?!"
    changes = parse_update_message(attack_increase_message, battle_state, opponent=False)
    print(f"Parsed changes: {changes}")
    enact_changes(battle_state, changes, opponent=False)
    
    print(f"After attack boost:")
    print(f"  Player Pokemon attack boost: {player_pokemon.atk_boost}")
    print(f"  Opponent Pokemon attack boost: {opponent_pokemon.atk_boost}")
    
    # Example 3: Opponent's Pokemon gets burned
    print("\n--- Example 3: Opponent's Pokemon gets burned ---")
    burn_message = "Il was buoned!"
    changes = parse_update_message(burn_message, battle_state, opponent=False)
    print(f"Parsed changes: {changes}")
    enact_changes(battle_state, changes, opponent=False)
    
    print(f"After burn:")
    print(f"  Player Pokemon status: {player_pokemon.status}")
    print(f"  Opponent Pokemon status: {opponent_pokemon.status}")

    # Example 4: Charmander switches out to Squirtle
    print("\n--- Example 4: Opponent's Pokemon switches out ---")
    switch_message = "Go, SquudGo0ls!"
    changes = parse_update_message(switch_message, battle_state, opponent=True)
    print(f"Parsed changes: {changes}")
    enact_changes(battle_state, changes, opponent=True)
    
    print(f"After switch:")
    print(f"  Player active pokemon: {battle_state.player_team.pk_list[battle_state.player_active_mon].name}")
    print(f"  Opponent active pokemon: {battle_state.opponent_team.pk_list[battle_state.opponent_active_mon].name}")


if __name__ == "__main__":
    demonstrate_message_parsing()
