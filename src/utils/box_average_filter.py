from collections import deque
from typing import Any, Sequence

from src.state.pokestate_defs import Rectangle

class BoxAverageFilter:
    def __init__(self, window_size: int):
        self.window_size = window_size
        self.values = deque(maxlen=window_size)

    def add(self, value: Rectangle) -> None:
        self.values.append(value)

    def get_average(self) -> Rectangle:
        if not self.values:
            return Rectangle(0, 0, 0, 0)

        x1 = sum(rect.x1 for rect in self.values) // len(self.values)
        y1 = sum(rect.y1 for rect in self.values) // len(self.values)
        x2 = sum(rect.x2 for rect in self.values) // len(self.values)
        y2 = sum(rect.y2 for rect in self.values) // len(self.values)

        return Rectangle(x1, y1, x2, y2)

    def reset(self) -> None:        
        self.values.clear()

    '''
        Determines if the input rectangle is an outlier based on the average of the stored rectangles.
        If the rectangle is significantly different from the average (relative to its size), it is considered an outlier.
    '''
    def is_outlier(self, value: Rectangle, threshold: float = 0.5) -> bool:
        if not self.values or len(self.values) < self.window_size:
            return False

        avg = self.get_average()
        return (abs(value.x1 - avg.x1) > threshold * (avg.x2 - avg.x1) or
                abs(value.y1 - avg.y1) > threshold * (avg.y2 - avg.y1) or
                abs(value.x2 - avg.x2) > threshold * (avg.x2 - avg.x1) or
                abs(value.y2 - avg.y2) > threshold * (avg.y2 - avg.y1))