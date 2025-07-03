"""
Generation 1 Pokédex data including all Pokémon species and type information.
This module provides comprehensive data for all 151 original Pokémon.
"""

from typing import Dict, List, Tuple

# All Pokémon types in Generation 1
TYPES = [
    "Normal",
    "Fire", 
    "Water",
    "Electric",
    "Grass",
    "Ice",
    "Fighting",
    "Poison",
    "Ground",
    "Flying",
    "Psychic",
    "Bug",
    "Rock",
    "Ghost",
    "Dragon"
]

# Type effectiveness chart (attacking type -> defending type -> effectiveness)
TYPE_CHART = {
    "Normal": {
        "Rock": 0.5,
        "Ghost": 0.0,
    },
    "Fire": {
        "Fire": 0.5,
        "Water": 0.5,
        "Grass": 2.0,
        "Ice": 2.0,
        "Bug": 2.0,
        "Rock": 0.5,
        "Dragon": 0.5,
    },
    "Water": {
        "Fire": 2.0,
        "Water": 0.5,
        "Grass": 0.5,
        "Ground": 2.0,
        "Rock": 2.0,
        "Dragon": 0.5,
    },
    "Electric": {
        "Water": 2.0,
        "Electric": 0.5,
        "Grass": 0.5,
        "Ground": 0.0,
        "Flying": 2.0,
        "Dragon": 0.5,
    },
    "Grass": {
        "Fire": 0.5,
        "Water": 2.0,
        "Grass": 0.5,
        "Poison": 0.5,
        "Ground": 2.0,
        "Flying": 0.5,
        "Bug": 0.5,
        "Rock": 2.0,
        "Dragon": 0.5,
    },
    "Ice": {
        "Water": 0.5,
        "Grass": 2.0,
        "Ice": 0.5,
        "Ground": 2.0,
        "Flying": 2.0,
        "Dragon": 2.0,
    },
    "Fighting": {
        "Normal": 2.0,
        "Ice": 2.0,
        "Poison": 0.5,
        "Flying": 0.5,
        "Psychic": 0.5,
        "Bug": 0.5,
        "Rock": 2.0,
        "Ghost": 0.0,
    },
    "Poison": {
        "Grass": 2.0,
        "Poison": 0.5,
        "Ground": 0.5,
        "Bug": 2.0,
        "Rock": 0.5,
        "Ghost": 0.5,
    },
    "Ground": {
        "Fire": 2.0,
        "Electric": 2.0,
        "Grass": 0.5,
        "Poison": 2.0,
        "Flying": 0.0,
        "Bug": 0.5,
        "Rock": 2.0,
    },
    "Flying": {
        "Electric": 0.5,
        "Grass": 2.0,
        "Ice": 0.5,
        "Fighting": 2.0,
        "Bug": 2.0,
        "Rock": 0.5,
    },
    "Psychic": {
        "Fighting": 2.0,
        "Poison": 2.0,
        "Psychic": 0.5,
    },
    "Bug": {
        "Fire": 0.5,
        "Grass": 2.0,
        "Fighting": 0.5,
        "Poison": 2.0,
        "Flying": 0.5,
        "Psychic": 2.0,
        "Ghost": 0.5,
    },
    "Rock": {
        "Fire": 2.0,
        "Ice": 2.0,
        "Fighting": 0.5,
        "Ground": 0.5,
        "Flying": 2.0,
        "Bug": 2.0,
    },
    "Ghost": {
        "Normal": 0.0,
        "Psychic": 0.0,
        "Ghost": 2.0,
    },
    "Dragon": {
        "Dragon": 2.0,
    },
}

