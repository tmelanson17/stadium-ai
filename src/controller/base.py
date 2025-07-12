from abc import ABC, abstractmethod
from src.state.pokestate import BattleState

class Controller(ABC):
    @abstractmethod
    def send_command(self, command: str) -> None:
        pass

class Agent(ABC):
    @abstractmethod
    def choose_action(self, battle_state: BattleState) -> str:
        pass