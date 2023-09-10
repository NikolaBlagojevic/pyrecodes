from abc import ABC, abstractmethod
from pyrecodes import Component
from pyrecodes import ComponentLibraryCreator
from pyrecodes import ResourceDistributionModel
from pyrecodes import ResilienceCalculator
import json
import copy
import math
import pandas as pd
import geopandas as gpd
import shapely

"""
Module used to create a system based on a system configuration file.

More details coming soon.
"""


class SystemCreator(ABC):
    """
    Abstract class for creating a System from a file
    """

    @abstractmethod
    def setup(self, component_library: ComponentLibraryCreator.ComponentLibraryCreator, file_name: str) -> None:
        pass

    @abstractmethod
    def create_components(self) -> list([Component.Component]):
        pass

    @abstractmethod
    def get_damage_input_type(self) -> str:
        pass

    @abstractmethod
    def get_damage_input_parameters(self) -> dict:
        pass

    @abstractmethod
    def get_resource_distribution_parameters(self) -> dict:
        pass

    @abstractmethod
    def get_resilience_calculators(self) -> list([dict]):
        pass

class ConcreteSystemCreator(SystemCreator):
    """
    Class that implements methods common to all SystemCreator subclasses.
    """

    def __init__(self):
        self.component_library = {}
        self.system_configuration = {}
        self.components = []

    def setup(self, component_library: dict, system_configuration: dict) -> None:
        self.component_library = component_library
        self.system_configuration = system_configuration
        self.set_constants()
       
    def set_constants(self) -> None:
        constants = self.system_configuration.get('Constants', {})
        for constant_label, constant_value in constants.items():
            setattr(self, constant_label, constant_value)
    
    def get_damage_input_type(self) -> str:
        return self.system_configuration['DamageInput']['Type']

    def get_damage_input_parameters(self) -> dict:
        return self.system_configuration['DamageInput']['Parameters']

    def get_resource_distribution_parameters(self) -> dict:
        return self.system_configuration['Resources']
    
    def get_resource_parameters(self, components) -> dict:
        all_resources_parameters = self.get_resource_distribution_parameters()
        transfer_services = self.get_transfer_services(components, all_resources_parameters)
        non_transfer_services = self.get_non_transfer_services(components, all_resources_parameters, transfer_services)
        return {**transfer_services, **non_transfer_services}
    
    def get_transfer_services(self, components: list([Component.Component]), all_resources_parameters: dict) -> dict:
        resources = dict()
        for resource_name, resource_parameters in all_resources_parameters.items():
            if resource_parameters['Group'] == 'TransferService':
                resources[resource_name] = dict()        
                resources[resource_name]['Group'] = resource_parameters['Group']
                resources[resource_name]['DistributionModel'] = self.get_resource_distribution_model(resource_name, resource_parameters, components)                
        return resources
    
    def get_non_transfer_services(self, components: list([Component.Component]), all_resources_parameters: dict, transfer_services: dict) -> dict:
        resources = {}
        for resource_name, resource_parameters in all_resources_parameters.items():
            if resource_parameters['Group'] != 'TransferService':
                resources[resource_name] = dict()        
                resources[resource_name]['Group'] = resource_parameters['Group']
                resources[resource_name]['DistributionModel'] = self.get_resource_distribution_model(resource_name, resource_parameters, components)
                required_transfer_service = resource_parameters['DistributionModel']['Parameters'].get('TransferService', None)
                if required_transfer_service is not None: 
                    resources[resource_name]['DistributionModel'].transfer_service_distribution_model = transfer_services[required_transfer_service]['DistributionModel']
        return resources
    
    def get_resource_distribution_model(self, resource_name: str, resource_parameters: dict, components: list([Component.Component])) -> ResourceDistributionModel:
        target_distribution_model = getattr(ResourceDistributionModel, resource_parameters['DistributionModel']['Type'])
        return target_distribution_model(resource_name, resource_parameters['DistributionModel']['Parameters'], components)
    
    def get_resilience_calculators(self) -> list([ResilienceCalculator.ResilienceCalculator]):
        resilience_calculators = []
        for resilience_calculator_parameters in self.system_configuration.get('ResilienceCalculator', []):
            target_resilience_calculator = getattr(ResilienceCalculator, resilience_calculator_parameters['Type'])
            resilience_calculators.append(target_resilience_calculator(resilience_calculator_parameters['Parameters']))
        return resilience_calculators
    
    def create_components(self) -> list([Component.Component]):
        self.components = []
        for locality, content in self.system_configuration.get("Content", {}).items():
            self.create_components_in_localities(locality, content.get('ComponentsInLocality', {}))
            self.create_components_between_localities(locality, content.get('LinkTo', ()))
        return self.components
    
    def create_components_in_localities(self, locality: str, content: dict) -> None:
        """
        Implemented by subclasses.
        """
        pass

    def create_components_between_localities(self, locality: str, content: dict) -> None:
        """
        Implemented by subclasses.
        """
        pass

    def get_component_object(self, component_type: str) -> Component.Component:
        return copy.deepcopy(self.component_library[component_type])

    def add_component(self, component_object: Component.Component) -> None:
        self.components.append(copy.deepcopy(component_object))
    
    @staticmethod
    def format_locality_id(locality_string) -> int:
        return int(locality_string.split(' ')[-1])   

