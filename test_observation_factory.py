"""
Test script for the ObservationFactory to demonstrate encoding/decoding of battle states with actual data.
"""

import numpy as np
from src.state.observation_factory import create_observation_factory
from src.state.pokestate import (
    create_default_battle_state, 
    BattleState, 
    PokemonState, 
    MoveState,
    print_battle_state
)
from src.state.pokestate_defs import Status


def create_test_battle_state() -> BattleState:
    """Create a battle state with some example data for testing."""
    battle_state = create_default_battle_state()
    
    # Player's active Pokemon (Charizard)
    player_char = battle_state.player_team.pk_list[0]
    player_char.active = True
    player_char.known = True
    player_char.revealed = True
    player_char.in_play = True
    player_char.level = 50
    player_char.species = "Charizard"
    player_char.type1 = "Fire"
    player_char.type2 = "Flying"
    player_char.hp = 85.5
    player_char.status = Status.NONE
    player_char.atk_boost = 1
    player_char.def_boost = 0
    player_char.special_boost = -1
    player_char.speed_boost = 0
    
    # Player's Charizard moves
    player_char.move1 = MoveState(known=True, name="Flamethrower", pp=15, pp_max=15, disabled=False)
    player_char.move2 = MoveState(known=True, name="Earthquake", pp=10, pp_max=10, disabled=False)
    player_char.move3 = MoveState(known=True, name="Slash", pp=20, pp_max=20, disabled=False)
    player_char.move4 = MoveState(known=True, name="Fire Blast", pp=5, pp_max=5, disabled=False)
    
    # Player's second Pokemon (Blastoise)
    player_blast = battle_state.player_team.pk_list[1]
    player_blast.known = True
    player_blast.revealed = False
    player_blast.in_play = True
    player_blast.level = 50
    player_blast.species = "Blastoise"
    player_blast.type1 = "Water"
    player_blast.hp = 100.0
    player_blast.status = Status.NONE
    
    # Opponent's active Pokemon (Venusaur)
    opponent_venus = battle_state.opponent_team.pk_list[0]
    opponent_venus.active = True
    opponent_venus.known = True
    opponent_venus.revealed = True
    opponent_venus.in_play = True
    opponent_venus.level = 50
    opponent_venus.species = "Venusaur"
    opponent_venus.type1 = "Grass"
    opponent_venus.type2 = "Poison"
    opponent_venus.hp = 67.2
    opponent_venus.status = Status.POISONED
    opponent_venus.confused = True
    opponent_venus.substitute = True
    
    # Opponent's Venusaur moves (partially known)
    opponent_venus.move1 = MoveState(known=True, name="Razor Leaf", pp=25, pp_max=25, disabled=False)
    opponent_venus.move2 = MoveState(known=True, name="Sleep Powder", pp=15, pp_max=15, disabled=True)
    opponent_venus.move3 = MoveState(known=False, name=None, pp=0, pp_max=0, disabled=False)
    opponent_venus.move4 = MoveState(known=False, name=None, pp=0, pp_max=0, disabled=False)
    
    # Set active Pokemon indices
    battle_state.player_active_mon = 0
    battle_state.opponent_active_mon = 0
    
    return battle_state


def analyze_observation(observation: np.ndarray, factory) -> None:
    """Analyze and print information about the observation array."""
    print("\nObservation Analysis:")
    print("=" * 50)
    print(f"Total observation size: {len(observation)}")
    print(f"Non-zero elements: {np.count_nonzero(observation)}")
    print(f"Percentage non-zero: {np.count_nonzero(observation) / len(observation) * 100:.2f}%")
    print(f"Min value: {observation.min():.3f}")
    print(f"Max value: {observation.max():.3f}")
    print(f"Mean value: {observation.mean():.6f}")
    print(f"Standard deviation: {observation.std():.6f}")
    
    # Show which sections have data
    info = factory.get_observation_info()
    offset = 0
    
    # Active Pokemon indices
    active_section = observation[offset:offset + 2]
    print(f"\nActive Pokemon indices: {active_section}")
    offset += 2
    
    # Player team section
    player_section = observation[offset:offset + info['team_state_size']]
    player_nonzero = np.count_nonzero(player_section)
    print(f"Player team non-zero elements: {player_nonzero}/{info['team_state_size']}")
    offset += info['team_state_size']
    
    # Opponent team section
    opponent_section = observation[offset:offset + info['team_state_size']]
    opponent_nonzero = np.count_nonzero(opponent_section)
    print(f"Opponent team non-zero elements: {opponent_nonzero}/{info['team_state_size']}")


