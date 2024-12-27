from abc import ABC, abstractmethod
from pyrecodes.component.component import Component

class DistributionPriority(ABC):
    """
    Interface for defining component priority for resource distribution.
    """

    @abstractmethod
    def __init__(self, components: list[Component], parameters, resource_name: str):
        pass

    @abstractmethod
    def get_component_priorities(self) -> list[int]:
        pass