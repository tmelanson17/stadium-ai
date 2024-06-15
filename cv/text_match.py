from enum import Enum
import sys

def LevenshteinDistance(s: str, t: str) -> int:
  m = len(s)
  n = len(t)
  # for all i and j, d[i,j] will hold the Levenshtein distance between
  # the first i characters of s and the first j characters of t
  d = [[0]*(n+2) for _ in [0]*(m+1)] 
  # source prefixes can be transformed into empty string by
  # dropping all characters
  for i in range(1,m+1):
    d[i][0] = i
 
  # target prefixes can be reached from empty source prefix
  # by inserting every character
  for j in range(1,n+1):
    d[0][j] = j
 
  for j in range(1,n+1):
    for i in range(1,m+1):
      if s[i-1] == t[j-1]:
        substitution_cost = 0
      else:
        substitution_cost = 1

      d[i][j] = min(d[i-1][j] + 1,                        # deletion
                         d[i][j-1] + 1,                   # insertion
                         d[i-1][j-1] + substitution_cost)  # substitution
 
  return d[m][n]


class StaticMessages(Enum):
    NOTVERY = "It's not very effective..."
    SUPER = "It's super effective!"
    SWITCH1 = "OK! Come back!"
    SWITCH2 = "Enough! Come back!"
    CRIT = "Critical hit!"
    MISS = "Its attack missed!"
    DIG = "It dug a hole!"
    FLY = "It flew up high!"
    CONF = "It's confused!"
    STARTCONF = "It became confused!"
    STARTFRZ = "It was frozen solid!"
    STARTPLZ = "It may not attack!"
    STARTSLP = "It fell asleep!"
    STARTBRN = "Burnburnburn" # TODO: What is the actual message
    STATUSFAIL = "But, it failed!"
    STATUSBRN = "Burnburnburn" # TODO: What is the actual message
    PLZ = "It's fully paralyzed!"
    FRZ = "It's frozen solid!"
    PSN = "It's badly poisoned!"
    SLP = "It's fast asleep!"
    REST = "It fell asleep and was healed!"
    WOKE = "It woke up!" # TODO: Double check this one

class SecondLineMessages(Enum):
    STARTFRZ = "It was frozen solid!"
    STARTPLZ = "It may not attack!"
    STARTBRN = "Burnburnburn" # TODO: What is the actual message
    STATUSBRN = "Burnburnburn" # TODO: What is the actual message
    CRIT = "Critical hit!"
    REST = "It regained health!"
    CONF = "It's confused!"
    NOCONF = "It's no longer confused!"

SELF_AFFECT = [StaticMessages.SWITCH1, StaticMessages.SWITCH2, StaticMessages.DIG, StaticMessages.FLY,
               StaticMessages.WOKE, StaticMessages.SLP, StaticMessages.PLZ, StaticMessages.FRZ, StaticMessages.REST,
               SecondLineMessages.REST, SecondLineMessages.NOCONF]


move_used = "%p used %m!"
swap_in = ["Go! %p!", "Get 'em! %p", "Do it! %p"]


def check_closest_message(textbox, pokemon_names, pokemon_config, max_distance = 5):
    messages = textbox.split('\n')
    msg = messages[0].strip()
    min_message = None
    min_distance_so_far = max_distance
    for static_enum in StaticMessages:
        static_msg = static_enum.value
        distance = LevenshteinDistance(msg, static_msg)
        if distance < min_distance_so_far:
            min_distance_so_far = distance
            min_message = static_enum
    for pokemon in pokemon_names:
        pokemon_caps = pokemon.upper()
        for swap_in_message in swap_in:
            completed_message = swap_in_message.replace("%p", pokemon_caps)
            distance = LevenshteinDistance(completed_message, msg)
            if distance < min_distance_so_far:
                min_distance_so_far = distance
                min_message = pokemon

        for move in pokemon_config.moveset(pokemon):
            completed_message = move_used.replace("%p", pokemon_caps)
            completed_message = completed_message.replace("%m", move.upper())
            distance = LevenshteinDistance(completed_message, msg)
            if distance < min_distance_so_far:
                min_distance_so_far = distance
                min_message = completed_message
    min_second_message = None
    if len(messages) > 1:
        for msg in messages[1:]:
            msg = msg.strip()
            if msg is not None and len(msg) > 0:
                print(msg)
                min_distance_second_line = max_distance
                for second_msg in SecondLineMessages:
                    distance = LevenshteinDistance(msg, second_msg.value)
                    if distance < min_distance_second_line:
                        min_second_message = second_msg
                        min_distance_second_line = distance
            if min_second_message is not None:
                break
    return min_message, min_second_message


if __name__ == "__main__":
    print(LevenshteinDistance("kitten", "sitting"))
    print(LevenshteinDistance("Sunday", "Saturday"))
    print(LevenshteinDistance("~£l ECTRODE used THUNDER!", "ELECTRODE used THUNDER!"))
    from parse import parse_movesets
    config = parse_movesets.PokemonParser("config/fake.yaml")
    line1, line2 = check_closest_message("~£l ECTRODE used THUNDER!", config)
    print(line1)
    print(line2)
    line1, line2 = check_closest_message("It flew up high!", config)
    print(line1)
    print(line2)
