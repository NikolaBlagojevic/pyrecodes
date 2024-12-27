from pyrecodes.distribution_priority.distribution_priority import DistributionPriority
from pyrecodes.component.component import Component
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
import random
import copy

class RandomPriority(DistributionPriority):
    """
    | Randomly shuffle components for resource distribution. 
    | Keeps resource suppliers on top of the priority list to maximize the consumption of components' supply capacity.
    """

    def __init__(self, resource_name: str, parameters: dict, components: list[Component]):
        self.resource_name = resource_name
        self.components = components
        self.set_distribution_priority(parameters)

    def set_distribution_priority(self, parameters: dict) -> None:
        random.seed(parameters['Seed'])        
        supplier_ids, nonsupplier_ids = self.get_suppliers_id()
        supplier_ids_randomized, supplier_demand_types = self.randomize_ids(supplier_ids,
                                                                                     [StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value])
        nonsupplier_ids_randomized, nonsupplier_demand_types = self.randomize_ids(nonsupplier_ids, parameters['DemandType'])

        self.distribution_priority = supplier_ids_randomized + nonsupplier_ids_randomized, supplier_demand_types + nonsupplier_demand_types

    def get_suppliers_id(self):
        suppliers_id = []
        component_ids = list(range(len(self.components)))
        remaining_components_id = component_ids
        for component_id, component in enumerate(self.components):       
            if component.has_resource_supply(self.resource_name):
                suppliers_id.append(component_id)
                remaining_components_id.remove(component_id)
        return suppliers_id, remaining_components_id
    
    def randomize_ids(self, component_ids: list, demand_types: list) -> tuple:
        """
        The method randomizes component ids. Demand types are in the same order as in the input.
        """
        randomized_priorities = []
        randomized_demand_types = []
        for demand_type in demand_types:
            random.shuffle(component_ids)
            randomized_priorities += copy.deepcopy(component_ids)
            randomized_demand_types += [demand_type for _ in component_ids]
        return randomized_priorities, randomized_demand_types
        
    def get_component_priorities(self) -> list[int]:
        return self.distribution_priority