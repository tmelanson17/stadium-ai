#!/usr/bin/env python3
"""
Improved Pokémon Stadium Rental Parser for Serebii.net
Parses the 'poketab' section from https://www.serebii.net/stadium/pokerental.shtml
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional
import json

from src.state.gen1_moves import get_move_by_name


class PokemonRentalParser:
    """Parser for Pokémon Stadium rental data from Serebii.net"""
    
    def __init__(self, url: str = "https://www.serebii.net/stadium/pokerental.shtml"):
        self.url = url
        self.soup = None
        self.pokemon_data = []
    
    def fetch_page(self) -> None:
        """Fetch the HTML page and parse it with BeautifulSoup"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch page: {e}")
    
    def parse_pokemon_data(self) -> List[Dict]:
        """Parse all Pokémon data from the page"""
        if not self.soup:
            self.fetch_page()
        
        self.pokemon_data = []
        
        # The page has tables with Pokemon data
        # Let's find all tables and extract the data
        tables = self.soup.find_all('table')
        
        # Get all text content for pattern matching
        page_text = self.soup.get_text()
        
        # Find all Pokemon entries using regex
        pokemon_pattern = r'#(\d{3})\s+([A-Za-z♀♂\'\-\.\s]+?)(?=\s*\||\s*Level|\s*HP:|\s*Attack:|\s*#\d{3}|$)'
        pokemon_matches = re.finditer(pokemon_pattern, page_text)
        
        for match in pokemon_matches:
            pokemon_number = match.group(1)
            pokemon_name = match.group(2).strip()
            
            # Extract the data section for this Pokemon
            pokemon_info = self._extract_pokemon_info(pokemon_number, pokemon_name, page_text)
            if pokemon_info:
                self.pokemon_data.append(pokemon_info)
        
        return self.pokemon_data
    
    def _extract_pokemon_info(self, number: str, name: str, page_text: str) -> Optional[Dict]:
        """Extract complete Pokemon information from the page text"""
        # Clean up the name
        clean_name = re.sub(r'\s+', ' ', name.strip())
        clean_name = re.sub(r'[^\w\s♀♂\'\-\.]', '', clean_name)
        clean_name = clean_name.split(' ')[0]  # Use only the first part of the name for matching
        
        # Find the start of this Pokemon's section
        pokemon_section_pattern = f"#{number}\\s+{re.escape(clean_name)}"
        start_match = re.search(pokemon_section_pattern, page_text, re.IGNORECASE)
        
        if not start_match:
            return None
        
        start_pos = start_match.start()
        
        # Find the end of this Pokemon's section (next Pokemon or end of text)
        next_pokemon_pattern = f"#{int(number) + 1:03d}\\s+"
        end_match = re.search(next_pokemon_pattern, page_text[start_pos + 1:])
        
        if end_match:
            end_pos = start_pos + end_match.start() + 1
        else:
            # If no next Pokemon found, look for any Pokemon pattern
            end_match = re.search(r'#\d{3}\s+[A-Za-z♀♂\'\-\.\s]+', page_text[start_pos + 1:])
            end_pos = start_pos + end_match.start() + 1 if end_match else len(page_text)
        
        section_text = page_text[start_pos:end_pos]
        
        # Parse the section
        pokemon_info = {
            'number': number,
            'species': clean_name,
            'nickname': clean_name.upper(),
            'level': self._extract_level(section_text),
            'stats': self._extract_stats(section_text),
            'moves': self._extract_moves(section_text)
        }
        
        return pokemon_info
    
    def _extract_level(self, text: str) -> Optional[int]:
        """Extract level from Pokemon section text"""
        level_match = re.search(r'Level\s+(\d+)', text)
        return int(level_match.group(1)) if level_match else None
    
    def _extract_stats(self, text: str) -> Dict[str, int]:
        """Extract stats from Pokemon section text"""
        stats = {}
        
        # Define stat patterns
        stat_patterns = {
            'hp': r'HP:\s*(\d+)',
            'attack': r'Attack:\s*(\d+)',
            'defense': r'Defense:\s*(\d+)',
            'special': r'Special:\s*(\d+)',
            'speed': r'Speed:\s*(\d+)'
        }
        
        for stat_name, pattern in stat_patterns.items():
            match = re.search(pattern, text)
            if match:
                stats[stat_name] = int(match.group(1))
        
        return stats
    
    def _extract_moves(self, text: str) -> List[str]:
        """Extract moves from Pokemon section text"""
        lines = [l for l in text.split('\n') if l.strip()]
        move_lines = lines[-4:]  
        
        
        moves = []
        for move in move_lines:
            move = move.strip()
            # Weird edge case with Exploison (Explosion) and Nigh Shade (Night Shade)
            move = re.sub(r'\bExploison\b', 'Explosion', move, flags=re.IGNORECASE)
            move = re.sub(r'\bNigh Shade\b', 'Night Shade', move, flags=re.IGNORECASE)
            if move and get_move_by_name(move):
                moves.append(move)
        return moves
    
    def get_pokemon_by_number(self, number: str) -> Optional[Dict]:
        """Get a specific Pokemon by its number"""
        if not self.pokemon_data:
            self.parse_pokemon_data()
        
        for pokemon in self.pokemon_data:
            if pokemon['number'] == number:
                return pokemon
        return None
    
    def get_pokemon_by_name(self, name: str) -> Optional[Dict]:
        """Get a specific Pokemon by its name"""
        if not self.pokemon_data:
            self.parse_pokemon_data()
        
        for pokemon in self.pokemon_data:
            if pokemon['species'].lower() == name.lower():
                return pokemon
        return None
    
    def get_all_pokemon(self) -> List[Dict]:
        """Get all Pokemon data"""
        if not self.pokemon_data:
            self.parse_pokemon_data()
        return self.pokemon_data
    
    def save_to_json(self, filename: str) -> None:
        """Save parsed data to JSON file"""
        if not self.pokemon_data:
            self.parse_pokemon_data()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.pokemon_data, f, indent=2, ensure_ascii=False)
    
    def print_pokemon_summary(self) -> None:
        """Print a summary of all Pokemon"""
        if not self.pokemon_data:
            self.parse_pokemon_data()
        
        print(f"Found {len(self.pokemon_data)} Pokemon in the rental list:")
        print("-" * 60)
        
        for pokemon in self.pokemon_data:
            print(f"#{pokemon['number']} {pokemon['species']} (Level {pokemon.get('level', 'Unknown')})")
            if pokemon['stats']:
                stats_str = ", ".join([f"{k.title()}: {v}" for k, v in pokemon['stats'].items()])
                print(f"  Stats: {stats_str}")
            if pokemon['moves']:
                moves_str = ", ".join(pokemon['moves'])
                print(f"  Moves: {moves_str}")
            print()
    
    def get_stats_summary(self) -> Dict:
        """Get summary statistics about the parsed data"""
        if not self.pokemon_data:
            self.parse_pokemon_data()
        
        total_pokemon = len(self.pokemon_data)
        pokemon_with_stats = sum(1 for p in self.pokemon_data if p['stats'])
        pokemon_with_moves = sum(1 for p in self.pokemon_data if p['moves'])
        
        return {
            'total_pokemon': total_pokemon,
            'pokemon_with_stats': pokemon_with_stats,
            'pokemon_with_moves': pokemon_with_moves,
            'completion_rate': {
                'stats': f"{pokemon_with_stats/total_pokemon*100:.1f}%" if total_pokemon > 0 else "0%",
                'moves': f"{pokemon_with_moves/total_pokemon*100:.1f}%" if total_pokemon > 0 else "0%"
            }
        }