# Complete Generation 1 Pokédex
# Format: (name, type1, type2 or None, base_stats: [HP, Attack, Defense, Special, Speed])
GEN1_POKEMON = {
    1: ("Bulbasaur", "Grass", "Poison", [45, 49, 49, 65, 45]),
    2: ("Ivysaur", "Grass", "Poison", [60, 62, 63, 80, 60]),
    3: ("Venusaur", "Grass", "Poison", [80, 82, 83, 100, 80]),
    4: ("Charmander", "Fire", None, [39, 52, 43, 50, 65]),
    5: ("Charmeleon", "Fire", None, [58, 64, 58, 80, 80]),
    6: ("Charizard", "Fire", "Flying", [78, 84, 78, 109, 100]),
    7: ("Squirtle", "Water", None, [44, 48, 65, 50, 43]),
    8: ("Wartortle", "Water", None, [59, 63, 80, 65, 58]),
    9: ("Blastoise", "Water", None, [79, 83, 100, 85, 78]),
    10: ("Caterpie", "Bug", None, [45, 30, 35, 20, 45]),
    11: ("Metapod", "Bug", None, [50, 20, 55, 25, 30]),
    12: ("Butterfree", "Bug", "Flying", [60, 45, 50, 90, 70]),
    13: ("Weedle", "Bug", "Poison", [40, 35, 30, 20, 50]),
    14: ("Kakuna", "Bug", "Poison", [45, 25, 50, 25, 35]),
    15: ("Beedrill", "Bug", "Poison", [65, 90, 40, 45, 75]),
    16: ("Pidgey", "Normal", "Flying", [40, 45, 40, 35, 56]),
    17: ("Pidgeotto", "Normal", "Flying", [63, 60, 55, 50, 71]),
    18: ("Pidgeot", "Normal", "Flying", [83, 80, 75, 70, 101]),
    19: ("Rattata", "Normal", None, [30, 56, 35, 25, 72]),
    20: ("Raticate", "Normal", None, [55, 81, 60, 50, 97]),
    21: ("Spearow", "Normal", "Flying", [40, 60, 30, 31, 70]),
    22: ("Fearow", "Normal", "Flying", [65, 90, 65, 61, 100]),
    23: ("Ekans", "Poison", None, [35, 60, 44, 40, 55]),
    24: ("Arbok", "Poison", None, [60, 85, 69, 65, 80]),
    25: ("Pikachu", "Electric", None, [35, 55, 30, 50, 90]),
    26: ("Raichu", "Electric", None, [60, 90, 55, 90, 110]),
    27: ("Sandshrew", "Ground", None, [50, 75, 85, 30, 40]),
    28: ("Sandslash", "Ground", None, [75, 100, 110, 45, 65]),
    29: ("Nidoran♀", "Poison", None, [55, 47, 52, 40, 41]),
    30: ("Nidorina", "Poison", None, [70, 62, 67, 55, 56]),
    31: ("Nidoqueen", "Poison", "Ground", [90, 92, 87, 75, 76]),
    32: ("Nidoran♂", "Poison", None, [46, 57, 40, 40, 50]),
    33: ("Nidorino", "Poison", None, [61, 72, 57, 55, 65]),
    34: ("Nidoking", "Poison", "Ground", [81, 102, 77, 85, 85]),
    35: ("Clefairy", "Normal", None, [70, 45, 48, 60, 35]),
    36: ("Clefable", "Normal", None, [95, 70, 73, 95, 60]),
    37: ("Vulpix", "Fire", None, [38, 41, 40, 65, 65]),
    38: ("Ninetales", "Fire", None, [73, 76, 75, 81, 100]),
    39: ("Jigglypuff", "Normal", None, [115, 45, 20, 25, 20]),
    40: ("Wigglytuff", "Normal", None, [140, 70, 45, 85, 45]),
    41: ("Zubat", "Poison", "Flying", [40, 45, 35, 40, 55]),
    42: ("Golbat", "Poison", "Flying", [75, 80, 70, 65, 90]),
    43: ("Oddish", "Grass", "Poison", [45, 50, 55, 75, 30]),
    44: ("Gloom", "Grass", "Poison", [60, 65, 70, 85, 40]),
    45: ("Vileplume", "Grass", "Poison", [75, 80, 85, 110, 50]),
    46: ("Paras", "Bug", "Grass", [35, 70, 55, 55, 25]),
    47: ("Parasect", "Bug", "Grass", [60, 95, 80, 60, 30]),
    48: ("Venonat", "Bug", "Poison", [60, 55, 50, 40, 45]),
    49: ("Venomoth", "Bug", "Poison", [70, 65, 60, 90, 90]),
    50: ("Diglett", "Ground", None, [10, 55, 25, 45, 95]),
    51: ("Dugtrio", "Ground", None, [35, 80, 50, 50, 120]),
    52: ("Meowth", "Normal", None, [40, 45, 35, 40, 90]),
    53: ("Persian", "Normal", None, [65, 70, 60, 65, 115]),
    54: ("Psyduck", "Water", None, [50, 52, 48, 50, 55]),
    55: ("Golduck", "Water", None, [80, 82, 78, 95, 85]),
    56: ("Mankey", "Fighting", None, [40, 80, 35, 35, 70]),
    57: ("Primeape", "Fighting", None, [65, 105, 60, 60, 95]),
    58: ("Growlithe", "Fire", None, [55, 70, 45, 50, 60]),
    59: ("Arcanine", "Fire", None, [90, 110, 80, 100, 95]),
    60: ("Poliwag", "Water", None, [40, 50, 40, 40, 90]),
    61: ("Poliwhirl", "Water", None, [65, 65, 65, 50, 90]),
    62: ("Poliwrath", "Water", "Fighting", [90, 95, 95, 70, 70]),
    63: ("Abra", "Psychic", None, [25, 20, 15, 105, 90]),
    64: ("Kadabra", "Psychic", None, [40, 35, 30, 120, 105]),
    65: ("Alakazam", "Psychic", None, [55, 50, 45, 135, 120]),
    66: ("Machop", "Fighting", None, [70, 80, 50, 35, 35]),
    67: ("Machoke", "Fighting", None, [80, 100, 70, 50, 45]),
    68: ("Machamp", "Fighting", None, [90, 130, 80, 65, 55]),
    69: ("Bellsprout", "Grass", "Poison", [50, 75, 35, 70, 40]),
    70: ("Weepinbell", "Grass", "Poison", [65, 90, 50, 85, 55]),
    71: ("Victreebel", "Grass", "Poison", [80, 105, 65, 100, 70]),
    72: ("Tentacool", "Water", "Poison", [40, 40, 35, 50, 70]),
    73: ("Tentacruel", "Water", "Poison", [80, 70, 65, 80, 100]),
    74: ("Geodude", "Rock", "Ground", [40, 80, 100, 30, 20]),
    75: ("Graveler", "Rock", "Ground", [55, 95, 115, 45, 35]),
    76: ("Golem", "Rock", "Ground", [80, 120, 130, 55, 45]),
    77: ("Ponyta", "Fire", None, [50, 85, 55, 65, 90]),
    78: ("Rapidash", "Fire", None, [65, 100, 70, 80, 105]),
    79: ("Slowpoke", "Water", "Psychic", [90, 65, 65, 40, 15]),
    80: ("Slowbro", "Water", "Psychic", [95, 75, 110, 100, 30]),
    81: ("Magnemite", "Electric", None, [25, 35, 70, 95, 45]),
    82: ("Magneton", "Electric", None, [50, 60, 95, 120, 70]),
    83: ("Farfetch'd", "Normal", "Flying", [52, 65, 55, 58, 60]),
    84: ("Doduo", "Normal", "Flying", [35, 85, 45, 35, 75]),
    85: ("Dodrio", "Normal", "Flying", [60, 110, 70, 60, 100]),
    86: ("Seel", "Water", None, [65, 45, 55, 45, 45]),
    87: ("Dewgong", "Water", "Ice", [90, 70, 80, 70, 70]),
    88: ("Grimer", "Poison", None, [80, 80, 50, 40, 25]),
    89: ("Muk", "Poison", None, [105, 105, 75, 65, 50]),
    90: ("Shellder", "Water", None, [30, 65, 100, 45, 40]),
    91: ("Cloyster", "Water", "Ice", [50, 95, 180, 85, 70]),
    92: ("Gastly", "Ghost", "Poison", [30, 35, 30, 100, 80]),
    93: ("Haunter", "Ghost", "Poison", [45, 50, 45, 115, 95]),
    94: ("Gengar", "Ghost", "Poison", [60, 65, 60, 130, 110]),
    95: ("Onix", "Rock", "Ground", [35, 45, 160, 30, 70]),
    96: ("Drowzee", "Psychic", None, [60, 48, 45, 43, 42]),
    97: ("Hypno", "Psychic", None, [85, 73, 70, 73, 67]),
    98: ("Krabby", "Water", None, [30, 105, 90, 25, 50]),
    99: ("Kingler", "Water", None, [55, 130, 115, 50, 75]),
    100: ("Voltorb", "Electric", None, [40, 30, 50, 55, 100]),
    101: ("Electrode", "Electric", None, [60, 50, 70, 80, 140]),
    102: ("Exeggcute", "Grass", "Psychic", [60, 40, 80, 60, 40]),
    103: ("Exeggutor", "Grass", "Psychic", [95, 95, 85, 125, 55]),
    104: ("Cubone", "Ground", None, [50, 50, 95, 40, 35]),
    105: ("Marowak", "Ground", None, [60, 80, 110, 50, 45]),
    106: ("Hitmonlee", "Fighting", None, [50, 120, 53, 35, 87]),
    107: ("Hitmonchan", "Fighting", None, [50, 105, 79, 35, 76]),
    108: ("Lickitung", "Normal", None, [90, 55, 75, 60, 30]),
    109: ("Koffing", "Poison", None, [40, 65, 95, 60, 35]),
    110: ("Weezing", "Poison", None, [65, 90, 120, 85, 60]),
    111: ("Rhyhorn", "Ground", "Rock", [80, 85, 95, 30, 25]),
    112: ("Rhydon", "Ground", "Rock", [105, 130, 120, 45, 40]),
    113: ("Chansey", "Normal", None, [250, 5, 5, 35, 50]),
    114: ("Tangela", "Grass", None, [65, 55, 115, 100, 60]),
    115: ("Kangaskhan", "Normal", None, [105, 95, 80, 40, 90]),
    116: ("Horsea", "Water", None, [30, 40, 70, 70, 60]),
    117: ("Seadra", "Water", None, [55, 65, 95, 95, 85]),
    118: ("Goldeen", "Water", None, [45, 67, 60, 50, 63]),
    119: ("Seaking", "Water", None, [80, 92, 65, 65, 68]),
    120: ("Staryu", "Water", None, [30, 45, 55, 70, 85]),
    121: ("Starmie", "Water", "Psychic", [60, 75, 85, 100, 115]),
    122: ("Mr. Mime", "Psychic", None, [40, 45, 65, 100, 90]),
    123: ("Scyther", "Bug", "Flying", [70, 110, 80, 55, 105]),
    124: ("Jynx", "Ice", "Psychic", [65, 50, 35, 115, 95]),
    125: ("Electabuzz", "Electric", None, [65, 83, 57, 95, 105]),
    126: ("Magmar", "Fire", None, [65, 95, 57, 100, 93]),
    127: ("Pinsir", "Bug", None, [65, 125, 100, 55, 85]),
    128: ("Tauros", "Normal", None, [75, 100, 95, 40, 110]),
    129: ("Magikarp", "Water", None, [20, 10, 55, 20, 80]),
    130: ("Gyarados", "Water", "Flying", [95, 125, 79, 60, 81]),
    131: ("Lapras", "Water", "Ice", [130, 85, 80, 85, 60]),
    132: ("Ditto", "Normal", None, [48, 48, 48, 48, 48]),
    133: ("Eevee", "Normal", None, [55, 55, 50, 65, 55]),
    134: ("Vaporeon", "Water", None, [130, 65, 60, 110, 65]),
    135: ("Jolteon", "Electric", None, [65, 65, 60, 110, 130]),
    136: ("Flareon", "Fire", None, [65, 130, 60, 95, 65]),
    137: ("Porygon", "Normal", None, [65, 60, 70, 85, 40]),
    138: ("Omanyte", "Rock", "Water", [35, 40, 100, 90, 35]),
    139: ("Omastar", "Rock", "Water", [70, 60, 125, 115, 55]),
    140: ("Kabuto", "Rock", "Water", [30, 80, 90, 45, 55]),
    141: ("Kabutops", "Rock", "Water", [60, 115, 105, 65, 80]),
    142: ("Aerodactyl", "Rock", "Flying", [80, 105, 65, 60, 130]),
    143: ("Snorlax", "Normal", None, [160, 110, 65, 65, 30]),
    144: ("Articuno", "Ice", "Flying", [90, 85, 100, 95, 85]),
    145: ("Zapdos", "Electric", "Flying", [90, 90, 85, 125, 100]),
    146: ("Moltres", "Fire", "Flying", [90, 100, 90, 125, 90]),
    147: ("Dratini", "Dragon", None, [41, 64, 45, 50, 50]),
    148: ("Dragonair", "Dragon", None, [61, 84, 65, 70, 70]),
    149: ("Dragonite", "Dragon", "Flying", [91, 134, 95, 100, 80]),
    150: ("Mewtwo", "Psychic", None, [106, 110, 90, 154, 130]),
    151: ("Mew", "Psychic", None, [100, 100, 100, 100, 100]),
}

