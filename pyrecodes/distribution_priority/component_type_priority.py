from pyrecodes.component.component import Component
from pyrecodes.distribution_priority.distribution_priority import DistributionPriority

class ComponentTypePriority(DistributionPriority):
    """
    | Class that prioritizes components based on their type (i.e., name) as defined in the component library. 
    | Components higher in the system's component list are prioritized among same type components.
    """

    def __init__(self, resource_name: str, parameters, components: list[Component]):
        self.components = components
        self.resource_name = resource_name
        self.set_distribution_priority(parameters)

    def set_distribution_priority(self, parameters):
        categorized_components_dict = self.categorize_components_based_on_type()
        distribution_priority_ids = []
        distribution_priority_demand_types = []
        for component_type_name, component_demand_type in parameters:
            distribution_priority_ids += categorized_components_dict[component_type_name] 
            distribution_priority_demand_types += [component_demand_type for _ in range(len(categorized_components_dict[component_type_name]))]
        self.distribution_priority = distribution_priority_ids, distribution_priority_demand_types
    
    def categorize_components_based_on_type(self) -> dict:
        categorized_components = {}
        for i, component in enumerate(self.components):
            if component.name in categorized_components:
                categorized_components[component.name].append(i)
            else:
               categorized_components[component.name] = [i] 
        return categorized_components     

    def get_component_priorities(self) -> list[int]:  
        return self.distribution_priority