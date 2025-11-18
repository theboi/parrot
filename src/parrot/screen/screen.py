from .window_detector import WindowDetector
from abc import ABC, abstractmethod


class Screen(ABC):
    def __init__(self):
        self.detector = WindowDetector()

    def get_bounds(self):
        return self.detector.get_window_bounds(self.pid)

    @property
    @abstractmethod
    def pid(self):
        pass

    # @abstractmethod
    # def capture():
    #   pass

    # @abstractmethod
    # def click(relative_coord: (int, int)):
    #   pass
