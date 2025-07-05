from src.params.yaml_parser import load_battle_state_from_yaml

from src.state.pokestate import BattleState

def create_sample_yaml() -> str:
    """
    Create a sample YAML configuration string for testing.
    
    Returns:
        Sample YAML configuration as a string
    """
    sample_yaml = """
Team 1:
  - species: "Charizard"
    nickname: "Blaze"
    level: 50
    moves:
      - "Fire Blast"
      - "Earthquake"
      - "Fire Spin"
      - "Slash"
  - species: "Blastoise"
    nickname: "Hydro"
    level: 50
    moves:
      - "Hydro Pump"
      - "Ice Beam"
      - "Earthquake"
      - "Body Slam"
  - species: "Venusaur"
    nickname: "Chloro"
    level: 50
    moves:
      - "Solar Beam"
      - "Sleep Powder"
      - "Body Slam"
      - "Leech Seed"
  - species: "Pikachu"
    nickname: "Sparky"
    level: 50
    moves:
      - "Thunderbolt"
      - "Double Kick"
      - "Seismic Toss"
      - "Thunder Wave"
  - species: "Alakazam"
    nickname: "Psycho"
    level: 50
    moves:
      - "Psychic"
      - "Thunder Wave"
      - "Recover"
      - "Substitute"
  - species: "Machamp"
    nickname: "Muscle"
    level: 50
    moves:
      - "Submission"
      - "Earthquake"
      - "Rock Slide"
      - "Body Slam"

Team 2:
  - species: "Dragonite"
    nickname: "Dragon"
    level: 50
    moves:
      - "Blizzard"
      - "Thunder"
      - "Hyper Beam"
      - "Body Slam"
  - species: "Gengar"
    nickname: "Ghost"
    level: 50
    moves:
      - "Psychic"
      - "Thunderbolt"
      - "Explosion"
      - "Hypnosis"
  - species: "Lapras"
    nickname: "Surf"
    level: 50
    moves:
      - "Ice Beam"
      - "Thunderbolt"
      - "Psychic"
      - "Body Slam"
  - species: "Snorlax"
    nickname: "Tank"
    level: 50
    moves:
      - "Body Slam"
      - "Rest"
      - "Substitute"
      - "Earthquake"
  - species: "Starmie"
    nickname: "Star"
    level: 50
    moves:
      - "Psychic"
      - "Thunderbolt"
      - "Ice Beam"
      - "Recover"
  - species: "Tauros"
    nickname: "Bull"
    level: 50
    moves:
      - "Body Slam"
      - "Hyper Beam"
      - "Earthquake"
      - "Blizzard"
"""
    return sample_yaml.strip()


def save_sample_yaml_file(filename: str = "sample_battle.yaml") -> None:
    """
    Save a sample YAML configuration to a file.
    
    Args:
        filename: Name of the file to save
    """
    sample_yaml = create_sample_yaml()
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(sample_yaml)
    print(f"Sample YAML saved to {filename}")


if __name__ == "__main__":
    # Example usage
    print("YAML Parser for Pokemon Stadium AI")
    print("=" * 40)
    
    # Create and save a sample YAML file
    sample_filename = "sample_battle.yaml"
    save_sample_yaml_file(sample_filename)
    
    # Load the sample YAML and create a BattleState
    try:
        battle_state = load_battle_state_from_yaml(sample_filename)
        print(f"\nSuccessfully loaded BattleState from {sample_filename}")
        print(f"Player team: {len(battle_state.player_team.pk_list)} Pokemon")
        print(f"Opponent team: {len(battle_state.opponent_team.pk_list)} Pokemon")
        print(f"Active player Pokemon: {battle_state.player_team.pk_list[0].species}")
        print(f"Active opponent Pokemon: {battle_state.opponent_team.pk_list[0].species}")
        
        # Test numpy conversion
        numpy_array = battle_state.to_numpy()
        print(f"BattleState numpy array shape: {numpy_array.shape}")
        
        # Test conversion back from numpy
        reconstructed_state = BattleState.from_numpy(numpy_array)
        print(f"Successfully reconstructed BattleState from numpy array")
        
    except Exception as e:
        print(f"Error: {e}")