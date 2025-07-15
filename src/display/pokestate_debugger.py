import cv2

from asyncio import Queue
from typing import Dict, Any

from src.display.draw_pokestate import draw_battle_state
from src.state.pokestate import BattleState, create_default_battle_state
from src.utils.battle_state_serialization import BattleStateSerializer
from src.rabbitmq.receive import listen
from src.rabbitmq.topics import BATTLE_STATE_UPDATE, CONTROLLER_EXCHANGE


class PokeStateDebuggerNode:
    def __init__(self, width: int = 1200, height: int = 800):
        self.width = width
        self.height = height
        self.battle_state = create_default_battle_state()
        self.serializer = BattleStateSerializer()
        self.listener = listen(CONTROLLER_EXCHANGE, {
            BATTLE_STATE_UPDATE: self.update_battle_state
        })
    
    def update_battle_state(self, battle_state: Dict[str, Any]) -> None:
        """
        Update the battle state with a new BattleState object.
        """
        self.battle_state = self.serializer.from_dict(battle_state)
        frame = draw_battle_state(self.battle_state, self.width, self.height)
        cv2.imshow("Battle State Debugger", frame)
        cv2.waitKey(1)  # Allow OpenCV to process the window events
        
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PokeState Debugger Node")
    parser.add_argument("--width", type=int, default=1200, help="Width of the display window")
    parser.add_argument("--height", type=int, default=800, help="Height of the display window")
    args = parser.parse_args()  
    debugger_node = PokeStateDebuggerNode(width=args.width, height=args.height)