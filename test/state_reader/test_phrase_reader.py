"""
Example usage of the battle message parsing and state updating system.
"""
import numpy as np
from src.state.pokestate import BattleState, TeamState, PokemonState, MoveState
from src.state_reader.phrases import Messages, parse_update_message
from src.state_reader.state_updater import enact_changes

from test.state_reader.test_utils import create_example_battle_state


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
