from pyrecodes.distribution_priority.distribution_priority import DistributionPriority
from pyrecodes.component.component import Component
import copy

class ComponentBasedPriority(DistributionPriority):
    """
    Class that defines resource distribution priority by specifying the priority of each component.
    """

    def __init__(self, resource_name: str, parameters, components: list[Component]):
        self.resource_name = resource_name
        self.components = components
        self.set_distribution_priority(parameters)

    def set_distribution_priority(self, parameters):
        distribution_priority = []
        component_demand_types = []
        temp_components = copy.deepcopy(self.components)
        for component_name, component_locality, component_demand_type in parameters:
            component_position_in_list, temp_components = self.find_component_position(component_name,
                                                                                       component_locality,
                                                                                       temp_components)
            distribution_priority.append(component_position_in_list)
            component_demand_types.append(component_demand_type)
        self.distribution_priority = distribution_priority, component_demand_types

    def find_component_position(self, component_name: str, component_locality: str, temp_components: list
        [Component]) -> 'tuple[int, list[Component]]':
        locality_id = self.get_locality_id_from_string(component_locality)
        for i, component in enumerate(temp_components):
            if self.component_not_already_in_priority_list(component):
                if component.name == component_name and component.locality == locality_id:
                    temp_components[i] = None
                    return i, temp_components
        else:
            raise ValueError(
                f'Component {component_name} | Locality: {locality_id} not found in distribution priorities list.')

    @staticmethod
    def component_not_already_in_priority_list(component):
        return not (component is None)

    @staticmethod
    def get_locality_id_from_string(locality_strings: list[str]) -> list:
        return [int(locality_string.split(' ')[-1]) for locality_string in locality_strings]

    def get_component_priorities(self) -> list[int]:
        return self.distribution_priority