# Petit Cup eligible Pokémon (unevolved, max 6'08" tall, max 44lbs weight)
# Based on Pokémon Stadium Petit Cup rules
PC_ELIGIBLE = [
    1,   # Bulbasaur
    4,   # Charmander  
    7,   # Squirtle
    10,  # Caterpie
    13,  # Weedle
    16,  # Pidgey
    19,  # Rattata
    21,  # Spearow
    23,  # Ekans
    25,  # Pikachu
    27,  # Sandshrew
    29,  # Nidoran♀
    32,  # Nidoran♂
    35,  # Clefairy
    37,  # Vulpix
    39,  # Jigglypuff
    41,  # Zubat
    43,  # Oddish
    46,  # Paras
    50,  # Diglett
    52,  # Meowth
    54,  # Psyduck
    58,  # Growlithe
    60,  # Poliwag
    63,  # Abra
    66,  # Machop
    69,  # Bellsprout
    74,  # Geodude
    81,  # Magnemite
    83,  # Farfetch'd
    90,  # Shellder
    92,  # Gastly
    98,  # Krabby
    100, # Voltorb
    102, # Exeggcute
    104, # Cubone
    109, # Koffing
    116, # Horsea
    118, # Goldeen
    129, # Magikarp
    132, # Ditto
    133, # Eevee
    138, # Omanyte
    140, # Kabuto
    147, # Dratini
]