class JSONSystemCreator(ConcreteSystemCreator):
    """
    Create a System from a JSON file.
    """

    def create_components_in_localities(self, locality: str, content: dict) -> None:
        for component_type, amount in content.items():
            component_object = self.get_component_object(component_type)
            component_object.set_locality([self.format_locality_id(locality)])
            for _ in range(amount):
                self.add_component(component_object)

    def create_components_between_localities(self, locality: str, content: dict) -> None:
        for link_to, link_type_list in content.items():
            for link_type in link_type_list:
                component_object = self.get_component_object(link_type)
                component_object.set_locality([self.format_locality_id(locality), self.format_locality_id(link_to)])
                self.add_component(component_object)

class R2DSystemCreator(ConcreteSystemCreator):
    """
    Create a System based on SimCenter R2D Tool's output files for Example 1.
    """

    def __init__(self) -> None:
        super().__init__()
        self.building_area_per_person = {}
        self.scenario_id = None
        self.component_parameters_setter = None

    def setup(self, component_library: dict, system_configuration: dict) -> None:
        super().setup(component_library, system_configuration)
        self.set_building_area_per_person()
        self.scenario_id = self.system_configuration["DamageInput"]["Parameters"]["ScenarioID"]
        self.set_component_parameters_setter()
        
    def set_building_area_per_person(self) -> None:
        for locality, locality_content in self.system_configuration["Content"].items():
            self.building_area_per_person[locality] = locality_content['ComponentsInLocality']['AreaPerPerson']
    
    def set_component_parameters_setter(self) -> None:
        system_level_data = {key: self.__dict__.get(key, None) for key in R2DResidentialBuildingParametersSetter.SYSTEM_LEVEL_DATA_REQUIRED_FOR_BUILDINGS}
        self.component_parameters_setter = R2DResidentialBuildingParametersSetter(system_level_data)        

    def create_components_in_localities(self, locality: str, content: dict) -> list([Component.Component]):
        self.components += self.create_recovery_resource_suppliers(locality, content)
        self.components += self.create_residential_building_components(locality, content)     

    def create_recovery_resource_suppliers(self, locality: str, content: dict) -> list([Component.Component]):
        suppliers = []
        for component_name in content.get('RecoveryResourceSuppliers', []):
            component = copy.deepcopy(self.component_library[component_name])
            component.set_locality([self.format_locality_id(locality)])
            suppliers.append(component)
        return suppliers

    def create_residential_building_components(self, locality: str, content: dict) -> list([Component.Component]):
        building_info_folder = content['BuildingsInfoFolder']
        building_id_range = range(content['BuildingIDsRange'][0],
                                  content['BuildingIDsRange'][1])
        bounding_box = content['Coordinates']['BoundingBox']
        max_num_buildings = content['MaxNumBuildings']
        num_buildings = 0
        components = []
        for building_id in building_id_range:
            building_data = self.load_building_data(building_id, building_info_folder)
            building_location = self.get_building_location(building_data)
            if self.building_location_inside_bounding_box(building_location,
                                                          bounding_box) and self.building_is_residential(building_data):
                components.append(self.create_residential_building(locality, building_data))
                num_buildings += 1
                if num_buildings >= max_num_buildings:
                    break
        return components

    def load_building_data(self, building_id: int, building_info_folder: str) -> dict:
        building_json_name = str(building_id) + '-BIM.json'
        building_data = {}
        with open(building_info_folder + str(building_id) + '/' + building_json_name, 'r') as file:
            building_data['Information'] = json.load(file)
        with open(building_info_folder + str(building_id) + '/' + 'DL_summary.csv', 'r') as file:
            building_data['Damage'] = pd.read_csv(file)
        return building_data

    @staticmethod
    def get_building_location(building_data: dict) -> list:
        return [building_data['Information']['GeneralInformation']['Latitude'],
                building_data['Information']['GeneralInformation']['Longitude']]

    @staticmethod
    def building_location_inside_bounding_box(building_location: list, bounding_box: dict) -> bool:
        # TODO: this can be optimized if needed. polygon created only once per locality, building locations in a list for vectorization.
        polygon = shapely.Polygon([(lat, long) for lat, long in zip(bounding_box['Latitude'], bounding_box['Longitude'])])
        building_centroid = shapely.Point(building_location[0], building_location[1])
        return building_centroid.within(polygon)

    @staticmethod
    def building_is_residential(building_data: dict) -> bool:
        return 'RES' in building_data['Information']['GeneralInformation']['OccupancyClass']

    def create_residential_building(self, locality, building_data) -> Component.Component:
        building_DS = self.get_building_damage_state(building_data)        
        component_template = copy.deepcopy(self.component_library[f'DS{building_DS}_ResidentialBuilding'])
        residential_building = self.component_parameters_setter.set_parameters(component_template, locality, building_data, building_DS)
        return residential_building

    def get_building_damage_state(self, building_data: dict) -> int:
        return building_data['Damage']['highest_damage_state/S'][self.scenario_id]

