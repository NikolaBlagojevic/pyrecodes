from abc import ABC, abstractmethod

class RecoveryModel(ABC):
    """
    Abstract class representing a recovery model.
    """

    @abstractmethod
    def __init__(self, recovery_model_parameters: dict) -> None:
        pass

    @abstractmethod
    def set_parameters(self, parameters: dict) -> None:
        pass

    @abstractmethod
    def set_initial_damage_level(self, damage_level: float) -> None:
        pass

    @abstractmethod
    def get_damage_level(self) -> None:
        pass

    @abstractmethod
    def set_damage_functionality(self, damage_functionality_relation: dict) -> None:
        pass

    @abstractmethod
    def recover(self, time_step: int) -> None:
        pass

    @abstractmethod
    def get_functionality_level(self) -> float:
        pass

    @abstractmethod
    def get_demand(self) -> dict:
        pass

    @abstractmethod
    def set_recovery_time_steps(self, time_steps: list) -> None:
        pass

    @abstractmethod
    def set_met_demand_for_recovery_activities(self, resource_name: str, percent_of_met_demand: float) -> None:
        pass

    @abstractmethod
    def set_activities_demand_to_met(self) -> None:
        pass