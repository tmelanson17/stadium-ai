from enum import Enum
import numpy as np
import cv2

class GameState(Enum):
    PREGAME=1
    STARTING=2
    DECISION=3
    EXECUTION=4

LIGHT=150
DARK=45

class GameStateMachine:
    def __init__(self, state_change_threshold=1, cooldown=15):
        self.state = GameState.PREGAME
        self.increment_threshold = state_change_threshold
        self.cooldown_threshold = cooldown
        self.i = 0
        self.cooldown = 0

    def check_state(self, img):
        if self.cooldown > 0:
            self.cooldown += 1
            if self.cooldown > self.cooldown_threshold:
                self.i = 0
                self.cooldown = 0
            return
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if self.state == GameState.PREGAME and np.average(img) > LIGHT:
            self.i += 1
            if self.i > 2:
                self.cooldown = 1
                self.state = GameState.STARTING
        elif (self.state == GameState.STARTING or self.state == GameState.EXECUTION) and np.average(img) < DARK:
            self.i += 1
            if self.i >= self.increment_threshold:
                self.cooldown = 1
                self.state = GameState.DECISION
        elif (self.state == GameState.DECISION) and np.average(img) < DARK:
            self.i += 1
            if self.i >= self.increment_threshold:
                self.cooldown = 1
                self.state = GameState.EXECUTION