class R2DSystemWithInterfacesCreator(R2DSystemCreator):
    """
    Create a System based on SimCenter R2D Tool's output files for Example 1 with infrastructure interfaces.
    """

    def create_components_in_localities(self, locality: str, content: dict) -> list([Component.Component]):
        super().create_components_in_localities(locality, content)        
        self.components += self.create_infrastructure_service_suppliers(locality, content)
        
    def create_infrastructure_service_suppliers(self, locality: str, content: dict) -> list([Component.Component]):
        suppliers = []
        for interface_dict in content['Infrastructure']:
            component = copy.deepcopy(self.component_library[list(interface_dict.keys())[0]])
            self.set_infrastructure_system_parameters(component, list(interface_dict.values())[0])
            component.set_locality([self.format_locality_id(locality)])
            suppliers.append(component)
        return suppliers
    
    def set_infrastructure_system_parameters(self, component: Component.Component, interface_parameters: dict) -> None:
        component.set_supply_dynamics(interface_parameters)   
        if 'Demand' in interface_parameters:
            self.component_parameters_setter.set_component_operation_demand(component, interface_parameters['Demand']['Resource'], interface_parameters['Demand']['Amount'])
    
class ComponentParametersSetter:
    """
    Class that sets component parameters unique to each component and defined during system creation.
    """

    def set_component_supply(self, component: Component.Component, resource_name: str, 
                             resource_supply_amount: float, 
                             resource_supply_type=Component.StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value) -> None:        
        component_supply = getattr(component, Component.SupplyOrDemand.SUPPLY.value)[resource_supply_type]
        component_supply[resource_name].set_initial_amount(resource_supply_amount)

    def set_component_operation_demand(self, component: Component.Component, resource_name: str, 
                             resource_demand_amount: float) -> None: 
        component_demand = getattr(component, Component.SupplyOrDemand.DEMAND.value)[
                            Component.StandardiReCoDeSComponent.DemandTypes.OPERATION_DEMAND.value]
        component_demand[resource_name].set_initial_amount(resource_demand_amount)
    
    def set_component_recovery_demand(self, component: Component.Component, recovery_activity_name: str, 
                                      resource_name: str, resource_amount: float):
        if recovery_activity_name in component.recovery_model.recovery_activities.keys():
            component.recovery_model.recovery_activities[recovery_activity_name].demand[resource_name].set_initial_amount(
                resource_amount)

