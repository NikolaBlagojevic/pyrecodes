from pyrecodes.system_creator.system_creator import SystemCreator
from pyrecodes.component.component import Component
from pyrecodes.resilience_calculator.resilience_calculator import ResilienceCalculator
from pyrecodes.resource_distribution_model.resource_distribution_model import ResourceDistributionModel
from pyrecodes.utilities import get_class, get_locality_coordinates_from_geojson

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

    def create_components(self) -> list[Component]:
        self.components = []
        for locality_name, content in self.system_configuration.get("Content", {}).items():
            locality = {'LocalityName': locality_name, 'Coordinates': self.get_locality_coordinates(content)}
            subsystem_creators = self.get_subsystem_creators(self.component_library, locality, content)
            self.create_components_in_localities(subsystem_creators)
            self.create_components_between_localities(subsystem_creators)
        return self.components
    
    def get_subsystem_creators(self, component_library: dict, locality: dict, content: dict) -> list():
        """
        Create subsystem creators for a locality based on the system configuration file.
        """
        subsystem_creators = []
        for subsystems_list in content['Components'].values():
            for subsystem in subsystems_list: 
                subsystem_content = list(subsystem.values())[0]   
                subsystem_creator_class = get_class(subsystem_content['CreatorFileName'], subsystem_content['CreatorClassName'], 'subsystem_creator')  
                subsystem_creator = subsystem_creator_class(component_library, 
                                                            locality, subsystem_content['Parameters'], 
                                                            self.system_configuration['Constants'], 
                                                            self.system_configuration['DamageInput'])
                subsystem_creators.append(subsystem_creator)
        return subsystem_creators
    
    def create_components_in_localities(self, subsystem_creators: list) -> None:
        """
        Call the create_components_in_localities method of each subsystem creator.
        """        
        for subsystem_creator in subsystem_creators:
            components = subsystem_creator.create_components_in_localities()
            self.components += components

    def create_components_between_localities(self, subsystem_creators: list) -> None:
        """
        Call the create_components_between_localities method of each subsystem creator.
        """
        for subsystem_creator in subsystem_creators:
            components = subsystem_creator.create_components_between_localities()
            self.components += components  
    
    def get_damage_input_type(self) -> str:
        return self.system_configuration['DamageInput']['FileName'], self.system_configuration['DamageInput']['ClassName']

    def get_damage_input_parameters(self) -> dict:
        return self.system_configuration['DamageInput']['Parameters']

    def get_resource_distribution_parameters(self) -> dict:
        return self.system_configuration['Resources']
    
    def get_resource_parameters(self, components) -> dict:
        all_resources_parameters = self.get_resource_distribution_parameters()
        transfer_services = self.get_transfer_services(components, all_resources_parameters)
        non_transfer_services = self.get_non_transfer_services(components, all_resources_parameters, transfer_services)
        return {**transfer_services, **non_transfer_services}
    
    def get_transfer_services(self, components: list[Component], all_resources_parameters: dict) -> dict:
        resources = dict()
        for resource_name, resource_parameters in all_resources_parameters.items():
            if resource_parameters['Group'] == 'TransferService':
                resources[resource_name] = dict()        
                resources[resource_name]['Group'] = resource_parameters['Group']
                resources[resource_name]['DistributionModel'] = self.get_resource_distribution_model(resource_name, resource_parameters, components)                
        return resources
    
    def get_non_transfer_services(self, components: list[Component], all_resources_parameters: dict, transfer_services: dict) -> dict:
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
    
    def get_resource_distribution_model(self, resource_name: str, resource_parameters: dict, components: list[Component]) -> ResourceDistributionModel:
        target_distribution_model = get_class(resource_parameters['DistributionModel']['FileName'], resource_parameters['DistributionModel']['ClassName'], 'resource_distribution_model')
        return target_distribution_model(resource_name, resource_parameters['DistributionModel']['Parameters'], components)
    
    def get_resilience_calculators(self) -> list[ResilienceCalculator]:
        resilience_calculators = []
        for resilience_calculator_parameters in self.system_configuration.get('ResilienceCalculator', []):
            target_resilience_calculator = get_class(resilience_calculator_parameters['FileName'], resilience_calculator_parameters['ClassName'], 'resilience_calculator')
            resilience_calculators.append(target_resilience_calculator(resilience_calculator_parameters['Parameters']))
        return resilience_calculators

    def get_locality_coordinates(self, content) -> dict:
        locality_info = content.get('Coordinates', {})
        if list(locality_info.keys())[0] == 'BoundingBox' or list(locality_info.keys())[0] == 'Centroid':
            return locality_info
        elif list(locality_info.keys())[0] == 'GeoJSON':
            return get_locality_coordinates_from_geojson(locality_info)