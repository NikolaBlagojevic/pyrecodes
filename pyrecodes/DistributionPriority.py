from abc import ABC, abstractmethod
import random
from pyrecodes import Component
import copy

"""
Module used to define component priority for resource distribution.

More details coming soon.
"""

class DistributionPriority(ABC):
    """
    Abstract class for defining component priority for resource distribution.
    """

    @abstractmethod
    def __init__(self, components: list([Component.Component]), parameters, resource_name: str):
        pass

    @abstractmethod
    def get_component_priorities(self) -> list([int]):
        pass

class ComponentTypeBasedPriority(DistributionPriority):
    """
    Components are prioritized based on their type (i.e., name). Components higher in the system's component list are prioritized among same type components.
    """

    def __init__(self, resource_name: str, parameters, components: list([Component.Component])):
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

    def get_component_priorities(self) -> list([int]):  
        return self.distribution_priority

class SupplierOnlyDistributionPriority(DistributionPriority):
    """
    Find all components that have a supply for a specified resource and only include those components when distributing a resource.
    Used for housing service distribution, as it only considers components with housing supply when distributing housing services. Makes housing distribution faster.
    Considers Operation Demand only.
    """

    def __init__(self, resource_name: str, parameters: dict, components: list([Component.Component])):
        self.resource_name = resource_name
        self.components = components
        self.set_distribution_priority(parameters)

    def set_distribution_priority(self, parameters) -> None:
        residential_building_ids = []
        for component_id, component in enumerate(self.components):
            if component.has_resource_supply(self.resource_name) > 0:
                residential_building_ids.append(component_id)
        self.distribution_priority = residential_building_ids, [
            Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value for _ in residential_building_ids]

    def get_component_priorities(self) -> list([int]):
        return self.distribution_priority


class RandomPriority(DistributionPriority):
    """
    Randomly shuffle components for resource distribution. 
    Keeps resource suppliers on top of the priority list to maximize the consumption of components' supply capacity.
    """

    def __init__(self, resource_name: str, parameters: dict, components: list([Component.Component])):
        self.resource_name = resource_name
        self.components = components
        self.set_distribution_priority(parameters)

    def set_distribution_priority(self, parameters: dict) -> None:
        random.seed(parameters['Seed'])
        component_ids = list(range(len(self.components)))
        supplier_ids, nonsupplier_ids = self.get_suppliers_id(component_ids)
        supplier_ids_randomized, supplier_demand_types = self.randomize_ids(supplier_ids,
                                                                                     [Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value])
        nonsupplier_ids_randomized, nonsupplier_demand_types = self.randomize_ids(nonsupplier_ids, parameters['DemandType'])

        self.distribution_priority = supplier_ids_randomized + nonsupplier_ids_randomized, supplier_demand_types + nonsupplier_demand_types

    def get_suppliers_id(self, component_ids: list([int])):
        suppliers_id = []
        remaining_components_id = component_ids
        for component_id, component in enumerate(self.components):       
            if component.has_resource_supply(self.resource_name):
                suppliers_id.append(component_id)
                remaining_components_id.remove(component_id)
        return suppliers_id, remaining_components_id
    
    def randomize_ids(self, component_ids: list, demand_types: list) -> tuple:
        """
        The method randomizes component ids. Demand types are in the same order as in the input variable.
        """
        randomized_priorities = []
        randomized_demand_types = []
        for demand_type in demand_types:
            random.shuffle(component_ids)
            randomized_priorities += copy.deepcopy(component_ids)
            randomized_demand_types += [demand_type for _ in component_ids]
        return randomized_priorities, randomized_demand_types
        
    def get_component_priorities(self) -> list([int]):
        return self.distribution_priority
    
class RandomPriorityWithPrioritizedInterfaces(RandomPriority):
    """
    Randomly shuffle components for resource distribution. 
    Keeps resource suppliers on top of the priority list to maximize the consumption of components' supply capacity. 
    Prioritized infrastructure interfaces over other components to minimize shutdowns due to infrastructure interdependency effects. 
    """

    def set_distribution_priority(self, parameters: dict) -> None:
        component_ids = list(range(len(self.components)))
        suppliers_ids, remaining_components_id = self.get_suppliers_id(component_ids)
        interface_ids, remaining_components_id = self.get_infrastructure_interface_id(remaining_components_id)
        random.seed(parameters['Seed'])
        random.shuffle(suppliers_ids)
        supplier_demand_types = [Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value for _ in
                                 suppliers_ids]
        interface_demand_types = [Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value for _ in
                                 interface_ids]
        random_priorities = []
        random_demand_types = []
        for demand_type in parameters['DemandType']:
            random.shuffle(remaining_components_id)
            random_priorities += copy.deepcopy(remaining_components_id)
            random_demand_types = [demand_type for _ in remaining_components_id]

        self.distribution_priority = suppliers_ids + interface_ids + random_priorities, supplier_demand_types + interface_demand_types + random_demand_types

    def get_infrastructure_interface_id(self, component_ids: list([int])):
        interface_ids = []
        remaining_component_ids = copy.deepcopy(component_ids)
        for component_id in component_ids:  
            if isinstance(self.components[component_id], Component.InfrastructureInterface):
                interface_ids.append(component_id)
                remaining_component_ids.remove(component_id)
        return interface_ids, remaining_component_ids


class ComponentBasedPriority(DistributionPriority):
    """
    Resource distribution priority of each component are explicitly defined.
    """

    def __init__(self, resource_name: str, parameters, components: list([Component.Component])):
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

    def find_component_position(self, component_name: str, component_locality: str, temp_components: list(
        [Component.Component])) -> 'tuple[int, list([Component.Component])]':
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
    def get_locality_id_from_string(locality_strings: list([str])) -> list:
        return [int(locality_string.split(' ')[-1]) for locality_string in locality_strings]

    def get_component_priorities(self) -> list([int]):
        return self.distribution_priority
