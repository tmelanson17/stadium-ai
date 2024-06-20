from parse import pokemon_parser
from attrs import define
from analysis.calculate_type_effectiveness import calculate_type_effectiveness

import numpy as np
import random

Boost = dict[pokemon_parser.Stat, int]

LOW_ROLL=217
HIGH_ROLL=255

def calculate_damage(move: pokemon_parser.Move, A: int, D: int, crit: bool, level: int, 
                     stab: bool, effective: int, calc_strongest=False, calc_weakest=False) -> int:
    if move.fixed_damage():
        return level
    crit_boost = 2 if crit or move.high_crit() else 1
    if move.selfdestruct():
        D = D // 2
    if A > 255 or D > 255:
        A = A // 4
        D = D // 4
    damage = ((((2*level*crit_boost)//5+2)*move.power()*A)//D) // 50 + 2
    if stab:
        damage += damage // 2
    if calc_weakest:
        rng = LOW_ROLL
    elif calc_strongest:
        rng = HIGH_ROLL
    else:
        rng = random.randint(LOW_ROLL,HIGH_ROLL) 
    
    if effective >= 0:
        return (damage * effective * rng) // 255
    else:
        return (damage // (-effective) * rng) // 255


def likelihood_ohko(max_damage: int, defending_hp: int, fixed_damage: bool) -> float:
    if fixed_damage:
        return 1.0 if max_damage >= defending_hp else 0.0
    damage_rolls = np.arange(LOW_ROLL, HIGH_ROLL+1) * max_damage // HIGH_ROLL
    return np.sum(damage_rolls >= defending_hp) / (HIGH_ROLL-LOW_ROLL+1)

def likelihood_2hko(max_damage: int, defending_hp: int, fixed_damage: bool) -> float:
    if fixed_damage:
        return 1.0 if max_damage*2 >= defending_hp else 0.0
    damage_rolls = np.arange(LOW_ROLL, HIGH_ROLL+1) * max_damage // HIGH_ROLL
    return np.sum(damage_rolls[np.newaxis,:] + damage_rolls[:,np.newaxis] >= defending_hp) / (HIGH_ROLL - LOW_ROLL + 1)**2

def likelihood_3hko(max_damage: int, defending_hp: int, fixed_damage: bool) -> float:
    if fixed_damage:
        return 1.0 if max_damage*3 >= defending_hp else 0.0
    damage_rolls = np.arange(LOW_ROLL, HIGH_ROLL+1) * max_damage // HIGH_ROLL
    turn1, turn2, turn3 = np.meshgrid(damage_rolls, damage_rolls, damage_rolls)
    return np.sum((turn1 + turn2 + turn3) >= defending_hp) / (HIGH_ROLL - LOW_ROLL + 1)**3

def likelihood_4hko(max_damage: int, defending_hp: int, fixed_damage: bool) -> float:
    if fixed_damage:
        return 1.0 if max_damage*4 >= defending_hp else 0.0
    damage_rolls = np.arange(LOW_ROLL, HIGH_ROLL+1) * max_damage // HIGH_ROLL
    turn1, turn2, turn3, turn4 = np.meshgrid(damage_rolls, damage_rolls, damage_rolls, damage_rolls)
    return np.sum((turn1 + turn2 + turn3 + turn4) >= defending_hp) / (HIGH_ROLL - LOW_ROLL + 1)**4


boost_modification_numerator = [25, 28, 33, 40, 50, 66, 100, 150, 200, 250, 300, 350, 400]
boost_modification_denominator = 100

def modify_stat(base_stat: int, boost: int) -> int:
    return (base_state * boost_modification_numerator[boost+6]) // boost_modification_denominator


def calc_move_damage(
        move_data: pokemon_parser.Move, attacking: str, defending: str, attacking_boost: Boost, defending_boost: Boost, 
        parser: pokemon_parser.PokemonParser, calc_strongest=False, calc_weakest=False) -> int:
    attacking_stat = pokemon_parser.Stat.SPC if move_data.category() == "Special" else pokemon_parser.Stat.ATK
    A = parser.get_stat(attacking, attacking_stat)
    if attacking_stat in attacking_boost:
        attacking_stat = modify_stat(attacking_stat, attacking_boost[attacking_stat])
    defending_stat = pokemon_parser.Stat.SPC if move_data.category() == "Special" else pokemon_parser.Stat.DEF
    if defending_stat in defending_boost:
        defending_stat = modify_stat(defending_stat, defending_boost[defending_stat])
    def_type1, def_type2 = parser.type(defending)
    atk_type1, atk_type2 = parser.type(attacking)
    stab = (atk_type1 == move_data.type()) or (atk_type2 == move_data.type())
    return calculate_damage(
            move_data,
            parser.get_stat(attacking, attacking_stat),
            parser.get_stat(defending, defending_stat),
            False,
            parser.level(attacking),
            stab,
            calculate_type_effectiveness(move_data.type(), def_type1, def_type2),
            calc_strongest=calc_strongest,
            calc_weakest=calc_weakest)


# Get % likelihood from ohko to 4hko
def ko_odds(attacking: str, defending: str, attacking_boost: Boost, defending_boost: Boost,
                     parser: pokemon_parser.PokemonParser, calc_last_resort=False) -> float:
    max_ohko=0
    max_2hko=0
    max_3hko=0
    max_4hko=0
    defending_hp= parser.get_stat(defending, pokemon_parser.Stat.HP)
    for move in parser.moveset(attacking):
        move_data = pokemon_parser.Move(move)
        if not calc_last_resort and move_data.last_resort():
            continue
        damage = calc_move_damage(move_data, attacking, defending, attacking_boost, defending_boost, 
                            parser, calc_strongest=True) 
        max_ohko = max(likelihood_ohko(damage, defending_hp, move_data.fixed_damage()), max_ohko)
        max_2hko = max(likelihood_2hko(damage, defending_hp, move_data.fixed_damage()), max_2hko)
        max_3hko = max(likelihood_3hko(damage, defending_hp, move_data.fixed_damage()), max_3hko)
        max_4hko = max(likelihood_4hko(damage, defending_hp, move_data.fixed_damage()), max_4hko)
    return max_ohko, max_2hko, max_3hko, max_4hko

if __name__ == "__main__":
    print(calculate_damage(
        pokemon_parser.Move("Blizzard"), 160, 92, False, 73, True, 2, calc_strongest=True
    ))
    parser = pokemon_parser.PokemonParser("config/pokemon.yaml")
    print(calc(pokemon_parser.Move("Blizzard"), "Gengar", "Chansey", parser, calc_strongest=True))
