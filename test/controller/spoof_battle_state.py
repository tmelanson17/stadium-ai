from src.params.yaml_parser import load_battle_state_from_yaml
from src.rabbitmq.send import publish_message_to_topic
from src.rabbitmq.topics import BATTLE_STATE_UPDATE, CONTROLLER_EXCHANGE
from src.utils.battle_state_serialization import BattleStateSerializer

class BattleStateSpoofer:
    """
    Spoofs publishing the BattleState to RabbitMQ to test the controller.
    """
    
    def __init__(self, path: str):
        self.battle_state = load_battle_state_from_yaml(path)
        self.serializer = BattleStateSerializer()
    
    def spoof(self) -> None:
        """
        Spoofs the BattleState by publishing it to RabbitMQ.
        This is useful for testing scenarios where you want to simulate different battle states.
        """
        # Modify the battle state as needed for testing
        publish_message_to_topic(CONTROLLER_EXCHANGE, BATTLE_STATE_UPDATE, self.serializer.to_dict(self.battle_state))
        
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Battle State Spoofer")
    parser.add_argument("--path", type=str, required=True, help="Path to the YAML file containing the battle state")
    args = parser.parse_args()
    
    spoofer = BattleStateSpoofer(args.path)
    spoofer.spoof()
    print("Battle state spoofed and published to RabbitMQ.")