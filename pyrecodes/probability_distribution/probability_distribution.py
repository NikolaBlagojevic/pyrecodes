"""
Module used to define probability distributions used in pyrecodes.
"""

from abc import ABC, abstractmethod
import math
import numpy as np

class Distribution(ABC):

    @abstractmethod
    def set_parameters(self, parameters: dict) -> None:
        pass

    @abstractmethod
    def sample(self) -> float:
        pass


class Deterministic(Distribution):

    def __init__(self, parameters: dict):
        self.set_parameters(parameters)

    def set_parameters(self, parameters: dict) -> None:
        self.value = parameters['Value']

    def sample(self) -> float:
        return self.value


class Lognormal(Distribution):

    def __init__(self, parameters: dict):
        self.set_parameters(parameters)

    def set_parameters(self, parameters: dict) -> None:
        self.median = parameters['Median']
        self.dispersion = parameters['Dispersion']

    def sample(self) -> float:
        mean_normal = math.log(self.median)
        return np.random.lognormal(mean_normal, self.dispersion)
