from pyrecodes.distribution_priority.random_priority import RandomPriority
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.component.infrastructure_interface import InfrastructureInterface
import random
import copy

class RandomPriorityWithPrioritizedInterfaces(RandomPriority):
    """
    | Randomly shuffle components for resource distribution. 
    | Keeps resource suppliers on top of the priority list to maximize the consumption of components' supply capacity. 
    | Prioritized infrastructure interfaces over other components to minimize shutdowns due to infrastructure interdependency effects. 
    """

    def set_distribution_priority(self, parameters: dict) -> None:
        component_ids = list(range(len(self.components)))
        suppliers_ids, remaining_components_id = self.get_suppliers_id()
        interface_ids, remaining_components_id = self.get_infrastructure_interface_id(remaining_components_id)
        random.seed(parameters['Seed'])
        random.shuffle(suppliers_ids)
        supplier_demand_types = [StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value for _ in
                                 suppliers_ids]
        interface_demand_types = [StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value for _ in
                                 interface_ids]
        random_priorities = []
        random_demand_types = []
        for demand_type in parameters['DemandType']:
            random.shuffle(remaining_components_id)
            random_priorities += copy.deepcopy(remaining_components_id)
            random_demand_types = [demand_type for _ in remaining_components_id]

        self.distribution_priority = suppliers_ids + interface_ids + random_priorities, supplier_demand_types + interface_demand_types + random_demand_types

    def get_infrastructure_interface_id(self, component_ids: list[int]):
        interface_ids = []
        remaining_component_ids = copy.deepcopy(component_ids)
        for component_id in component_ids:  
            if isinstance(self.components[component_id], InfrastructureInterface):
                interface_ids.append(component_id)
                remaining_component_ids.remove(component_id)
        return interface_ids, remaining_component_ids