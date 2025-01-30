import pytest
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.system_creator.concrete_system_creator import ConcreteSystemCreator
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.component.building_with_emergency_calls import BuildingWithEmergencyCalls
from pyrecodes.resource_distribution_model.transfer_service_distribution_model_potential_paths import TransferServiceDistributionModelPotentialPaths
from pyrecodes.resource_distribution_model.utility_distribution_model import UtilityDistributionModel 
from pyrecodes.resilience_calculator.recodes_calculator import ReCoDeSCalculator
from pyrecodes.resilience_calculator.nist_goals_calculator import NISTGoalsCalculator

class TestThreeLocalitiesConcreteSystemCreator():

    MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

    @pytest.fixture()
    def system_creator(self):
        return ConcreteSystemCreator()

    @pytest.fixture()
    def component_library(self):
        input_dict = read_json_file(self.MAIN_FILE)
        return main.form_component_library(input_dict)
    
    @pytest.fixture()
    def system_configuration(self) -> dict:
        input_dict = read_json_file(self.MAIN_FILE)
        system_configuration = read_json_file(input_dict['System']['SystemConfigurationFile'])
        return system_configuration
    
    def test_init(self, system_creator):
        assert system_creator.component_library == {}
        assert system_creator.system_configuration == {}
        assert system_creator.components == []
    
    def test_setup(self, system_creator,
                   component_library: dict, system_configuration: dict):
        system_creator.setup(component_library, system_configuration)
        assert isinstance(system_creator.component_library, dict)
        assert isinstance(system_creator.system_configuration, dict)
        assert system_creator.START_TIME_STEP == 0
        assert system_creator.DISASTER_TIME_STEP == 1
        assert system_creator.MAX_TIME_STEP == 500

    def test_get_damage_input_type(self, system_creator,
                                   component_library: dict, system_configuration: dict):
        system_creator.setup(component_library, system_configuration)
        assert system_creator.get_damage_input_type() == ("list_damage_input", "ListDamageInput")

    def test_get_damage_input_parameters(self, system_creator,
                                     component_library: dict, system_configuration: dict):
        system_creator.setup(component_library, system_configuration)
        assert system_creator.get_damage_input_parameters() == [0.0, 0.4, 0.0, 0.0, 0.4, 0.0, 0.0, 0.4, 0.4, 0.0,
                                                                     0.0]
    
    def test_get_resource_distribution_parameters(self, system_creator,
                                                  component_library: dict, system_configuration: dict):
        system_creator.setup(component_library, system_configuration)
        assert len(system_creator.get_resource_distribution_parameters()) == 4
        assert isinstance(system_creator.get_resource_distribution_parameters(), dict)

    def test_get_resource_parameters(self, system_creator,
                                     component_library: dict, system_configuration: dict):
        system_creator.setup(component_library, system_configuration)
        components = system_creator.create_components()
        resource_parameters = system_creator.get_resource_parameters(components)
        assert len(resource_parameters) == 4
        assert isinstance(resource_parameters, dict)
        assert list(resource_parameters.keys()) == ['SuperTransferService', 'ElectricPower', 'CoolingWater', 'Communication']

    def test_get_transfer_services(self, system_creator,
                                   component_library: dict, system_configuration: dict):
        system_creator.setup(component_library, system_configuration)
        components = system_creator.create_components()
        all_resources_parameters = system_creator.get_resource_distribution_parameters()
        transfer_services = system_creator.get_transfer_services(components, all_resources_parameters)
        assert len(transfer_services) == 1
        assert isinstance(transfer_services, dict)
        assert list(transfer_services.keys()) == ['SuperTransferService']
        assert isinstance(transfer_services['SuperTransferService']['DistributionModel'], TransferServiceDistributionModelPotentialPaths)
    
    def test_get_nontransfer_services(self, system_creator,
                                   component_library: dict, system_configuration: dict):
        system_creator.setup(component_library, system_configuration)
        components = system_creator.create_components()
        all_resources_parameters = system_creator.get_resource_distribution_parameters()
        transfer_services = system_creator.get_transfer_services(components, all_resources_parameters)
        nontransfer_services = system_creator.get_non_transfer_services(components, all_resources_parameters, transfer_services)        
        assert len(nontransfer_services) == 3
        assert isinstance(nontransfer_services, dict)
        assert list(nontransfer_services.keys()) == ['ElectricPower', 'CoolingWater', 'Communication']
        assert isinstance(nontransfer_services['ElectricPower']['DistributionModel'], UtilityDistributionModel)
        assert isinstance(nontransfer_services['ElectricPower']['DistributionModel'].transfer_service_distribution_model, TransferServiceDistributionModelPotentialPaths)
        assert isinstance(nontransfer_services['CoolingWater']['DistributionModel'], UtilityDistributionModel)
        assert isinstance(nontransfer_services['CoolingWater']['DistributionModel'].transfer_service_distribution_model, TransferServiceDistributionModelPotentialPaths)
        assert isinstance(nontransfer_services['Communication']['DistributionModel'], UtilityDistributionModel)
    
    def test_get_resilience_calculators(self, system_creator,
                                        component_library: dict, system_configuration: dict):
        system_creator.setup(component_library, system_configuration)
        resilience_calculators = system_creator.get_resilience_calculators()
        assert len(resilience_calculators) == 2
        assert isinstance(resilience_calculators, list)
        assert isinstance(resilience_calculators[0], ReCoDeSCalculator)
        assert isinstance(resilience_calculators[1], NISTGoalsCalculator)

    def test_add_components_empty(self, system_creator,
                                  component_library: dict, system_configuration: dict):
        system_creator.setup(component_library, system_configuration)
        assert system_creator.components == []
    
    def test_create_components_between_localities(self, system_creator,
                                                            component_library: dict, system_configuration: dict):
        system_creator.setup(component_library, system_configuration)
        localities = ['Locality 1', 'Locality 2', 'Locality 3']
        target_start_end_localities = [[[1, 2], [1, 3]], [[2, 1], [2, 3]], [[3, 1], [3, 2]]]
        for locality_name, target_start_end_locality in zip(localities, target_start_end_localities):
            system_creator.components = []
            content = system_configuration['Content'][locality_name]
            locality = {'LocalityName': locality_name, 'Coordinates': system_creator.get_locality_coordinates(content)}
            subsystem_creators = system_creator.get_subsystem_creators(component_library, locality, content)
            system_creator.create_components_between_localities(subsystem_creators)
            assert len(system_creator.components) == 2
            assert isinstance(system_creator.components[0], StandardiReCoDeSComponent)
            assert isinstance(system_creator.components[1], StandardiReCoDeSComponent)
            assert system_creator.components[0].locality == target_start_end_locality[0]
            assert system_creator.components[1].locality == target_start_end_locality[1]

    def test_create_components_in_localities_locality_1(self, system_creator,
                                                        component_library: dict, system_configuration: dict):
        system_creator.setup(component_library, system_configuration)                                                        
        locality_name = 'Locality 1'
        content = system_configuration['Content'][locality_name]
        locality = {'LocalityName': locality_name, 'Coordinates': system_creator.get_locality_coordinates(content)}
        subsystem_creators = system_creator.get_subsystem_creators(component_library, locality, content)
        system_creator.create_components_in_localities(subsystem_creators)       
        
        assert len(system_creator.components) == 2
        assert isinstance(system_creator.components[0], StandardiReCoDeSComponent)
        assert isinstance(system_creator.components[1], StandardiReCoDeSComponent)
        assert system_creator.components[0].name == 'ElectricPowerPlant'
        assert system_creator.components[0].locality == [1]
        assert system_creator.components[1].name == 'BaseTransceiverStation_1'
        assert system_creator.components[1].locality == [1]
        
    
    def test_create_components_in_localities_locality_2(self, system_creator,
                                                        component_library: dict, system_configuration: dict):
        system_creator.setup(component_library, system_configuration)                                                        
        locality_name = 'Locality 2'
        content = system_configuration['Content'][locality_name]
        locality = {'LocalityName': locality_name, 'Coordinates': system_creator.get_locality_coordinates(content)}
        subsystem_creators = system_creator.get_subsystem_creators(component_library, locality, content)
        system_creator.create_components_in_localities(subsystem_creators)       
        
        assert len(system_creator.components) == 1
        assert isinstance(system_creator.components[0], StandardiReCoDeSComponent)
        assert system_creator.components[0].name == 'CoolingWaterFacility'
        assert system_creator.components[0].locality == [2]

    def test_create_components_in_localities_locality_3(self, system_creator,
                                                        component_library: dict, system_configuration: dict):
        system_creator.setup(component_library, system_configuration)                                                        
        locality_name = 'Locality 3'
        content = system_configuration['Content'][locality_name]
        locality = {'LocalityName': locality_name, 'Coordinates': system_creator.get_locality_coordinates(content)}
        subsystem_creators = system_creator.get_subsystem_creators(component_library, locality, content)
        system_creator.create_components_in_localities(subsystem_creators)       
        
        assert len(system_creator.components) == 2
        assert system_creator.components[0].name == 'BaseTransceiverStation_2'
        assert system_creator.components[0].locality == [3]
        assert isinstance(system_creator.components[1], BuildingWithEmergencyCalls)
        assert system_creator.components[1].name == 'BuildingStockUnit'
        assert system_creator.components[1].locality == [3]        
    
    def test_create_components_num_components_created(self, system_creator,
                                                        component_library: dict, system_configuration: dict):
        system_creator.setup(component_library, system_configuration)                                                        
        system_creator.create_components()
        assert len(system_creator.components) == 11