def get_pokemon_by_dex_number(dex_num: int) -> Tuple[str, str, str, List[int]]:
    """Get Pokémon data by Pokédex number."""
    if dex_num not in GEN1_POKEMON:
        raise ValueError(f"Invalid Pokédex number: {dex_num}")
    
    name, type1, type2, stats = GEN1_POKEMON[dex_num]
    return name, type1, type2 or "", stats


def get_pokemon_by_name(name: str) -> Tuple[int, str, str, List[int]]:
    """Get Pokémon data by name."""
    for dex_num, (poke_name, type1, type2, stats) in GEN1_POKEMON.items():
        if poke_name.lower() == name.lower():
            return dex_num, type1, type2 or "", stats
    
    raise ValueError(f"Pokémon not found: {name}")


def is_pc_eligible(dex_num: int) -> bool:
    """Check if a Pokémon is eligible for Petit Cup."""
    return dex_num in PC_ELIGIBLE


def get_type_effectiveness(attacking_type: str, defending_type: str) -> float:
    """Get type effectiveness multiplier."""
    if attacking_type not in TYPE_CHART:
        return 1.0
    
    return TYPE_CHART[attacking_type].get(defending_type, 1.0)


def get_all_pc_pokemon() -> List[Tuple[int, str, str, str, List[int]]]:
    """Get all Petit Cup eligible Pokémon."""
    pc_pokemon = []
    for dex_num in PC_ELIGIBLE:
        name, type1, type2, stats = GEN1_POKEMON[dex_num]
        pc_pokemon.append((dex_num, name, type1, type2 or "", stats))
    
    return pc_pokemon


