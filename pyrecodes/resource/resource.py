from abc import ABC, abstractmethod
from pyrecodes.relation import relation

class Resource(ABC):
    """
    Interface for a resource class in a component object.    
    """
    name: str
    initial_amount: float
    current_amount: float
    component_functionality_to_amount: relation.Relation
    unmet_demand_to_amount: relation.Relation

    @abstractmethod
    def __init__(self, name: str, amount: float, functionality_to_amount_relation: str,
                 unmet_demand_to_amount_relation: str) -> None:
        pass

    @abstractmethod
    def set_current_amount(self, amount: float) -> None:
        pass

    @abstractmethod
    def update_based_on_component_functionality(self, functionality_level: float) -> None:
        pass

    @abstractmethod
    def update_based_on_unmet_demand(self, percent_of_met_demand: float) -> None:
        pass

    @abstractmethod
    def update_based_on_consumption(self, consumption: float) -> None:
        pass