def compare_battle_states(original: BattleState, decoded: BattleState) -> None:
    """Compare original and decoded battle states for differences."""
    print("\nBattle State Comparison:")
    print("=" * 50)
    
    # Compare active indices
    print(f"Player active mon: {original.player_active_mon} -> {decoded.player_active_mon}")
    print(f"Opponent active mon: {original.opponent_active_mon} -> {decoded.opponent_active_mon}")
    
    # Compare player team
    print("\nPlayer Team Comparison:")
    for i, (orig_pk, dec_pk) in enumerate(zip(original.player_team.pk_list, decoded.player_team.pk_list)):
        if orig_pk.known or dec_pk.known:
            print(f"  Slot {i+1}: {orig_pk.species} -> {dec_pk.species}")
            if orig_pk.known and dec_pk.known:
                print(f"    Level: {orig_pk.level} -> {dec_pk.level}")
                print(f"    HP: {orig_pk.hp:.1f}% -> {dec_pk.hp:.1f}%")
                print(f"    Status: {orig_pk.status.name} -> {dec_pk.status.name}")
                if orig_pk.atk_boost != 0 or dec_pk.atk_boost != 0:
                    print(f"    Atk boost: {orig_pk.atk_boost} -> {dec_pk.atk_boost}")
    
    # Compare opponent team
    print("\nOpponent Team Comparison:")
    for i, (orig_pk, dec_pk) in enumerate(zip(original.opponent_team.pk_list, decoded.opponent_team.pk_list)):
        if orig_pk.known or dec_pk.known:
            print(f"  Slot {i+1}: {orig_pk.species} -> {dec_pk.species}")
            if orig_pk.known and dec_pk.known:
                print(f"    Level: {orig_pk.level} -> {dec_pk.level}")
                print(f"    HP: {orig_pk.hp:.1f}% -> {dec_pk.hp:.1f}%")
                print(f"    Status: {orig_pk.status.name} -> {dec_pk.status.name}")
                print(f"    Confused: {orig_pk.confused} -> {dec_pk.confused}")
                print(f"    Substitute: {orig_pk.substitute} -> {dec_pk.substitute}")


def test_encoding_decoding():
    """Test the observation factory with various battle states."""
    print("Testing ObservationFactory Encoding and Decoding")
    print("=" * 80)
    
    # Create factory
    factory = create_observation_factory()
    
    # Test with default empty battle state
    print("\n1. Testing with empty battle state:")
    empty_state = create_default_battle_state()
    empty_obs = factory.encode_battle_state(empty_state)
    analyze_observation(empty_obs, factory)
    
    # Test decoding empty state
    decoded_empty = factory.decode_battle_state(empty_obs)
    print(f"Empty state round-trip successful: {type(decoded_empty).__name__}")
    
    # Test with populated battle state
    print("\n\n2. Testing with populated battle state:")
    test_state = create_test_battle_state()
    print_battle_state(test_state, "Original Test Battle State")
    
    test_obs = factory.encode_battle_state(test_state)
    analyze_observation(test_obs, factory)
    
    # Test decoding populated state
    print("\n\n3. Testing decoding of populated state:")
    decoded_test = factory.decode_battle_state(test_obs)
    print_battle_state(decoded_test, "Decoded Test Battle State")
    
    # Compare original and decoded states
    compare_battle_states(test_state, decoded_test)
    
    # Test observation consistency
    print("\n\n4. Testing round-trip consistency:")
    obs1 = factory.encode_battle_state(test_state)
    decoded = factory.decode_battle_state(obs1)
    obs2 = factory.encode_battle_state(decoded)
    
    print(f"Identical encodings after round-trip: {np.array_equal(obs1, obs2)}")
    print(f"Close encodings after round-trip: {np.allclose(obs1, obs2, atol=1e-6)}")
    
    if not np.allclose(obs1, obs2, atol=1e-6):
        diff = np.abs(obs1 - obs2)
        max_diff = np.max(diff)
        print(f"Maximum difference: {max_diff}")
        print(f"Number of differing elements: {np.sum(diff > 1e-6)}")
        
        # Show some differing elements
        diff_indices = np.where(diff > 1e-6)[0]
        if len(diff_indices) > 0:
            print(f"First few differences at indices: {diff_indices[:5]}")
            for idx in diff_indices[:3]:
                print(f"  Index {idx}: {obs1[idx]:.6f} -> {obs2[idx]:.6f}")
    
    print("\n\nObservationFactory encoding/decoding test completed successfully!")


if __name__ == "__main__":
    test_encoding_decoding()
