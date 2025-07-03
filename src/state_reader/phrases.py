from enum import Enum
from typing import Tuple, Any, Dict, Optional
from rapidfuzz import process, fuzz

from src.state.pokestate_defs import Status
from src.state.pokestate import MoveState, BattleState
from src.state.gen1_moves import TRAPPING_MOVES, TWO_TURN_MOVES, normalize_move_name


class Messages(Enum):
    """Enum containing all possible battle messages that can be recognized."""
    # No effect messages
    NOT_VERY_EFFECTIVE = "It's not very effective..."
    SUPER_EFFECTIVE = "It's super effective!"
    OK_COME_BACK = "OK! Come back!"
    ENOUGH_COME_BACK = "Enough! Come back!"
    CRITICAL_HIT = "Critical hit!"
    ATTACK_MISSED = "Its attack missed!"
    ATTACKED_ITSELF = "It attacked itself!"
    SUCKED_HP = "It sucked HP!"
    FAILED = "But, it failed!"
    FLINCH = "Flinch???"  # TODO: What is the flinch message?
    REGAINED_HEALTH = "It regained health!"
    
    # Actor effect messages
    FLEW_UP_HIGH = "It flew up high!"
    CONFUSED = "It's confused!"
    NO_LONGER_CONFUSED = "It's no longer confused!"
    FULLY_PARALYZED = "It's fully paralyzed!"
    FAST_ASLEEP = "It's fast asleep!"
    FELL_ASLEEP_HEALED = "It fell asleep and was healed!"
    GAINED_ARMOR = "It gained armor!"
    PROTECTED_SPECIAL = "It's protected from SPECIAL attacks!"
    WOKE_UP = "It woke up!"
    
    # Receiver effect messages
    WAS_BURNED = "It was burned!"
    FROZEN_SOLID = "It was frozen solid!"
    BECAME_CONFUSED = "It became confused!"
    BADLY_POISONED = "It's badly poisoned!"
    FELL_ASLEEP = "It fell asleep!"
    MAY_NOT_ATTACK = "It may not attack!"
    
    # Stat change messages
    ATTACK_INCREASED = "ATTACK increased!"
    ATTACK_GREATLY_INCREASED = "ATTACK greatly increased!"
    DEFENSE_INCREASED = "DEFENSE increased!"
    DEFENSE_GREATLY_INCREASED = "DEFENSE greatly increased!"
    SPECIAL_INCREASED = "SPECIAL increased!"
    SPECIAL_GREATLY_INCREASED = "SPECIAL greatly increased!"
    SPEED_INCREASED = "SPEED increased!"
    SPEED_GREATLY_INCREASED = "SPEED greatly increased!"
    
    ATTACK_FELL = "ATTACK fell!"
    DEFENSE_FELL = "DEFENSE fell!"
    SPECIAL_FELL = "SPECIAL fell!"
    SPEED_FELL = "SPEED fell!"
    
    # Haze message
    ALL_STATUS_ELIMINATED = "All STATUS changes were eliminated!"


no_effect_messages = [
    Messages.NOT_VERY_EFFECTIVE.value,
    Messages.SUPER_EFFECTIVE.value,
    Messages.OK_COME_BACK.value,
    Messages.ENOUGH_COME_BACK.value,
    Messages.CRITICAL_HIT.value,
    Messages.ATTACK_MISSED.value,
    Messages.ATTACKED_ITSELF.value,
    Messages.SUCKED_HP.value,
    Messages.FAILED.value,
    Messages.FLINCH.value,
    Messages.REGAINED_HEALTH.value
]

