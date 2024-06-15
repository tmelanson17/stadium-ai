import os
import yaml
from enum import Enum
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

Moveset = list[str]

class Stat(Enum):
    HP=0
    ATK=1
    DEF=2
    SPC=3
    SPD=4

class Move:
    def __init__(self, name):
        self.name = name
        yaml_filepath = os.path.join("config/moves", name + ".yaml")
        with open(yaml_filepath) as yaml_file:
            self.data = yaml.load(yaml_file, Loader=Loader)

    def healing(self) -> bool:
        return "heal" in self.data["flags"]

    def selfdestruct(self) -> bool:
        return "selfdestruct" in self.data and self.data["selfdestruct"] == "always"

    def last_resort(self) -> bool:
        return self.selfdestruct() or self.name == "Hyper Beam"

    def status(self) -> str:
        return self.data.get("status", None)

    # Secondary effect parsing isn't that great rn.
    def has_secondary(self) -> bool:
        return type(self.data["secondary"]) == list or type(self.data["secondary"]) == dict

    def draining_move(self) -> bool:
        return "drain" in self.data

    def power(self) -> int:
        return self.data["basePower"] 

    def category(self) -> str:
        return self.data["category"]

    def type(self) -> str:
        return self.data["type"]

    def fixed_damage(self) -> bool:
        return "damage" in self.data

    def high_crit(self) -> bool:
        return "critRatio" in self.data and self.data["critRatio"] == 2


class PokemonParser:
    def __init__(self, yaml_filepath: str):
        with open(yaml_filepath) as yaml_file:
            self.yaml = yaml.load(yaml_file, Loader=Loader)

    def level(self, pokemon: str) -> int:
        return self.yaml[pokemon]["level"]

    def moveset(self, pokemon: str) -> Moveset:
        return self.yaml[pokemon]["moves"]

    def get_pokemon_names(self) -> list[str]:
        return [pokemon for pokemon in self.yaml]

    def get_stats(self, pokemon) -> list[int]:
        return self.yaml[pokemon]["stats"]

    def get_stat(self, pokemon, stat: Stat) -> int:
        return self.yaml[pokemon]["stats"][stat.value]

    def type(self, pokemon) -> tuple[str, str]:
        if type(self.yaml[pokemon]["type"]) == str:
            return self.yaml[pokemon]["type"], None
        else:
            return self.yaml[pokemon]["type"][0], self.yaml[pokemon]["type"][1]
        
if __name__ == "__main__":
    bliz = Move("Blizzard")
    print("Blizzard")
    print("bp", bliz.power())
    print("secondary", bliz.has_secondary())
    print("status", bliz.status())
    print("type", blix.type())
