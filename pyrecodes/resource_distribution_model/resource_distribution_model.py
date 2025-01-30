from abc import ABC, abstractmethod

class ResourceDistributionModel(ABC):
    """
    Interface for the Resource Distribution Model class.
    """

    @abstractmethod
    def set_distribution_time_steps(self, distribution_time_steps: list) -> None:
        pass

    @abstractmethod
    def distribute(self, time_step: int) -> None:
        pass

    @abstractmethod
    def get_total_supply(self, scope: str) -> float:
        pass

    @abstractmethod
    def get_total_demand(self, scope: str) -> float:
        pass

    @abstractmethod
    def get_total_consumption(self, scope: str) -> float:
        pass