def get_pokemon_by_type(poke_type: str) -> List[Tuple[int, str, str, str, List[int]]]:
    """Get all Pokémon that have the specified type."""
    if poke_type not in TYPES:
        raise ValueError(f"Invalid type: {poke_type}")
    
    result = []
    for dex_num, (name, type1, type2, stats) in GEN1_POKEMON.items():
        if type1 == poke_type or type2 == poke_type:
            result.append((dex_num, name, type1, type2 or "", stats))
    
    return result

def get_species_index_by_name(name: str) -> int:
    """Get the Pokédex index by Pokémon name."""
    for dex_num, (poke_name, _, _, _) in GEN1_POKEMON.items():
        if poke_name.lower() == name.lower():
            return dex_num
    raise ValueError(f"Pokémon not found: {name}")

def get_species_name_by_index(idx: int) -> str:
    if  idx > len(GEN1_POKEMON):
        raise ValueError(f"Invalid Pokédex index: {idx}")
    return GEN1_POKEMON[idx][0]

def get_type_index_by_name(name: str) -> int:
    for i, typename in enumerate(TYPES):
        if typename.lower() == name.lower():
            return i
    raise ValueError(f"Invalid typename: {name}")

def get_type_name_by_index(idx: int) -> str:
    if idx < 0 or idx >= len(TYPES):
        raise ValueError(f"Invalid type index: {idx}")
    return TYPES[idx]

if __name__ == "__main__":
    # Example usage
    print("Generation 1 Pokédex Demo")
    print("=" * 30)
    
    # Show all types
    print(f"Types: {', '.join(TYPES)}")
    print()
    
    # Show a few Pokémon
    for dex_num in [1, 25, 150]:
        name, type1, type2, stats = get_pokemon_by_dex_number(dex_num)
        type_str = f"{type1}/{type2}" if type2 else type1
        print(f"#{dex_num:03d} {name} ({type_str}) - Stats: {stats}")
    
    print()
    print(f"Petit Cup eligible Pokémon: {len(PC_ELIGIBLE)}")
    print("First 10 PC Pokémon:")
    for i, dex_num in enumerate(PC_ELIGIBLE[:10]):
        name, type1, type2, stats = get_pokemon_by_dex_number(dex_num)
        type_str = f"{type1}/{type2}" if type2 else type1
        print(f"  #{dex_num:03d} {name} ({type_str})")
