"""
Module used to define resources used in the system.

More details coming soon.
"""

from abc import ABC, abstractmethod
from pyrecodes import Relation

class Resource(ABC):
    name: str
    initial_amount: float
    current_amount: float
    component_functionality_to_amount: Relation
    unmet_demand_to_amount: Relation

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


class ConcreteResource(Resource):

    def __init__(self, name: str, parameters: dict, default_relation='Constant') -> None:
        self.name = name
        self.set_initial_amount(parameters.get('Amount', 0.0))
        self.set_functionality_to_amount_relation(parameters.get('FunctionalityToAmountRelation', default_relation))
        self.set_unmet_demand_to_amount_relation(parameters.get('UnmetDemandToAmountRelation', default_relation)) 

    def set_initial_amount(self, amount: float) -> None:
        if self.amount_is_a_positive_number(amount):
            self.initial_amount = amount
            self.current_amount = amount

    def set_current_amount(self, amount: float) -> None:
        if self.amount_is_a_positive_number(amount):
            self.current_amount = amount

    @staticmethod
    def amount_is_a_positive_number(amount) -> bool:
        if amount >= 0:
            return True
        else:
            raise ValueError('Resource amount must be a positive number.')

    def set_relation(self, relation_class_name: str, attribute_name: str) -> None:
        try:
            target_relation = getattr(Relation, relation_class_name)
            setattr(self, attribute_name, target_relation())
        except:
            raise ValueError(f'Relation {relation_class_name} not defined.')

    def set_functionality_to_amount_relation(self, relation_class_name: str) -> None:
        self.set_relation(relation_class_name, 'component_functionality_to_amount')

    def set_unmet_demand_to_amount_relation(self, relation_class_name: str) -> None:
        self.set_relation(relation_class_name, 'unmet_demand_to_amount')

    def update_based_on_component_functionality(self, component_functionality_level: float) -> None:
        self.current_amount = self.initial_amount * self.component_functionality_to_amount.get_output(
            component_functionality_level)

    def update_based_on_unmet_demand(self, percent_of_met_demand: float) -> None:
        reduced_amount = self.initial_amount * self.unmet_demand_to_amount.get_output(percent_of_met_demand)
        if reduced_amount < self.current_amount:
            self.current_amount = reduced_amount   

class NonConsumableResource(ConcreteResource):
    """
    Class to simulate a resource whose supply does not decrease when it is consumed.
    """

    def update_based_on_consumption(self, consumption: float) -> None:
        pass 

class ConsumableResource(ConcreteResource):
    """
    Class to simulate a resource whose supply decreases when it is consumed.

    Both initial and current amounts are reduced by the consumption amount. 

    The reason is that the initial amount represents the amount that the component provides when 
    functionality level is 1 and this value is also decreased for a consumable resource.
    """

    def update_based_on_consumption(self, consumption: float) -> None:
        self.initial_amount = max(self.initial_amount - consumption, 0)
        self.current_amount = max(self.current_amount - consumption, 0)