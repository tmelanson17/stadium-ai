

class StateMachine(Enum):
    OFF=0
    SWITCH=1
    FAST_MOVE=2
    FAST_EFFECT=3
    SLOW_MOVE=4
    SLOW_EFFECT=5


class GameStateUpdater:
    def __init__(self):
        self.state = StateMachine.OFF

    def update_state(self, lines, pokemon_state):
        for line in lines:
            if 
