from src.controller.serial_controller import SerialController
from src.controller.base import Controller, Agent
from src.controller.random_agent import RandomAgent
from src.controller.controller_node import OutputControlService, MockController
from src.state.pokestate import BattleState

from test.controller.spoof_battle_state import BattleStateSpoofer

class MockAgent(Agent):
    def choose_action(self, battle_state: BattleState) -> str:
        self.battle_state = battle_state
        # Mock action for testing
        return "move 0"
        
    

class TestController:
    def setup_method(self):
        self.controller = MockController()
        self.agent = MockAgent()
        self.service = OutputControlService(self.controller, self.agent)
        self.spoofer = BattleStateSpoofer("test/controller/test_battle_state.yaml")
    
    def test_update_battle_state(self):

        # Act
        self.spoofer.spoof()

        assert self.spoofer.battle_state == self.controller.battle_state

        # Assert
        assert self.controller.last_command == expected_command