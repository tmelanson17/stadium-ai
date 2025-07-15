import cv2
import numpy as np
from typing import Tuple, Optional

from src.state.pokestate import BattleState, PokemonState, MoveState
from src.state.pokestate_defs import Status


def draw_battle_state(battle_state: BattleState, width: int = 1200, height: int = 800) -> np.ndarray:
    """
    Draw a BattleState using OpenCV with two columns, one for each player.
    
    Args:
        battle_state: The BattleState to visualize
        width: Width of the output image
        height: Height of the output image
        
    Returns:
        numpy array representing the drawn image
    """
    # Create blank image
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img.fill(240)  # Light gray background
    
    # Define colors
    colors = {
        'player_bg': (220, 255, 220),      # Light green
        'opponent_bg': (220, 220, 255),    # Light blue
        'active_border': (0, 255, 0),     # Green for active
        'inactive_border': (128, 128, 128), # Gray for inactive
        'text': (0, 0, 0),                # Black text
        'hp_bar_bg': (200, 200, 200),     # Gray HP background
        'hp_bar_full': (0, 255, 0),       # Green HP
        'hp_bar_medium': (255, 255, 0),   # Yellow HP
        'hp_bar_low': (0, 0, 255),        # Red HP
        'status_bg': (255, 255, 0),       # Yellow status background
        'move_bg': (240, 240, 240),       # Light gray move background
        'header_bg': (100, 100, 100),     # Dark gray headers
        'header_text': (255, 255, 255)    # White header text
    }
    
    # Layout constants
    margin = 20
    column_width = (width - 3 * margin) // 2
    header_height = 50
    active_section_height = 300
    team_section_start = header_height + active_section_height + margin
    
    # Draw column backgrounds
    cv2.rectangle(img, (margin, 0), (margin + column_width, height), colors['player_bg'], -1)
    cv2.rectangle(img, (2 * margin + column_width, 0), (width - margin, height), colors['opponent_bg'], -1)
    
    # Draw headers
    _draw_header(img, "PLAYER", margin, 0, column_width, header_height, colors)
    _draw_header(img, "OPPONENT", 2 * margin + column_width, 0, column_width, header_height, colors)
    
    # Draw active Pokemon sections
    player_active = battle_state.get_player_active_mon()
    opponent_active = battle_state.get_opponent_active_mon()
    
    _draw_active_pokemon(img, player_active, margin, header_height, column_width, active_section_height, colors, "ACTIVE POKEMON")
    _draw_active_pokemon(img, opponent_active, 2 * margin + column_width, header_height, column_width, active_section_height, colors, "ACTIVE POKEMON")
    
    # Draw team sections
    team_section_height = height - team_section_start - margin
    _draw_team_section(img, battle_state.player_team, battle_state.player_team.in_play, 
                      margin, team_section_start, column_width, team_section_height, colors, "TEAM")
    _draw_team_section(img, battle_state.opponent_team, battle_state.opponent_team.in_play,
                      2 * margin + column_width, team_section_start, column_width, team_section_height, colors, "TEAM")
    
    return img


