from parse import pokemon_parser
from simulate_attack import ko_odds
import csv

LIKELY_THRESHOLD=0.6

def calc_ko_ranges(yaml_file):
    parser = pokemon_parser.PokemonParser(yaml_file)
    total_pokemon = parser.get_pokemon_names()
    fieldnames = ["Pokemon",] + total_pokemon
    table1 = []
    table2 = []
    table3 = []
    table4 = []
    nkos = []
    for attacker in total_pokemon: 
        row1 = {"Pokemon": attacker}
        row2 = {"Pokemon": attacker}
        row3 = {"Pokemon": attacker}
        row4 = {"Pokemon": attacker}
        nko_row = {"Pokemon": attacker}
        for defender in total_pokemon:
            defending_hp = pokemon_parser.get_stat(defender, pokemon_parser.Stat.HP)
            row1[defender], row2[defender], row3[defender], row4[defender] = ko_odds(attacker, defender, defending_hp, {}, {}, 
                                               parser)
            # Maxes out at 5
            nko_row[defender] = sum([int(r[defender] < LIKELY_THRESHOLD) for r in [row1, row2, row3, row4]]) + 1
        table1.append(row1)
        table2.append(row2)
        table3.append(row3)
        table4.append(row4)
        nkos.append(nko_row)
    return fieldnames, table1, table2, table3, table4, nkos


class Matchup:
    def __init__(self, pokemon_list):
        self.matchup = dict()
        self.pokemon_list = pokemon_list
        # Initialize table
        for p1 in pokemon_list:
            self.matchup[p1] = {}
            for p2 in pokemon_list:
                self.matchup[p1][p2] = 0

    def from_csv(self, nkos_file):
        with open(nkos_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                for mon in self.pokemon_list:
                    self.matchup[row["Pokemon"]][mon] = int(row[mon])

# Returns true if :
#  - Outspeeds and kos opponent in as many moves as opponent does it (or fewer)
#  - Underspeeds and kos opponent in one less move than the opponent does it (or fewer)
    def favorable_matchup(self, pokemon1_name, pokemon2_name, speed_advantage):
        required_kos = self.matchup[pokemon2_name][pokemon1_name]
        if not speed_advantage:
            required_kos -= 1
        return self.matchup[pokemon1_name][pokemon2_name] <= required_kos
    


if __name__ == "__main__":
    fieldnames, table1, table2, table3, table4, nkos = calc_ko_ranges("config/pokemon.yaml")

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

    with open("data/nkos.csv", 'w') as matchup_file:
        writer = csv.DictWriter(matchup_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in nkos:
            writer.writerow(row)
