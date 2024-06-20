import random

from typing import List, Tuple

from matchups import Matchup
from parse import pokemon_parser

# There's no more than 2 of each type
def type_criteria(pokemon: List[str], parser: pokemon_parser.PokemonParser):
    type_count = dict()
    for p in pokemon:
        type1, type2 = parser.type(p)
        if type1 not in type_count:
            type_count[type1] = 0
        type_count[type1] += 1
        if type2 is not None:
            if type2 not in type_count:
                type_count[type2] = 0
            type_count[type2] += 1
    return all([type_count[typ] <= 2 for typ in type_count])

def choose_random_teams(parser: pokemon_parser.PokemonParser) -> Tuple[List[str], List[str]]:
    pokemon_list = parser.get_pokemon_names()
    team1 = list()
    while len(team1) == 0 or not type_criteria(team1, parser):
        team1 = random.sample(pokemon_list, k=6)
    pokemon_list_without_team1 = [mon for mon in pokemon_list if mon not in team1]
    team2 = list()
    while len(team2) == 0 or not type_criteria(team2, parser):
        team2 = random.sample(pokemon_list_without_team1, k=6)

    return team1, team2


def pick_3(your_team: List[str], opposing_team: List[str], 
           parser: pokemon_parser.PokemonParser, matchup: Matchup):
    matchups = [0 for your_mon in your_team]
    i=0
    for your_mon in your_team:
        for opposing_mon in opposing_team:
            speed_advantage = parser.get_stat(your_mon, pokemon_parser.Stat.SPD) > parser.get_stat(opposing_mon, pokemon_parser.Stat.SPD)
            if matchup.favorable_matchup(your_mon, opposing_mon, speed_advantage):
                matchups[i]+=1
        i+=1
    ratings = list(zip(matchups, your_team))
    print(ratings)
    # So ties aren't broken in obvious way
    random.shuffle(ratings)
    ratings.sort(reverse=True)
    return [name for rating, name in ratings[:3]]




if __name__ == "__main__":
    parser = pokemon_parser.PokemonParser("config/pokemon.yaml")
    team1, team2 = choose_random_teams(parser)
    matchup = Matchup(parser.get_pokemon_names())
    matchup.from_csv("data/nkos.csv")
    print(team1)
    print(pick_3(team1, team2, parser, matchup))
    print(team2)
    print(pick_3(team2, team1, parser, matchup))


    
