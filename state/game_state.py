from attrs import define
from enum import Enum
from typing import List

from parse.pokemon_parser import PokemonParser, Move, Stat
from cv.text_match import StaticMessages, SecondLineMessages, SELF_AFFECT

class Turn(Enum):
    P1=0
    P2=1

class Stat(Enum):
    HP=0
    ATK=1
    DEF=2
    SPC=3
    SPD=4

class Status(Enum):
    OK=0
    Pz=1
    Slp=2
    Fnt=3
    Brn=4
    Frz=5
    Rest1=6
    Rest2=7

class VolatileStatus(Enum):
    OK=0
    Confused=1

@define
class PokemonState:
    hp: int = 0
    full_hp: int = 0
    speed: int = 0
    status: Status = Status.OK
    name: str = ""
    moves: list[Move] = []
    volatile: VolatileStatus  = VolatileStatus.OK
    substitute: bool = False
    invulnerable: bool = False
    recharge: bool = False
    boosts: dict[Stat, int] = {stat: 0 for stat in Stat}

    def reset(self):
        self.volatile = VolatileStatus.OK
        self.boosts = {stat: 0 for stat in Stat}
        self.substitute = False
        self.invulnerable = False
        self.recharge = False

    def assess_faint(self):
        if self.hp == 0:
            self.status = Status.Fnt

    def set_state(self, state):
        if state == StaticMessages.STARTPLZ or state == SecondLineMessages.STARTPLZ:
            self.status = Status.Pz
        elif state == StaticMessages.STARTCONF:
            self.volatile = VolatileStatus.Confused
        elif state == StaticMessages.STARTSLP:
            self.status = Status.Slp
        elif state == StaticMessages.STARTFRZ or state == SecondLineMessages.STARTFRZ:
            self.status = Status.Frz
        elif state == StaticMessages.STARTBRN or state == SecondLineMessages.STARTBRN:
            self.status = Status.Brn
        elif state == SecondLineMessages.NOCONF:
            self.volatile = VolatileStatus.OK
        elif state == StaticMessages.WOKE:
            self.status = Status.OK
        elif state == StaticMessages.DIG or state == StaticMessages.FLY:
            self.invulnerable = True
        print("State is now (status,volatile,inv): ", self.status, self.volatile, self.invulnerable)


def create_game_state():
    state = GameState(
            p1_pokemon_idx=0,
            p2_pokemon_idx=0,
            p1_team = [PokemonState(), PokemonState(), PokemonState()],
            p2_team = [PokemonState(), PokemonState(), PokemonState()])
    state.init()
    return state

@define
class GameState:
    p1_pokemon_idx: int
    p2_pokemon_idx: int
    p1_team: list[PokemonState] 
    p2_team: list[PokemonState]

    def init(self):
        for p in self.p1_team:
            p.reset()
        for p in self.p2_team:
            p.reset()

    def get_active_pokemon(self) -> tuple[PokemonState]:
        return (p1_team[p1_pokemon_idx], p2_team[p2_pokemon])

    def swap_p1_pokemon(self, i_switchin):
        p1_team[p1_pokemon_idx].reset()
        p1_pokemon_idx = i_switchin

    def swap_their_pokemon(self, i_switchin):
        p2_team[p2_pokemon_idx].reset()
        p2_pokemon_idx = i_switchin

    def update_hp(self, hp_p1: int, hp_p2: int):
        p1_team[p1_pokemon_idx].hp = hp_p1
        p1_team[p1_pokemon_idx].assess_faint()
        p2_team[p2_pokemon_idx].hp = hp_p2
        p2_team[p2_pokemon_idx].assess_faint()

    def update_status(self, line1, line2, team1, idx1, team2, idx2):
        if line1 in SELF_AFFECT:
            team1[idx1].set_state(line1)
        # Not self affecting but also static message
        elif type(line1) == StaticMessages or type(line1) == SecondLineMessages:
            team2[idx2].set_state(line1)
        print(line2, line2 in SELF_AFFECT)
        if line2 in SELF_AFFECT: 
            team1[idx1].set_state(line2)
        elif type(line2) == StaticMessages or type(line2) == SecondLineMessages:
            team2[idx2].set_state(line2)

    def update_p1_status(self, line1, line2):
        print("P1 , P2")
        self.update_status(line1, line2, self.p1_team, self.p1_pokemon_idx, self.p2_team, self.p2_pokemon_idx)

    def update_p2_status(self, line1, line2):
        print("P2 , P1")
        self.update_status(line1, line2, self.p2_team, self.p2_pokemon_idx, self.p1_team, self.p1_pokemon_idx)

    def print_active_pokemon_state(self, active_pk):
        print(f"{active_pk.name}")
        print(f"Status: {active_pk.status} - {active_pk.volatile}")
        print(f"HP: {active_pk.hp}/{active_pk.full_hp}")
        print(f"Invulnerable: {active_pk.invulnerable}, Sub: {active_pk.substitute}, Recharge: {active_pk.recharge}")
        print(f"Boosts: {active_pk.boosts}")
        print("Moves")
        for move in active_pk.moves:
            print(f"  - {move}")

    def print_side_pokemon(self, hidden):
        print(f"{hidden.name}")
        print(f"Status: {hidden.status}")
        print(f"HP: {hidden.hp}/{hidden.full_hp}")

    def print_state(self):
        print("==================")
        print("Active Pokemon")
        print("==================")
        self.print_active_pokemon_state(self.p1_team[self.p1_pokemon_idx])
        print("==================")
        self.print_active_pokemon_state(self.p2_team[self.p2_pokemon_idx])
        print("==================")
        print("Full Teams")
        print("==================")
        for mon in self.p1_team:
            self.print_side_pokemon(mon)
        print("==================")
        for mon in self.p2_team:
            self.print_side_pokemon(mon)



def create_pokemon_state(mon: str, pokemon_parser: PokemonParser):
    pokemon_state = PokemonState()
    pokemon_state.full_hp = pokemon_parser.get_stat(mon, Stat.HP)
    pokemon_state.hp = pokemon_state.full_hp
    pokemon_state.speed = pokemon_parser.get_stat(mon, Stat.SPD)
    pokemon_state.moves = pokemon_parser.moveset(mon)
    pokemon_state.name = mon
    return pokemon_state


def create_from_parser(team1: List[str], team2: List[str], pokemon_parser: PokemonParser):
    team1_state = list()
    for mon in team1:
        team1_state.append(create_pokemon_state(mon, pokemon_parser))
    active_idx=0
    team2_state = list()
    for mon in team2:
        team2_state.append(create_pokemon_state(mon, pokemon_parser))
    state = GameState(
    p1_pokemon_idx = active_idx,
    p2_pokemon_idx = active_idx,
    p1_team = team1_state,
    p2_team = team2_state)
    return state


if __name__ == "__main__":
    parser = PokemonParser("config/pokemon.yaml")
    game_state = create_from_parser(["Gengar", "Parasect", "Psyduck"],["Pikachu", "Venonat", "Gyarados"], parser)


    game_state.print_state()