def create_team_from_data(pokemon_data: List[Dict]) -> Dict[str, List[Dict]]:
    """ 
        Creates a team of 6 Pokemon randomly selected from the parsed data.
    """
    import random
    if len(pokemon_data) < 6:
        raise ValueError("Not enough Pokemon data available to create a team.")
    blacklist = ["Ditto", "Caterpie", "Weedle", "Metapod", "Kakuna", "Zubat", "Magikarp", "E"]  # Example blacklist to avoid certain Pokemon
    pokemon_filtered = [p for p in pokemon_data if p['species'] not in blacklist]

    # Randomly select 6 unique Pokemon
    selected_pokemon1 = random.sample(pokemon_filtered, 6)
    selected_pokemon2 = random.sample(pokemon_filtered, 6)

    return {
        "Team 1": selected_pokemon1,
        "Team 2": selected_pokemon2
    }


def main():
    """Main function to demonstrate the parser"""
    parser = PokemonRentalParser()
    
    try:
        print("Fetching and parsing Pokémon Stadium rental data...")
        parser.parse_pokemon_data()
        
        stats = parser.get_stats_summary()
        print(f"\nSuccessfully parsed {stats['total_pokemon']} Pokemon!")
        print(f"Pokemon with stats: {stats['pokemon_with_stats']} ({stats['completion_rate']['stats']})")
        print(f"Pokemon with moves: {stats['pokemon_with_moves']} ({stats['completion_rate']['moves']})")
        
        # Show first few Pokemon as examples
        print("\nFirst 5 Pokemon:")
        print("-" * 60)
        for i, pokemon in enumerate(parser.pokemon_data[:5]):
            print(f"#{pokemon['number']} (Level {pokemon.get('level', 'Unknown')})")
            if pokemon['stats']:
                stats_str = ", ".join([f"{k.title()}: {v}" for k, v in pokemon['stats'].items()])
                print(f"  Stats: {stats_str}")
            if pokemon['moves']:
                moves_str = ", ".join(pokemon['moves'])
                print(f"  Moves: {moves_str}")
            print()
        
        
        # Save to JSON
        parser.save_to_json("config/pokemon_rental_data.json")
        print(f"\nData saved to 'pokemon_rental_data.json'")

        # Show random team creation
        from src.params.yaml_parser import save_dict_to_yaml
        print("Creating random teams...")
        team_data = create_team_from_data(parser.get_all_pokemon())
        for team in ["Team 1", "Team 2"]:
            print(f"\n{team}:")
            for pokemon in team_data[team]:
                print(f"#{pokemon['number']} {pokemon['species']} (Level {pokemon.get('level', 'Unknown')})")
                if pokemon['stats']:
                    stats_str = ", ".join([f"{k.title()}: {v}" for k, v in pokemon['stats'].items()])
                    print(f"  Stats: {stats_str}")
                if pokemon['moves']:
                    moves_str = ", ".join(pokemon['moves'])
                    print(f"  Moves: {moves_str}")
                print()
        save_dict_to_yaml(team_data, "config/pokemon_rental_teams.yaml")

        
        # Example: Get specific Pokemon
        bulbasaur = parser.get_pokemon_by_name("Bulbasaur")
        if bulbasaur:
            print(f"\nExample - Bulbasaur data:")
            print(json.dumps(bulbasaur, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
