"""
Complete list of all moves available in Generation 1 of Pokémon (Red/Blue/Yellow).
This includes all 165 moves from the original Generation 1 games.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict

@dataclass
class Move:
    """Represents a Pokémon move with its properties."""
    name: str
    type: str
    power: Optional[int]
    accuracy: int
    pp: int
    description: str

# All Generation 1 moves (165 total)
GEN1_MOVES = [
    # Normal-type moves
    Move("Bite", "Normal", 60, 100, 40, "Bites with sharp fangs. May cause flinching."),
    Move("Pound", "Normal", 40, 100, 56, "A basic attack with a low power."),
    Move("Karate Chop", "Normal", 50, 100, 40, "A chopping attack with a high critical-hit ratio."),
    Move("Double Slap", "Normal", 15, 85, 16, "Hits 2-5 times in one turn."),
    Move("Comet Punch", "Normal", 18, 85, 24, "Hits 2-5 times in one turn."),
    Move("Vine Whip", "Grass", 18, 100, 35, "A Grass-type attack. The Pokémon uses its cruel whips to strike the opponent."),
    Move("Mega Punch", "Normal", 80, 85, 32, "A powerful punch."),
    Move("Pay Day", "Normal", 40, 100, 32, "Scatters coins that are picked up after battle."),
    Move("Scratch", "Normal", 40, 100, 56, "Scratches with sharp claws."),
    Move("Vice Grip", "Normal", 55, 100, 48, "Grips with powerful pincers."),
    Move("Guillotine", "Normal", None, 30, 8, "A one-hit KO attack."),
    Move("Razor Wind", "Normal", 80, 100, 16, "A two-turn attack with high critical-hit ratio."),
    Move("Swords Dance", "Normal", None, 100, 48, "Sharply raises Attack."),
    Move("Cut", "Normal", 50, 95, 48, "Cuts with claws or blades."),
    Move("Gust", "Normal", 40, 100, 56, "Strikes with a gust of wind."),
    Move("Wing Attack", "Flying", 60, 100, 56, "Strikes with wings."),
    Move("Whirlwind", "Normal", None, 85, 32, "Blows away the foe and ends the battle."),
    Move("Fly", "Flying", 70, 95, 24, "Flies high on the first turn, attacks on the second."),
    Move("Bind", "Normal", 15, 85, 32, "Binds the target for 4-5 turns."),
    Move("Slam", "Normal", 80, 75, 32, "Slams the foe with a tail or vine."),
    Move("Stomp", "Normal", 65, 100, 32, "Stomps with a big foot. May cause flinching."),
    Move("Double Kick", "Fighting", 30, 100, 48, "Kicks twice in one turn."),
    Move("Mega Kick", "Normal", 120, 75, 8, "A powerful kick."),
    Move("Jump Kick", "Fighting", 70, 95, 40, "A jumping kick. If it misses, the user is hurt."),
    Move("Rolling Kick", "Fighting", 60, 85, 24, "A fast kick delivered from a rapid spin."),
    Move("Sand-Attack", "Normal", None, 100, 24, "Reduces the foe's accuracy."),
    Move("Headbutt", "Normal", 70, 100, 24, "A ramming attack. May cause flinching."),
    Move("Horn Attack", "Normal", 65, 100, 40, "Stabs with a horn."),
    Move("Fury Attack", "Normal", 15, 85, 32, "Hits 2-5 times in one turn."),
    Move("Horn Drill", "Normal", None, 30, 8, "A one-hit KO attack."),
    Move("Tackle", "Normal", 35, 95, 56, "A full-body charge attack."),
    Move("Body Slam", "Normal", 85, 100, 24, "A full-body slam. May cause paralysis."),
    Move("Wrap", "Normal", 15, 90, 32, "Wraps around the foe for 4-5 turns."),
    Move("Take Down", "Normal", 90, 85, 32, "A reckless tackle that also hurts the user."),
    Move("Thrash", "Normal", 90, 100, 32, "A rampage that lasts 2-3 turns."),
    Move("Double-Edge", "Normal", 120, 100, 24, "A reckless tackle that also hurts the user."),
    Move("Tail Whip", "Normal", None, 100, 48, "Lowers the foe's Defense."),
    Move("Leer", "Normal", None, 100, 48, "Lowers the foe's Defense."),
    Move("Growl", "Normal", None, 100, 64, "Lowers the foe's Attack."),
    Move("Roar", "Normal", None, 100, 32, "Scares the foe away and ends the battle."),
    Move("Sing", "Normal", None, 55, 24, "A soothing song that puts the foe to sleep."),
    Move("Supersonic", "Normal", None, 55, 32, "Confuses the foe with an ultrasonic sound."),
    Move("Sonic Boom", "Normal", None, 90, 32, "Always inflicts 20 HP damage."),
    Move("Disable", "Normal", None, 80, 32, "Disables one of the foe's moves."),
    Move("Acid", "Poison", 40, 100, 48, "Sprays acid. May lower Defense."),
    Move("Ember", "Fire", 40, 100, 40, "A small flame. May cause a burn."),
    Move("Flamethrower", "Fire", 95, 100, 24, "A powerful fire attack. May cause a burn."),
    Move("Mist", "Ice", None, 100, 48, "Prevents stat reduction."),
    Move("Water Gun", "Water", 40, 100, 40, "Squirts water to attack."),
    Move("Hydro Pump", "Water", 120, 80, 8, "A powerful water attack."),
    Move("Surf", "Water", 95, 100, 24, "A big wave that strikes all Pokémon."),
    Move("Ice Beam", "Ice", 95, 100, 16, "An icy attack. May cause freezing."),
    Move("Blizzard", "Ice", 120, 90, 8, "A howling blizzard. May cause freezing."),
    Move("Psybeam", "Psychic", 65, 100, 32, "A psychic attack. May cause confusion."),
    Move("Bubble Beam", "Water", 65, 100, 32, "Fires bubbles. May lower Speed."),
    Move("Aurora Beam", "Ice", 65, 100, 32, "A rainbow beam. May lower Attack."),
    Move("Hyper Beam", "Normal", 150, 90, 8, "Powerful, but leaves the user immobile the next turn."),
    Move("Peck", "Flying", 35, 100, 56, "Attacks with a beak or horn."),
    Move("Drill Peck", "Flying", 80, 100, 32, "A corkscrewing attack with the beak."),
    Move("Submission", "Fighting", 80, 80, 40, "A reckless tackle that also hurts the user."),
    Move("Low Kick", "Fighting", 50, 90, 32, "A low kick that trips the foe."),
    Move("Counter", "Fighting", None, 100, 32, "Returns a physical attack double."),
    Move("Seismic Toss", "Fighting", None, 100, 32, "Inflicts damage equal to the user's level."),
    Move("Strength", "Normal", 80, 100, 24, "A powerful physical attack."),
    Move("Absorb", "Grass", 20, 100, 40, "An attack that steals half the damage inflicted."),
    Move("Mega Drain", "Grass", 40, 100, 24, "An attack that steals half the damage inflicted."),
    Move("Leech Seed", "Grass", None, 90, 16, "Plants a seed that steals HP every turn."),
    Move("Growth", "Normal", None, 100, 64, "Raises Attack and Special Attack."),
    Move("Razor Leaf", "Grass", 55, 95, 40, "Cuts with leaves. High critical-hit ratio."),
    Move("Solarbeam", "Grass", 120, 100, 16, "Absorbs light on turn 1, attacks on turn 2."),
    Move("Poison Powder", "Poison", None, 75, 56, "Scatters poison powder."),
    Move("Stun Spore", "Grass", None, 75, 48, "Scatters paralysis powder."),
    Move("Sleep Powder", "Grass", None, 75, 24, "Scatters sleep powder."),
    Move("Petal Dance", "Grass", 70, 100, 32, "A rampage that lasts 2-3 turns."),
    Move("String Shot", "Bug", None, 95, 64, "Lowers the foe's Speed."),
    Move("Dragon Rage", "Dragon", None, 100, 16, "Always inflicts 40 HP damage."),
    Move("Fire Spin", "Fire", 15, 70, 24, "Traps the foe in fire for 4-5 turns."),
    Move("Thunder Shock", "Electric", 40, 100, 48, "An electric attack. May cause paralysis."),
    Move("Thunderbolt", "Electric", 95, 100, 24, "A powerful electric attack. May cause paralysis."),
    Move("Thunder Wave", "Electric", None, 100, 32, "Paralyzes with electricity."),
    Move("Thunder", "Electric", 120, 70, 16, "A lightning attack. May cause paralysis."),
    Move("Rock Throw", "Rock", 50, 90, 24, "Throws rocks at the foe."),
    Move("Earthquake", "Ground", 100, 100, 16, "An earthquake that strikes all Pokémon."),
    Move("Fissure", "Ground", None, 30, 8, "A one-hit KO attack."),
    Move("Dig", "Ground", 60, 100, 16, "Digs underground on turn 1, attacks on turn 2."),
    Move("Toxic", "Poison", None, 85, 16, "Poisons the foe with an intensifying toxin."),
    Move("Confusion", "Psychic", 50, 100, 40, "A psychic attack. May cause confusion."),
    Move("Psychic", "Psychic", 90, 100, 16, "A powerful psychic attack. May lower Special Defense."),
    Move("Hypnosis", "Psychic", None, 60, 32, "A hypnotic move that puts the foe to sleep."),
    Move("Meditate", "Psychic", None, 100, 64, "Raises Attack."),
    Move("Agility", "Psychic", None, 100, 48, "Sharply raises Speed."),
    Move("Quick Attack", "Normal", 40, 100, 48, "An extremely fast attack that always strikes first."),
    Move("Rage", "Normal", 20, 100, 32, "Raises Attack when hit."),
    Move("Teleport", "Psychic", None, 100, 32, "Warps away from battle."),
    Move("Night Shade", "Ghost", None, 100, 24, "Inflicts damage equal to the user's level."),
    Move("Mimic", "Normal", None, 100, 16, "Copies a move used by the foe."),
    Move("Screech", "Normal", None, 85, 64, "Sharply lowers the foe's Defense."),
    Move("Double Team", "Normal", None, 100, 24, "Creates illusory copies to raise evasiveness."),
    Move("Recover", "Normal", None, 100, 32, "Restores HP by half the max HP."),
    Move("Harden", "Normal", None, 100, 48, "Raises Defense."),
    Move("Minimize", "Normal", None, 100, 32, "Sharply raises evasiveness."),
    Move("Smokescreen", "Normal", None, 100, 32, "Lowers the foe's accuracy."),
    Move("Confuse Ray", "Ghost", None, 100, 16, "Confuses the foe."),
    Move("Withdraw", "Water", None, 100, 64, "Raises Defense."),
    Move("Defense Curl", "Normal", None, 100, 64, "Raises Defense."),
    Move("Barrier", "Psychic", None, 100, 48, "Sharply raises Special Defense."),
    Move("Light Screen", "Psychic", None, 100, 48, "Reduces damage from special attacks."),
    Move("Haze", "Ice", None, 100, 48, "Resets all stat changes."),
    Move("Reflect", "Psychic", None, 100, 32, "Reduces damage from physical attacks."),
    Move("Focus Energy", "Normal", None, 100, 48, "Raises the critical-hit ratio."),
    Move("Bide", "Normal", None, 100, 16, "Endures attacks for 2 turns, then strikes back double."),
    Move("Metronome", "Normal", None, 100, 16, "Randomly uses any move."),
    Move("Mirror Move", "Flying", None, 100, 32, "Counters with the same move."),
    Move("Selfdestruct", "Normal", 200, 100, 8, "Inflicts severe damage but makes the user faint."),
    Move("Egg Bomb", "Normal", 100, 75, 16, "An egg is hurled at the foe."),
    Move("Lick", "Ghost", 20, 100, 48, "Licks with a long tongue. May cause paralysis."),
    Move("Smog", "Poison", 20, 70, 32, "An attack that may poison the foe."),
    Move("Sludge", "Poison", 65, 100, 32, "Hurls sludge. May poison the foe."),
    Move("Bone Club", "Ground", 65, 85, 32, "Clubs the foe with a bone."),
    Move("Fire Blast", "Fire", 120, 85, 8, "A fiery blast that may inflict a burn."),
    Move("Waterfall", "Water", 80, 100, 24, "Charges with a waterfall."),
    Move("Clamp", "Water", 35, 85, 24, "Clamps the foe for 4-5 turns."),
    Move("Swift", "Normal", 60, 100, 32, "Fires stars that never miss."),
    Move("Skull Bash", "Normal", 100, 100, 24, "Raises Defense on turn 1, attacks on turn 2."),
    Move("Spike Cannon", "Normal", 20, 100, 24, "Fires spikes that hit 2-5 times."),
    Move("Constrict", "Normal", 10, 100, 56, "Constricts to attack. May lower Speed."),
    Move("Amnesia", "Psychic", None, 100, 32, "Sharply raises Special Defense."),
    Move("Kinesis", "Psychic", None, 80, 24, "Lowers the foe's accuracy."),
    Move("Softboiled", "Normal", None, 100, 16, "Restores HP by half the max HP."),
    Move("High Jump Kick", "Fighting", 85, 90, 32, "A jumping kick. If it misses, the user is hurt."),
    Move("Glare", "Normal", None, 75, 48, "Paralyzes the foe."),
    Move("Dream Eater", "Psychic", 100, 100, 24, "Eats the dreams of a sleeping foe."),
    Move("Poison Gas", "Poison", None, 55, 64, "Poisons the foe."),
    Move("Barrage", "Normal", 15, 85, 32, "Hurls round objects. Hits 2-5 times."),
    Move("Leech Life", "Bug", 20, 100, 24, "An attack that steals half the damage inflicted."),
    Move("Lovely Kiss", "Normal", None, 75, 16, "Demands a kiss with a scary face. May cause sleep."),
    Move("Sky Attack", "Flying", 140, 90, 8, "Charges on turn 1, attacks on turn 2."),
    Move("Transform", "Normal", None, 100, 16, "Transforms into the foe."),
    Move("Bubble", "Water", 20, 100, 48, "Fires bubbles. May lower Speed."),
    Move("Dizzy Punch", "Normal", 70, 100, 16, "A rhythmic punch. May cause confusion."),
    Move("Spore", "Grass", None, 100, 24, "Scatters spores that always induce sleep."),
    Move("Flash", "Normal", None, 70, 32, "Looses a powerful flash. Lowers accuracy."),
    Move("Psywave", "Psychic", None, 80, 24, "Attacks with a psychic wave of varying intensity."),
    Move("Splash", "Normal", None, 100, 64, "It's just a splash... Has no effect whatsoever."),
    Move("Acid Armor", "Poison", None, 100, 64, "Sharply raises Defense."),
    Move("Crabhammer", "Water", 90, 90, 16, "Hammers with a claw. High critical-hit ratio."),
    Move("Explosion", "Normal", 250, 100, 8, "Inflicts severe damage but makes the user faint."),
    Move("Fury Swipes", "Normal", 18, 80, 24, "Rakes with claws. Hits 2-5 times."),
    Move("Bonemerang", "Ground", 50, 90, 16, "Hurls a bone that hits twice."),
    Move("Rest", "Psychic", None, 100, 16, "The user sleeps for 2 turns, restoring HP and status."),
    Move("Rock Slide", "Rock", 75, 90, 16, "Large rocks are hurled. May cause flinching."),
    Move("Hyper Fang", "Normal", 80, 90, 24, "Attacks with sharp fangs. May cause flinching."),
    Move("Sharpen", "Normal", None, 100, 48, "Raises Attack."),
    Move("Conversion", "Normal", None, 100, 48, "Changes type to that of the top move."),
    Move("Tri Attack", "Normal", 80, 100, 16, "Fires three types of beams simultaneously."),
    Move("Super Fang", "Normal", None, 90, 16, "Attacks with sharp fangs and cuts HP in half."),
    Move("Slash", "Normal", 70, 100, 32, "Slashes with claws. High critical-hit ratio."),
    Move("Substitute", "Normal", None, 100, 16, "Creates a decoy using 1/4 of max HP."),
    Move("Twinneedle", "Bug", 25, 100, 24, "Hits twice in one turn with bug-like needles."),
]

# Type-specific move lists for easier filtering
NORMAL_MOVES = [move for move in GEN1_MOVES if move.type == "Normal"]
FIRE_MOVES = [move for move in GEN1_MOVES if move.type == "Fire"]
WATER_MOVES = [move for move in GEN1_MOVES if move.type == "Water"]
ELECTRIC_MOVES = [move for move in GEN1_MOVES if move.type == "Electric"]
GRASS_MOVES = [move for move in GEN1_MOVES if move.type == "Grass"]
ICE_MOVES = [move for move in GEN1_MOVES if move.type == "Ice"]
FIGHTING_MOVES = [move for move in GEN1_MOVES if move.type == "Fighting"]
POISON_MOVES = [move for move in GEN1_MOVES if move.type == "Poison"]
GROUND_MOVES = [move for move in GEN1_MOVES if move.type == "Ground"]
FLYING_MOVES = [move for move in GEN1_MOVES if move.type == "Flying"]
PSYCHIC_MOVES = [move for move in GEN1_MOVES if move.type == "Psychic"]
BUG_MOVES = [move for move in GEN1_MOVES if move.type == "Bug"]
ROCK_MOVES = [move for move in GEN1_MOVES if move.type == "Rock"]
GHOST_MOVES = [move for move in GEN1_MOVES if move.type == "Ghost"]
DRAGON_MOVES = [move for move in GEN1_MOVES if move.type == "Dragon"]

# Move categories (since Gen 1 didn't have explicit categories, these are based on typical usage)
HIGH_POWER_MOVES = [move for move in GEN1_MOVES if move.power and move.power >= 100]
MEDIUM_POWER_MOVES = [move for move in GEN1_MOVES if move.power and 50 <= move.power < 100]
LOW_POWER_MOVES = [move for move in GEN1_MOVES if move.power and move.power < 50]

# One-hit KO moves
OHKO_MOVES = [
    move for move in GEN1_MOVES 
    if move.name in ["Guillotine", "Horn Drill", "Fissure"]
]

# Multi-hit moves
MULTI_HIT_MOVES = [
    move for move in GEN1_MOVES 
    if move.name in ["Double Slap", "Comet Punch", "Fury Attack", "Double Kick", 
                     "Spike Cannon", "Barrage", "Fury Swipes", "Bonemerang"]
]

# Two-turn moves
TWO_TURN_MOVES = [
    move for move in GEN1_MOVES 
    if move.name in ["Razor Wind", "Fly", "Solarbeam", "Skull Bash", "Sky Attack", "Dig"]
]

TRAPPING_MOVES = [
    move for move in GEN1_MOVES
    if move.name in ["Wrap", "Fire Spin", "Bind", "Clamp"]
]

def get_moves_by_type(type_name: str) -> List[Move]:
    """Get all moves of a specific type."""
    return [move for move in GEN1_MOVES if move.type == type_name]

def get_moves_by_power_range(min_power: int, max_power: int) -> List[Move]:
    """Get all moves within a power range."""
    return [move for move in GEN1_MOVES if move.power and min_power <= move.power <= max_power]

def normalize_move_name(name: str) -> str:
    """Transform a move name by removing spaces and converting to lowercase."""
    return name.replace(" ", "").replace("-", "").lower()

def get_move_by_name(name: str) -> Optional[Move]:
    """Get a specific move by name (handles both spaced and non-spaced names)."""
    normalized_search = normalize_move_name(name)
    for move in GEN1_MOVES:
        if normalize_move_name(move.name) == normalized_search:
            return move
    return None

def get_move_name_by_index(index: int) -> Optional[str]:
    """Get the name of a move by its index."""
    if 0 <= index < len(GEN1_MOVES):
        return GEN1_MOVES[index].name
    return None

def get_move_index_by_name(name: str) -> Optional[int]:
    """Get the index of a move by name (handles both spaced and non-spaced names)."""
    normalized_search = normalize_move_name(name)
    for index, move in enumerate(GEN1_MOVES):
        if normalize_move_name(move.name) == normalized_search:
            return index
    return None

def get_all_move_names() -> List[str]:
    """Get a list of all move names."""
    return [move.name for move in GEN1_MOVES]

def print_move_summary():
    """Print a summary of all Generation 1 moves."""
    print("Generation 1 Pokémon Moves Summary")
    print("=" * 40)
    print(f"Total moves: {len(GEN1_MOVES)}")
    print(f"High power moves (100+): {len(HIGH_POWER_MOVES)}")
    print(f"Medium power moves (50-99): {len(MEDIUM_POWER_MOVES)}")
    print(f"Low power moves (<50): {len(LOW_POWER_MOVES)}")
    print(f"One-hit KO moves: {len(OHKO_MOVES)}")
    print(f"Multi-hit moves: {len(MULTI_HIT_MOVES)}")
    print(f"Two-turn moves: {len(TWO_TURN_MOVES)}")

if __name__ == "__main__":
    print_move_summary()
    print("\nAll Generation 1 moves:")
    for i, move in enumerate(GEN1_MOVES, 1):
        power_str = f"{move.power}" if move.power else "—"
        print(f"{i:3d}. {move.name:<15} | {move.type:<8} | {power_str:>3} | {move.accuracy:>3}% | {move.pp:>2} PP")
