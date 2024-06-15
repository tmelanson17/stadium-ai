from parse import pokemon_parser
from simulate_attack import ko_odds
import csv

def calc_offensive_matchups(yaml_file):
    parser = pokemon_parser.PokemonParser(yaml_file)
    total_pokemon = parser.get_pokemon_names()
    fieldnames = ["Pokemon",] + total_pokemon
    table1 = []
    table2 = []
    table3 = []
    table4 = []
    for attacker in total_pokemon: 
        row1 = {"Pokemon": attacker}
        row2 = {"Pokemon": attacker}
        row3 = {"Pokemon": attacker}
        row4 = {"Pokemon": attacker}
        for defender in total_pokemon:
            row1[defender], row2[defender], row3[defender], row4[defender] = ko_odds(attacker, defender, {}, {}, 
                                               parser, calc_weakest=True)
        table1.append(row1)
        table2.append(row2)
        table3.append(row3)
        table4.append(row4)
    return fieldnames, table1, table2, table3, table4

if __name__ == "__main__":
    fieldnames, table1, table2, table3, table4 = calc_offensive_matchups("config/pokemon.yaml")

    with open("data/ohkos.csv", 'w') as matchup_file:
        writer = csv.DictWriter(matchup_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in table1:
            writer.writerow(row)
    
    with open("data/2hkos.csv", 'w') as matchup_file:
        writer = csv.DictWriter(matchup_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in table2:
            writer.writerow(row)

    with open("data/3hkos.csv", 'w') as matchup_file:
        writer = csv.DictWriter(matchup_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in table3:
            writer.writerow(row)

    with open("data/4hkos.csv", 'w') as matchup_file:
        writer = csv.DictWriter(matchup_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in table4:
            writer.writerow(row)
