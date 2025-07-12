from typing import Dict, Optional

from src.rabbitmq.receive import listen
from src.utils.battle_state_serialization import BattleStateSerializer
from src.controller.base import Controller, Agent
from src.rabbitmq.topics import CONTROLLER_EXCHANGE, BATTLE_STATE_UPDATE

'''
Service for handling output controls.
'''
class OutputControlService:
    def __init__(self, controller: Controller, agent: Agent):
        self.controller = controller
        self.agent = agent
        self.battle_state = None
        self.serializer = BattleStateSerializer()
        self.callbacks = {
            BATTLE_STATE_UPDATE: self.update,
        }
        listen(CONTROLLER_EXCHANGE, self.callbacks)

    def update(self, battle_state: Dict[str, str]) -> None:
        self.battle_state = self.serializer.from_dict(battle_state)
        action = self.agent.choose_action(self.battle_state)
        print(f"Chosen action: {action}")
        self.controller.send_command(action)


class MockController(Controller):
    def send_command(self, command: str) -> None:
        self.last_command = command
        print(f"MockController sent command: {command}")

if __name__ == "__main__":
    import argparse
    from src.controller.serial_controller import SerialController
    from src.controller.random_agent import RandomAgent

    parser = argparse.ArgumentParser(description="Controller Node")
    parser.add_argument("--port", type=str, help="Serial port to connect to")
    parser.add_argument("--mock", action="store_true", help="Use mock controller for testing")
    parser.add_argument("--baudrate", type=int, default=9600, help="Baud rate for serial communication")
    args = parser.parse_args()

    if args.mock:
        controller = MockController()
    else:
        if not args.port:
            raise ValueError("Port must be specified when using serial controller.")
        controller = SerialController(port=args.port, baudrate=args.baudrate)
    agent = RandomAgent()  # TODO: Replace with actual agent implementation
    service = OutputControlService(controller, agent)