actor_effect_messages = {
    Messages.FLEW_UP_HIGH.value: ("actor", "two_turn_move", True),
    Messages.CONFUSED.value: ("actor", "confused", True),
    Messages.NO_LONGER_CONFUSED.value: ("actor", "confused", False),
    Messages.FULLY_PARALYZED.value: ("actor", "status", Status.PARALYZED),
    Messages.FAST_ASLEEP.value: ("actor", "status", Status.SLEEP),
    Messages.FELL_ASLEEP_HEALED.value: ("actor", "status", Status.SLEEP),
    Messages.GAINED_ARMOR.value: ("actor", "reflect", True),
    Messages.PROTECTED_SPECIAL.value: ("actor", "light_screen", True),
    Messages.WOKE_UP.value: ("actor", "status", Status.NONE)
}

receiver_effect_messages = {
    Messages.WAS_BURNED.value: ("receiver", "status", Status.BURNED),
    Messages.FROZEN_SOLID.value: ("receiver", "status", Status.FROZEN),
    Messages.BECAME_CONFUSED.value: ("receiver", "confused", True),
    Messages.BADLY_POISONED.value: ("receiver", "status", Status.POISONED),
    Messages.FELL_ASLEEP.value: ("receiver", "status", Status.SLEEP),
    Messages.MAY_NOT_ATTACK.value: ("receiver", "status", Status.PARALYZED),
}

# TODO: We'll ignore HAZE, because it's not possible in Petit Cup and will be confusing to implement.
# But should keep in mind for the future.
# Potentially could just list all of the stat changes, since it's a tuple.
HAZE_MESSAGE = Messages.ALL_STATUS_ELIMINATED.value

MOVE_TEMPLATE = "{} used {}!"

STATS = {"ATTACK": "attack_boost", "DEFENSE": "defense_boost", "SPECIAL": "special_boost", "SPEED": "speed_boost"}
MAGNITUDES = {"greatly ": 2, "": 1}
DIRECTIONS = {"increased": +1, "fell": -1}

SWITCHOUT = "Go! {}!"

def parse_update_message(message: str, battle_state: BattleState, opponent: bool = False):
    message_map: Dict[str, Optional[Tuple]] = {m: None for m in no_effect_messages}
    message_map.update(actor_effect_messages)
    message_map.update(receiver_effect_messages)

    p1 = battle_state.player_team.pk_list[battle_state.player_active_mon]
    p2 = battle_state.opponent_team.pk_list[battle_state.opponent_active_mon]
    if opponent:
        team = battle_state.opponent_team.pk_list
        actor = "opponent"
        receiver = "self"
        self_pokemon = p2
    else:
        team = battle_state.player_team.pk_list
        actor = "self"
        receiver = "opponent"
        self_pokemon = p1

    for stat in STATS:
        for magnitude in MAGNITUDES:
            for direction in DIRECTIONS:
                key_str = f"{stat} {magnitude}{direction}!"
                # TODO: I realize this is not true in later gens, but this will do for now
                message_map[key_str] = (
                    "actor" if direction == "increased" else "receiver",
                    STATS[stat],
                    MAGNITUDES[magnitude]*DIRECTIONS[direction]
                )

    for i, pokemon in enumerate(team):
        if pokemon.name:
            message_map[SWITCHOUT.format(pokemon.name)] = ("actor", "switch", i)
    for move in [self_pokemon.move1, self_pokemon.move2, self_pokemon.move3, self_pokemon.move4]:
        if move and move.name:
            move_name = move.name.upper()
            if self_pokemon.name:
                key_str = MOVE_TEMPLATE.format(self_pokemon.name, move_name.upper())
                if move_name in TRAPPING_MOVES:
                    # TODO: how to reset trapping?
                    message_map[key_str]  = (receiver, "trapped", True)
                elif move_name in TWO_TURN_MOVES:
                    message_map[key_str] = (actor, "two_turn_move", False)
                # TODO: Add light screen / reflect state fields
                else:
                    # No effect other than damange / healing
                    # or is described by the static messages.
                    message_map[key_str] = None
    
    # Fuzzy match the message string against the keys
    result = process.extractOne(message, message_map.keys(), scorer=fuzz.ratio, score_cutoff=70)
    print(f"Result: {result}")
    if result is None:
        return None
    match, _, _ = result
    
    return message_map.get(match, None)
