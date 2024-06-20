from attrs import define
from enum import Enum
from parse.pokemon_parser import Move
from cv.text_match import StaticMessages, SecondLineMessages, SELF_AFFECT
from typing import List, Tuple, Dict

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
    moves: List[Move] = []
    volatile: VolatileStatus  = VolatileStatus.OK
    substitute: bool = False
    invulnerable: bool = False
    boosts: Dict[Stat, int] = {stat: 0 for stat in Stat}

    def reset(self):
        self.volatile = VolatileStatus.OK
        self.boosts = {stat: 0 for stat in Stat}
        self.substitute = False
        self.invulnerable = False

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
    p1_team: List[PokemonState] 
    p2_team: List[PokemonState]

    def init(self):
        for p in self.p1_team:
            p.reset()
        for p in self.p2_team:
            p.reset()

    def get_active_pokemon(self) -> Tuple[PokemonState]:
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
        print("Setting status")
        print(line1, line1 in SELF_AFFECT)
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
                        


