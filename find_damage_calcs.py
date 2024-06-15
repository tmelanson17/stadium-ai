from attrs import define
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import subprocess
from parse_movesets import PokemonParser

Calc = list[int]
MovesetDamage = dict[str, list[Calc]]
PokemonDamage = dict[str, MovesetDamage]
TeamDamage = dict[str, PokemonDamage]

pokemon_table =  PokemonParser("movesets.yaml")

@define
class DamageTable:
    your_team: TeamDamage 
    opposing_team: TeamDamage 

    # TODO : Actually fix the allocation here
    def __init__(self, your_team: list[str], opposing_team: list[str]):
        self.your_team = {poke : {opposing : {} for opposing in opposing_team} for poke in your_team}
        self.opposing_team = {poke : {opposing : {} for opposing in your_team} for poke in opposing_team}

@define
class PokemonState:
    name: str
    level: int
    # TODO: implement
    status: str = None
    boosts: list[int] = None
    
# node query_calc.js  --attacker Gengar --al 50 --defender Chansey --dl 50 --move=Recover 
def calculate_damage(your_pokemon: PokemonState, opposing_pokemon: PokemonState, move: str) -> Calc :
    proc = subprocess.Popen(["node", "query_calc.js", 
                             "--attacker=" + your_pokemon.name, "--attacking_level=" + str(your_pokemon.level), 
                             "--defender=" + opposing_pokemon.name, "--defending_level=" + str(opposing_pokemon.level),
                             "--move=" + move], stdout=subprocess.PIPE)
    exit_code = proc.wait()
    if exit_code != 0:
        return [-1]
    with open("query_result.yaml") as yaml_file:
        yaml_body = yaml.load(yaml_file, Loader=Loader)
        result = yaml_body["damage"]
        return result if type(result) == list else [result,]
    return [-1]


def calculate_damage_table(your_team: list[str], opposing_team: list[str]) -> DamageTable:
    table = DamageTable(your_team, opposing_team)
    for your_pokemon in your_team:
        for opposing_pokemon in opposing_team:
            table.your_team[your_pokemon][opposing_pokemon] = {move : calculate_damage(
                    PokemonState(name=your_pokemon, level=pokemon_table.level(your_pokemon)),
                    PokemonState(name=opposing_pokemon, level=pokemon_table.level(opposing_pokemon)),
                    move) for move in pokemon_table.moveset(your_pokemon)}
            table.opposing_team[opposing_pokemon][your_pokemon] = {move : calculate_damage(
                    PokemonState(name=opposing_pokemon, level=pokemon_table.level(opposing_pokemon)),
                    PokemonState(name=your_pokemon, level=pokemon_table.level(your_pokemon)),
                    move) for move in pokemon_table.moveset(opposing_pokemon)}
    return table

if __name__ == "__main__":
    gengar = PokemonState(name="Gengar", level=50, status=None, boosts=None)
    chansey = PokemonState(name="Chansey", level=50, status=None, boosts=None)
    Calc = calculate_damage(gengar, chansey, "Thunderbolt")
    print(Calc)
    print(len(Calc))
    table = calculate_damage_table(["Gengar", "Chansey", "Starmie"], ["Gengar", "Chansey", "Starmie"])

    print(table.your_team["Gengar"]["Starmie"])