class R2DResidentialBuildingParametersSetter(ComponentParametersSetter):
    """
    Class that sets parameters of residential building components as provided in the R2DTool output files
    """

    SYSTEM_LEVEL_DATA_REQUIRED_FOR_BUILDINGS = ['DS4_REPAIR_DURATION', 'MAX_REPAIR_CREW_DEMAND_PER_BUILDING',
                                                'MAX_RESIDENTS_PER_BUILDING', 'REPAIR_CREW_DEMAND_PER_SQFT',
                                                'DEFAULT_REPAIR_DURATION_DICT', 'DEMAND_PER_PERSON', 'HOUSING_RESOURCES',
                                                'building_area_per_person', 'scenario_id']
    
    def __init__(self, system_level_data: dict):
        self.system_level_data = system_level_data

    def set_parameters(self, component: Component.Component, locality: str, building_data: dict, building_DS: int):  
        self.set_building_geometry(component, building_data)      
        self.set_housing_parameters(component, locality)
        self.set_operation_demand_parameters(component, locality, building_data.get('OperationDemandResources', []))
        self.set_repair_parameters(component, building_data, building_DS)       
        component.set_locality([R2DSystemCreator.format_locality_id(locality)])
        return component

    def set_building_geometry(self, component, building_data: dict):
        self.set_building_area(component, building_data)
        self.set_building_footprint(component, building_data)
        self.set_building_num_stories(component, building_data)
    
    def set_building_area(self, component: Component.Component, building_data: dict) -> None:
        component.area = self.get_total_building_area(building_data)

    def set_building_footprint(self, component: Component.Component, building_data: dict) -> None:
        component.footprint = json.loads(building_data['Information']['GeneralInformation']['Footprint'])

    def set_building_num_stories(self, component: Component.Component, building_data: dict) -> None:
        component.num_stories = building_data['Information']['GeneralInformation']['NumberOfStories']

    def get_total_building_area(self, building_data: dict) -> float:
        return building_data['Information']['GeneralInformation']['PlanArea'] * \
            building_data['Information']['GeneralInformation']['NumberOfStories']
    
    def set_housing_parameters(self, component: Component.Component, locality: str):
        building_housing_capacity = self.get_building_housing_capacity(component.area, locality)
        for housing_resource_name in self.system_level_data['HOUSING_RESOURCES']:
            self.set_component_supply(component, housing_resource_name, building_housing_capacity)
            self.set_component_operation_demand(component, housing_resource_name, building_housing_capacity)

    def get_building_housing_capacity(self, building_area: float, locality: str) -> int:        
        building_housing_capacity = min(int(building_area / self.system_level_data['building_area_per_person'][locality]), self.system_level_data['MAX_RESIDENTS_PER_BUILDING'])
        return building_housing_capacity  
    
    def set_operation_demand_parameters(self, component: Component.Component, locality: str, operation_demand_resources: list):
        if self.system_level_data['DEMAND_PER_PERSON'] is not None:
            building_housing_capacity = self.get_building_housing_capacity(component.area, locality)
            # consider only those resources defined in the "DEMAND_PER_PERSON" attribute in the system configuration file
            operation_demand_resources = [resource_name for resource_name in self.system_level_data.get('DEMAND_PER_PERSON', {}).keys()]
            for operation_demand_resource in operation_demand_resources:
                amount = building_housing_capacity*self.system_level_data['DEMAND_PER_PERSON'][operation_demand_resource]
                self.set_component_operation_demand(component, operation_demand_resource, amount)
     
    def set_repair_parameters(self, component: Component.Component, building_data: dict, building_DS: int):
        self.set_repair_demand(component, building_data, building_DS)
        self.set_repair_duration(component, building_data)
        self.set_building_repair_cost(component, building_data)

    def set_repair_demand(self, component: Component.Component, building_data: dict, building_DS: int) -> None:
        if 'Repair' in component.recovery_model.recovery_activities.keys():
            repair_demand = self.get_repair_crew_demand(building_DS, component.area)
            self.set_component_recovery_demand(component, 'Repair', 'RepairCrew', repair_demand)

    def get_repair_crew_demand(self, building_DS: int, building_area: float) -> int:
        repair_crew_demand = math.ceil(building_area / self.system_level_data['REPAIR_CREW_DEMAND_PER_SQFT'].get(f'DS{building_DS}', math.inf))
        return min(self.system_level_data['MAX_REPAIR_CREW_DEMAND_PER_BUILDING'], repair_crew_demand)

    def set_repair_duration(self, component: Component.Component, building_data: dict) -> None:
        if 'Repair' in component.recovery_model.recovery_activities.keys():
            median_repair_duration = self.get_median_repair_duration(building_data)
            repair_duration_dict = copy.deepcopy(self.system_level_data['DEFAULT_REPAIR_DURATION_DICT'])
            repair_duration_dict['Lognormal']['Median'] = median_repair_duration
            component.recovery_model.recovery_activities['Repair'].set_duration(repair_duration_dict)

    def get_median_repair_duration(self, building_data: dict) -> int:
        """
        Get median repair duration from the R2D .csv building file. 
        Note that if the building collapsed, a dummy repair duration of 1 is assigned in R2D.
        In that case, set the repair duration to DS4 duration.
        """
        median_repair_duration = building_data['Damage']['reconstruction/time'][self.system_level_data['scenario_id']]
        if median_repair_duration == 1 and building_data['Damage']['collapses/collapsed'][self.system_level_data['scenario_id']] == 1:
            return self.system_level_data['DS4_REPAIR_DURATION']
        else:
            return median_repair_duration
  
    def set_building_repair_cost(self, component: Component.Component, building_data: dict) -> None:
        repair_cost = building_data['Damage']['reconstruction/cost'][self.system_level_data['scenario_id']]
        financing_activity = component.recovery_model.recovery_activities.get('Financing', None)
        if financing_activity is not None:
            repair_cost_distributed_over_duration = repair_cost / component.recovery_model.recovery_activities['Financing'].duration
        else:
            repair_cost_distributed_over_duration = 0
        self.set_component_recovery_demand(component, 'Financing', 'Money', repair_cost_distributed_over_duration)
        # financing = component.recovery_model.recovery_activities.get('Financing', None)
        # if financing:
        #     repair_cost = building_data['Damage']['reconstruction/cost'][system_level_data['scenario_id']]            
        #     financing.set_demand([{'Resource': 'Money', 'Amount': repair_cost}])

    