#!/usr/bin/env python3
"""
Demo script for the Pokémon Stadium Rental Parser
Shows various ways to use the parser and query the data
"""

from pokerental_parse import PokemonRentalParser
import json


def main():
    """Demonstrate various uses of the parser"""
    print("=== Pokémon Stadium Rental Parser Demo ===\n")
    
    # Initialize parser
    parser = PokemonRentalParser()
    
    print("1. Loading and parsing data...")
    parser.parse_pokemon_data()
    
    stats = parser.get_stats_summary()
    print(f"   Successfully parsed {stats['total_pokemon']} Pokemon!\n")
    
    print("2. Finding specific Pokemon...")
    # Get specific Pokemon by number
    charizard = parser.get_pokemon_by_number("006")
    if charizard:
        print(f"   Charizard found: {charizard['name']} (Level {charizard['level']})")
        print(f"   Stats: {charizard['stats']}")
        print(f"   Moves: {charizard['moves']}\n")
    
    # Get Pokemon by name
    pikachu = parser.get_pokemon_by_name("Pikachu")
    if pikachu:
        print(f"   Pikachu found: #{pikachu['number']} (Level {pikachu['level']})")
        print(f"   Stats: {pikachu['stats']}")
        print(f"   Moves: {pikachu['moves']}\n")
    
    print("3. Searching Pokemon by moves...")
    # Find Pokemon with specific moves
    earthquake_pokemon = parser.search_pokemon_by_move("Earthquake")
    print(f"   Pokemon with Earthquake: {len(earthquake_pokemon)} found")
    for p in earthquake_pokemon[:5]:  # Show first 5
        print(f"   - #{p['number']} {p['name'].strip()}")
    
    psychic_pokemon = parser.search_pokemon_by_move("Psychic")
    print(f"\n   Pokemon with Psychic: {len(psychic_pokemon)} found")
    for p in psychic_pokemon[:5]:  # Show first 5
        print(f"   - #{p['number']} {p['name'].strip()}")
    
    print("\n4. Searching Pokemon by stats...")
    # Find Pokemon with high HP
    high_hp_pokemon = parser.search_pokemon_by_stat_range("hp", 200, 400)
    print(f"   Pokemon with HP 200-400: {len(high_hp_pokemon)} found")
    for p in high_hp_pokemon:
        print(f"   - #{p['number']} {p['name'].strip()} (HP: {p['stats']['hp']})")
    
    # Find fast Pokemon
    fast_pokemon = parser.search_pokemon_by_stat_range("speed", 130, 200)
    print(f"\n   Pokemon with Speed 130-200: {len(fast_pokemon)} found")
    for p in fast_pokemon[:5]:  # Show first 5
        print(f"   - #{p['number']} {p['name'].strip()} (Speed: {p['stats']['speed']})")
    
    # Find strong attackers
    strong_attackers = parser.search_pokemon_by_stat_range("attack", 140, 200)
    print(f"\n   Pokemon with Attack 140-200: {len(strong_attackers)} found")
    for p in strong_attackers:
        print(f"   - #{p['number']} {p['name'].strip()} (Attack: {p['stats']['attack']})")
    
    print("\n5. Legendary Pokemon analysis...")
    # Check legendary Pokemon (typically #144-151)
    legendary_numbers = ["144", "145", "146", "147", "148", "149"]
    legendaries = []
    for num in legendary_numbers:
        pokemon = parser.get_pokemon_by_number(num)
        if pokemon:
            legendaries.append(pokemon)
    
    print(f"   Found {len(legendaries)} legendary Pokemon:")
    for legend in legendaries:
        print(f"   - #{legend['number']} {legend['name'].strip()}")
        print(f"     Stats: {legend['stats']}")
        print(f"     Moves: {legend['moves']}")
        print()
    
    print("6. Type analysis by moves...")
    # Analyze Pokemon by move types
    fire_moves = ["Flamethrower", "Fire Blast", "Fire Spin", "Fire Punch"]
    water_moves = ["Surf", "Hydro Pump", "Ice Beam", "Blizzard"]
    electric_moves = ["Thunderbolt", "Thunder", "Thunder Wave", "Thunderpunch"]
    
    fire_pokemon = []
    water_pokemon = []
    electric_pokemon = []
    
    for pokemon in parser.get_all_pokemon():
        if any(move in pokemon['moves'] for move in fire_moves):
            fire_pokemon.append(pokemon)
        if any(move in pokemon['moves'] for move in water_moves):
            water_pokemon.append(pokemon)
        if any(move in pokemon['moves'] for move in electric_moves):
            electric_pokemon.append(pokemon)
    
    print(f"   Pokemon with Fire-type moves: {len(fire_pokemon)}")
    print(f"   Pokemon with Water-type moves: {len(water_pokemon)}")
    print(f"   Pokemon with Electric-type moves: {len(electric_pokemon)}")
    
    print("\n7. Stat distribution analysis...")
    # Analyze stat distributions
    all_pokemon = parser.get_all_pokemon()
    
    hp_values = [p['stats']['hp'] for p in all_pokemon if 'hp' in p['stats']]
    attack_values = [p['stats']['attack'] for p in all_pokemon if 'attack' in p['stats']]
    speed_values = [p['stats']['speed'] for p in all_pokemon if 'speed' in p['stats']]
    
    if hp_values:
        print(f"   HP range: {min(hp_values)} - {max(hp_values)}")
        print(f"   Average HP: {sum(hp_values) / len(hp_values):.1f}")
    
    if attack_values:
        print(f"   Attack range: {min(attack_values)} - {max(attack_values)}")
        print(f"   Average Attack: {sum(attack_values) / len(attack_values):.1f}")
    
    if speed_values:
        print(f"   Speed range: {min(speed_values)} - {max(speed_values)}")
        print(f"   Average Speed: {sum(speed_values) / len(speed_values):.1f}")
    
    print("\n8. Export options...")
    # Save different formats
    parser.save_to_json("pokemon_rental_complete.json")
    print("   - Complete data saved to 'pokemon_rental_complete.json'")
    
    # Save only high-stat Pokemon
    powerful_pokemon = [p for p in all_pokemon 
                       if p['stats'].get('attack', 0) > 120 or 
                          p['stats'].get('hp', 0) > 180 or 
                          p['stats'].get('speed', 0) > 130]
    
    with open("powerful_pokemon.json", 'w', encoding='utf-8') as f:
        json.dump(powerful_pokemon, f, indent=2, ensure_ascii=False)
    print(f"   - {len(powerful_pokemon)} powerful Pokemon saved to 'powerful_pokemon.json'")
    
    print("\n=== Demo Complete ===")
    print(f"Total Pokemon processed: {len(all_pokemon)}")
    print("Parser is ready for use in your application!")


if __name__ == "__main__":
    main()
