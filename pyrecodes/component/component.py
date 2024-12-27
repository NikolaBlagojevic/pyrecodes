from abc import ABC, abstractmethod
from enum import Enum

class SupplyOrDemand(Enum):
    """
    Enum Class to specify the strings used for component's supply and demand attributes.
    """
    SUPPLY = 'supply'
    DEMAND = 'demand'

class Component(ABC):
    """
    Interface to define the required methods and properties of a component.
    """
    name: str
    functionality_level: float 
    functional: list[int]
    locality: list
    supply: dict
    demand: dict

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def construct(self, component_name: str, component_parameters: dict) -> None:
        pass

    @abstractmethod
    def set_initial_damage_level(self, damage_level: float) -> None:
        pass

    @abstractmethod
    def get_damage_level(self) -> float:
        pass

    @abstractmethod
    def update(self, time_step: int) -> None:
        pass

    @abstractmethod
    def set_met_demand_for_recovery_activities(self, resource_name: str, percent_of_met_demand: float) -> None:
        pass

    @abstractmethod
    def recover(self) -> None:
        pass

    @abstractmethod
    def update_supply_based_on_unmet_demand(self, percent_of_met_demand: float) -> None:
        pass

    @abstractmethod
    def set_locality(self, locality_id: list) -> None:
        pass

    @abstractmethod
    def set_recovery_time_steps(self, recovery_time_steps: list) -> None:
        pass

    @abstractmethod
    def get_locality(self) -> int:
        pass

    @abstractmethod
    def has_operation_demand(self) -> bool:
        pass

    @abstractmethod
    def has_resource_supply(self, resource_name: str) -> bool:
        pass
    
