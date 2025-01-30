from abc import ABC, abstractmethod
from pyrecodes.system.system import System

class ResilienceCalculator(ABC):
    """
    Interface for resilience calculators.
    """

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def calculate_resilience(self):
        pass

    @abstractmethod
    def update(self, system: System):
        pass