def _draw_header(img: np.ndarray, title: str, x: int, y: int, width: int, height: int, colors: dict):
    """Draw a header section with title"""
    cv2.rectangle(img, (x, y), (x + width, y + height), colors['header_bg'], -1)
    
    # Calculate text position for centering
    text_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_DUPLEX, 1.2, 2)[0]
    text_x = x + (width - text_size[0]) // 2
    text_y = y + (height + text_size[1]) // 2
    
    cv2.putText(img, title, (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX, 1.2, colors['header_text'], 2)


def _draw_active_pokemon(img: np.ndarray, pokemon: PokemonState, x: int, y: int, width: int, height: int, colors: dict, title: str):
    """Draw the active Pokemon section with detailed information"""
    # Draw section border
    cv2.rectangle(img, (x + 5, y + 5), (x + width - 5, y + height - 5), colors['active_border'], 2)
    
    current_y = y + 25
    
    # Title
    cv2.putText(img, title, (x + 10, current_y), cv2.FONT_HERSHEY_DUPLEX, 0.7, colors['text'], 2)
    current_y += 30
    
    # Pokemon info
    species_name = pokemon.species or "Unknown"
    level_text = f"Lv.{pokemon.level}" if pokemon.level > 0 else "Lv.?"
    pokemon_text = f"{species_name} {level_text}"
    
    cv2.putText(img, pokemon_text, (x + 10, current_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, colors['text'], 2)
    current_y += 30
    
    # HP bar
    hp_bar_width = width - 40
    hp_bar_height = 20
    _draw_hp_bar(img, pokemon.hp, x + 20, current_y, hp_bar_width, hp_bar_height, colors)
    current_y += 35
    
    # Status condition
    if pokemon.status != Status.NONE:
        status_text = _get_status_text(pokemon.status)
        cv2.rectangle(img, (x + 10, current_y - 5), (x + 10 + len(status_text) * 10, current_y + 15), colors['status_bg'], -1)
        cv2.putText(img, status_text, (x + 15, current_y + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['text'], 1)
        current_y += 25
    
    # Moves
    moves = [pokemon.move1, pokemon.move2, pokemon.move3, pokemon.move4]
    cv2.putText(img, "MOVES:", (x + 10, current_y), cv2.FONT_HERSHEY_DUPLEX, 0.6, colors['text'], 1)
    current_y += 20
    
    for i, move in enumerate(moves):
        if move and move.known and move.name:
            move_text = f"{move.name} ({move.pp}/{move.pp_max})"
            if move.disabled:
                move_text += " [DISABLED]"
            
            move_color = colors['text'] if not move.disabled else (128, 128, 128)
            cv2.putText(img, move_text, (x + 20, current_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, move_color, 1)
            current_y += 18


def _draw_team_section(img: np.ndarray, team_state, in_play: list, x: int, y: int, width: int, height: int, colors: dict, title: str):
    """Draw the team section showing all Pokemon in play"""
    # Title
    cv2.putText(img, title, (x + 10, y + 20), cv2.FONT_HERSHEY_DUPLEX, 0.7, colors['text'], 2)
    
    current_y = y + 40
    pokemon_height = 60
    
    for i, pokemon_idx in enumerate(in_play):
        if pokemon_idx < len(team_state.pk_list):
            pokemon = team_state.pk_list[pokemon_idx]
            
            # Pokemon container
            pokemon_y = current_y + i * (pokemon_height + 10)
            
            # Border color based on active status
            border_color = colors['active_border'] if pokemon.active else colors['inactive_border']
            cv2.rectangle(img, (x + 10, pokemon_y), (x + width - 10, pokemon_y + pokemon_height), border_color, 2)
            
            # Pokemon info
            species_name = pokemon.species or f"Pokemon {pokemon_idx + 1}"
            level_text = f"Lv.{pokemon.level}" if pokemon.level > 0 else "Lv.?"
            
            cv2.putText(img, f"{species_name} {level_text}", (x + 15, pokemon_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['text'], 1)
            
            # HP bar (smaller)
            hp_bar_width = width - 60
            hp_bar_height = 12
            _draw_hp_bar(img, pokemon.hp, x + 15, pokemon_y + 30, hp_bar_width, hp_bar_height, colors)
            
            # Status
            if pokemon.status != Status.NONE:
                status_text = _get_status_text(pokemon.status)
                cv2.putText(img, status_text, (x + 15, pokemon_y + 52), cv2.FONT_HERSHEY_SIMPLEX, 0.4, colors['text'], 1)


def _draw_hp_bar(img: np.ndarray, hp: float, x: int, y: int, width: int, height: int, colors: dict):
    """Draw an HP bar with color coding"""
    # Background
    cv2.rectangle(img, (x, y), (x + width, y + height), colors['hp_bar_bg'], -1)
    MAX_HP = 500 # Use 500 even if Chansey can have more.
    hp_percent = hp / MAX_HP * 100 

    # HP fill
    if hp_percent > 0:
        fill_width = int((hp_percent / 100.0) * width)
        
        # Color based on HP percentage
        if hp_percent > 50:
            hp_color = colors['hp_bar_full']
        elif hp_percent > 25:
            hp_color = colors['hp_bar_medium']
        else:
            hp_color = colors['hp_bar_low']
        
        cv2.rectangle(img, (x, y), (x + fill_width, y + height), hp_color, -1)
    
    # Border
    cv2.rectangle(img, (x, y), (x + width, y + height), colors['text'], 1)
    
    # HP text
    hp_text = f"{hp:.1f}%"
    text_size = cv2.getTextSize(hp_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
    text_x = x + (width - text_size[0]) // 2
    text_y = y + (height + text_size[1]) // 2
    cv2.putText(img, hp_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, colors['text'], 1)


def _get_status_text(status: Status) -> str:
    """Get display text for status conditions"""
    status_map = {
        Status.NONE: "",
        Status.POISONED: "PSN",
        Status.BURNED: "BRN", 
        Status.PARALYZED: "PAR",
        Status.SLEEP: "SLP",
        Status.FROZEN: "FRZ",
        Status.FAINTED: "FNT"
    }
    return status_map.get(status, "UNK")


def save_battle_state_image(battle_state: BattleState, filename: str, width: int = 1200, height: int = 800):
    """
    Draw and save a BattleState visualization to a file
    
    Args:
        battle_state: The BattleState to visualize
        filename: Output filename (should include .png, .jpg, etc.)
        width: Width of the output image
        height: Height of the output image
    """
    img = draw_battle_state(battle_state, width, height)
    cv2.imwrite(filename, img)


def display_battle_state(battle_state: BattleState, width: int = 1200, height: int = 800, window_name: str = "Battle State"):
    """
    Draw and display a BattleState in a window
    
    Args:
        battle_state: The BattleState to visualize
        width: Width of the display window
        height: Height of the display window
        window_name: Name of the display window
    """
    img = draw_battle_state(battle_state, width, height)
    cv2.imshow(window_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # Example usage
    from src.state.pokestate import create_default_battle_state, MoveState
    
    # Create example battle state
    state = create_default_battle_state()
    
    # Set up player active Pokemon
    state.player_team.pk_list[0].species = "Charizard"
    state.player_team.pk_list[0].level = 50
    state.player_team.pk_list[0].hp = 85.5
    state.player_team.pk_list[0].status = Status.BURNED
    state.player_team.pk_list[0].known = True
    state.player_team.pk_list[0].active = True
    state.player_team.pk_list[0].in_play = True
    state.player_team.pk_list[0].move1 = MoveState(known=True, name="Flamethrower", pp=15, pp_max=15, disabled=False)
    state.player_team.pk_list[0].move2 = MoveState(known=True, name="Dragon Pulse", pp=10, pp_max=10, disabled=False)
    state.player_team.pk_list[0].move3 = MoveState(known=True, name="Solar Beam", pp=5, pp_max=10, disabled=True)
    state.player_team.pk_list[0].move4 = MoveState(known=True, name="Earthquake", pp=8, pp_max=10, disabled=False)
    
    # Set up opponent active Pokemon
    state.opponent_team.pk_list[0].species = "Blastoise"
    state.opponent_team.pk_list[0].level = 50
    state.opponent_team.pk_list[0].hp = 23.7
    state.opponent_team.pk_list[0].status = Status.NONE
    state.opponent_team.pk_list[0].known = True
    state.opponent_team.pk_list[0].active = True
    state.opponent_team.pk_list[0].in_play = True
    state.opponent_team.pk_list[0].move1 = MoveState(known=True, name="Surf", pp=12, pp_max=15, disabled=False)
    state.opponent_team.pk_list[0].move2 = MoveState(known=True, name="Ice Beam", pp=8, pp_max=10, disabled=False)
    state.opponent_team.pk_list[0].move3 = MoveState(known=True, name="Earthquake", pp=10, pp_max=10, disabled=False)
    state.opponent_team.pk_list[0].move4 = MoveState(known=True, name="Rest", pp=10, pp_max=10, disabled=False)
    
    # Add some team members
    for i in range(1, 4):
        # Player team
        state.player_team.pk_list[i].species = f"Pokemon{i+1}"
        state.player_team.pk_list[i].level = 45 + i
        state.player_team.pk_list[i].hp = 60.0 + i * 10
        state.player_team.pk_list[i].in_play = True
        state.player_team.pk_list[i].known = True
        
        # Opponent team  
        state.opponent_team.pk_list[i].species = f"OpponentPkmn{i+1}"
        state.opponent_team.pk_list[i].level = 47 + i
        state.opponent_team.pk_list[i].hp = 70.0 + i * 5
        state.opponent_team.pk_list[i].in_play = True
        state.opponent_team.pk_list[i].known = True
    
    # Set up in_play lists
    state.player_team.in_play = [0, 1, 2, 3]
    state.opponent_team.in_play = [0, 1, 2, 3]
    
    # Display the battle state
    display_battle_state(state)
    
    # Save to file
    save_battle_state_image(state, "example_battle_state.png")
    print("Battle state visualization saved as 'example_battle_state.png'")