from abc import ABC, abstractmethod

class DamageInput(ABC):
    """
    Class that allows for different methods for providing initial damage information to the system class
    """

    @abstractmethod
    def __init__(self, parameters: dict, system) -> None:
        pass

    @abstractmethod
    def set_initial_damage(self, components: list) -> None:
        pass 