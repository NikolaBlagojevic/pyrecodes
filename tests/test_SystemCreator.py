import pytest
import math
import copy
from pyrecodes import SystemCreator
from pyrecodes import ComponentLibraryCreator
from pyrecodes import Component
from pyrecodes import ComponentRecoveryModel
from pyrecodes import ResourceDistributionModel
from pyrecodes import ResilienceCalculator
from pyrecodes import main


class TestThreeLocalitiesJSONSystemCreator():
    MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

    @pytest.fixture()
    def json_system_creator(self) -> SystemCreator.SystemCreator:
        return SystemCreator.JSONSystemCreator()

    @pytest.fixture()
    def component_library(self) -> ComponentLibraryCreator.JSONComponentLibraryCreator:
        input_dict = main.read_file(self.MAIN_FILE)
        return main.form_component_library(input_dict)
    
    @pytest.fixture()
    def system_configuration(self) -> dict:
        input_dict = main.read_file(self.MAIN_FILE)
        system_configuration = main.read_file(input_dict['System']['SystemConfigurationFile'])
        return system_configuration
    
    def test_init(self, json_system_creator: SystemCreator.SystemCreator):
        assert json_system_creator.component_library == {}
        assert json_system_creator.system_configuration == {}
        assert json_system_creator.components == []
    
    def test_setup(self, json_system_creator: SystemCreator.SystemCreator,
                   component_library: dict, system_configuration: dict):
        json_system_creator.setup(component_library, system_configuration)
        assert isinstance(json_system_creator.component_library, dict)
        assert isinstance(json_system_creator.system_configuration, dict)
        assert json_system_creator.START_TIME_STEP == 0
        assert json_system_creator.DISASTER_TIME_STEP == 1
        assert json_system_creator.MAX_TIME_STEP == 500

    def test_get_damage_input_type(self, json_system_creator: SystemCreator.SystemCreator,
                                   component_library: dict, system_configuration: dict):
        json_system_creator.setup(component_library, system_configuration)
        assert json_system_creator.get_damage_input_type() == "ListDamageInput"

    def test_get_damage_input_parameters(self, json_system_creator: SystemCreator.SystemCreator,
                                     component_library: dict, system_configuration: dict):
        json_system_creator.setup(component_library, system_configuration)
        assert json_system_creator.get_damage_input_parameters() == [0.0, 0.4, 0.0, 0.0, 0.4, 0.0, 0.0, 0.4, 0.4, 0.0,
                                                                     0.0]
    
    def test_get_resource_distribution_parameters(self, json_system_creator: SystemCreator.SystemCreator,
                                                  component_library: dict, system_configuration: dict):
        json_system_creator.setup(component_library, system_configuration)
        assert len(json_system_creator.get_resource_distribution_parameters()) == 4
        assert isinstance(json_system_creator.get_resource_distribution_parameters(), dict)

    def test_get_resource_parameters(self, json_system_creator: SystemCreator.SystemCreator,
                                     component_library: dict, system_configuration: dict):
        json_system_creator.setup(component_library, system_configuration)
        components = json_system_creator.create_components()
        resource_parameters = json_system_creator.get_resource_parameters(components)
        assert len(resource_parameters) == 4
        assert isinstance(resource_parameters, dict)
        assert list(resource_parameters.keys()) == ['SuperTransferService', 'ElectricPower', 'CoolingWater', 'Communication']
    
    def test_get_transfer_services(self, json_system_creator: SystemCreator.SystemCreator,
                                   component_library: dict, system_configuration: dict):
        json_system_creator.setup(component_library, system_configuration)
        components = json_system_creator.create_components()
        all_resources_parameters = json_system_creator.get_resource_distribution_parameters()
        transfer_services = json_system_creator.get_transfer_services(components, all_resources_parameters)
        assert len(transfer_services) == 1
        assert isinstance(transfer_services, dict)
        assert list(transfer_services.keys()) == ['SuperTransferService']
        assert isinstance(transfer_services['SuperTransferService']['DistributionModel'], ResourceDistributionModel.TransferServiceDistributionModelPotentialPathSets)
    
    def test_get_nontransfer_services(self, json_system_creator: SystemCreator.SystemCreator,
                                   component_library: dict, system_configuration: dict):
        json_system_creator.setup(component_library, system_configuration)
        components = json_system_creator.create_components()
        all_resources_parameters = json_system_creator.get_resource_distribution_parameters()
        transfer_services = json_system_creator.get_transfer_services(components, all_resources_parameters)
        nontransfer_services = json_system_creator.get_non_transfer_services(components, all_resources_parameters, transfer_services)        
        assert len(nontransfer_services) == 3
        assert isinstance(nontransfer_services, dict)
        assert list(nontransfer_services.keys()) == ['ElectricPower', 'CoolingWater', 'Communication']
        assert isinstance(nontransfer_services['ElectricPower']['DistributionModel'], ResourceDistributionModel.UtilityDistributionModel)
        assert isinstance(nontransfer_services['ElectricPower']['DistributionModel'].transfer_service_distribution_model, ResourceDistributionModel.TransferServiceDistributionModelPotentialPathSets)
        assert isinstance(nontransfer_services['CoolingWater']['DistributionModel'], ResourceDistributionModel.UtilityDistributionModel)
        assert isinstance(nontransfer_services['CoolingWater']['DistributionModel'].transfer_service_distribution_model, ResourceDistributionModel.TransferServiceDistributionModelPotentialPathSets)
        assert isinstance(nontransfer_services['Communication']['DistributionModel'], ResourceDistributionModel.UtilityDistributionModel)
    
    def test_get_resilience_calculators(self, json_system_creator: SystemCreator.SystemCreator,
                                        component_library: dict, system_configuration: dict):
        json_system_creator.setup(component_library, system_configuration)
        resilience_calculators = json_system_creator.get_resilience_calculators()
        assert len(resilience_calculators) == 2
        assert isinstance(resilience_calculators, list)
        assert isinstance(resilience_calculators[0], ResilienceCalculator.ReCoDeSResilienceCalculator)
        assert isinstance(resilience_calculators[1], ResilienceCalculator.NISTGoalsResilienceCalculator)

    def test_get_component_object(self, json_system_creator: SystemCreator.SystemCreator,
                                  component_library: dict, system_configuration: dict):
        json_system_creator.setup(component_library, system_configuration)
        component_types = ['ElectricPowerPlant', 'BuildingStockUnit', 'BaseTransceiverStation_1',
                           'BaseTransceiverStation_2', 'CoolingWaterFacility', 'SuperLink']
        for component_type in component_types:
            assert isinstance(json_system_creator.get_component_object(component_type),
                               Component.StandardiReCoDeSComponent)
        
    def test_add_components_empty(self, json_system_creator: SystemCreator.SystemCreator,
                                  component_library: dict, system_configuration: dict):
        json_system_creator.setup(component_library, system_configuration)
        assert json_system_creator.components == []
    
    def test_add_multiple_components(self, json_system_creator: SystemCreator.SystemCreator,
                                  component_library: dict, system_configuration: dict):
        json_system_creator.setup(component_library, system_configuration)
        num_components = 5
        for _ in range(num_components):
            component = json_system_creator.get_component_object('ElectricPowerPlant')
            json_system_creator.add_component(component)
        assert len(json_system_creator.components) == num_components

    def test_format_locality_id(self, json_system_creator: SystemCreator.SystemCreator):
        locality_strings = ['Locality 12', 'Locality 1', 'Locality 312', 'Locality 3124']
        locality_ids = [12, 1, 312, 3124]
        boolean_list = []
        for locality_id, locality_string in zip(locality_ids, locality_strings):
            boolean_list.append(locality_id == json_system_creator.format_locality_id(locality_string))
        assert all(boolean_list) == True
    
    def test_create_components_between_localities(self, json_system_creator: SystemCreator.SystemCreator,
                                                            component_library: dict, system_configuration: dict):
        json_system_creator.setup(component_library, system_configuration)
        localities = ['Locality 1', 'Locality 2', 'Locality 3']
        target_start_end_localities = [[[1, 2], [1, 3]], [[2, 1], [2, 3]], [[3, 1], [3, 2]]]
        for locality, target_start_end_locality in zip(localities, target_start_end_localities):
            content = system_configuration['Content'][locality]['LinkTo']
            json_system_creator.components = []
            json_system_creator.create_components_between_localities(locality, content)
            assert len(json_system_creator.components) == 2
            assert isinstance(json_system_creator.components[0], Component.StandardiReCoDeSComponent)
            assert isinstance(json_system_creator.components[1], Component.StandardiReCoDeSComponent)
            assert json_system_creator.components[0].locality == target_start_end_locality[0]
            assert json_system_creator.components[1].locality == target_start_end_locality[1]

    def test_create_components_in_localities_locality_1(self, json_system_creator: SystemCreator.SystemCreator,
                                                        component_library: dict, system_configuration: dict):
        json_system_creator.setup(component_library, system_configuration)                                                        
        locality = 'Locality 1'
        content = system_configuration['Content'][locality]['ComponentsInLocality']
        json_system_creator.create_components_in_localities(locality, content)       
        
        assert len(json_system_creator.components) == 2
        assert isinstance(json_system_creator.components[0], Component.StandardiReCoDeSComponent)
        assert isinstance(json_system_creator.components[1], Component.StandardiReCoDeSComponent)
        assert json_system_creator.components[0].name == 'BaseTransceiverStation_1'
        assert json_system_creator.components[0].locality == [1]
        assert json_system_creator.components[1].name == 'ElectricPowerPlant'
        assert json_system_creator.components[1].locality == [1]
    
    def test_create_components_in_localities_locality_2(self, json_system_creator: SystemCreator.SystemCreator,
                                                        component_library: dict, system_configuration: dict):
        json_system_creator.setup(component_library, system_configuration)                                                        
        locality = 'Locality 2'
        content = system_configuration['Content'][locality]['ComponentsInLocality']
        json_system_creator.create_components_in_localities(locality, content)       
        
        assert len(json_system_creator.components) == 1
        assert isinstance(json_system_creator.components[0], Component.StandardiReCoDeSComponent)
        assert json_system_creator.components[0].name == 'CoolingWaterFacility'
        assert json_system_creator.components[0].locality == [2]

    def test_create_components_in_localities_locality_3(self, json_system_creator: SystemCreator.SystemCreator,
                                                        component_library: dict, system_configuration: dict):
        json_system_creator.setup(component_library, system_configuration)                                                        
        locality = 'Locality 3'
        content = system_configuration['Content'][locality]['ComponentsInLocality']
        json_system_creator.create_components_in_localities(locality, content)       
        
        assert len(json_system_creator.components) == 2
        assert isinstance(json_system_creator.components[0], Component.BuildingStockUnitWithEmergencyCalls)
        assert json_system_creator.components[0].name == 'BuildingStockUnit'
        assert json_system_creator.components[0].locality == [3]
        assert json_system_creator.components[1].name == 'BaseTransceiverStation_2'
        assert json_system_creator.components[1].locality == [3]
    
    def test_create_components_num_components_created(self, json_system_creator: SystemCreator.SystemCreator,
                                                        component_library: dict, system_configuration: dict):
        json_system_creator.setup(component_library, system_configuration)                                                        
        json_system_creator.create_components()
        assert len(json_system_creator.components) == 11

class TestR2DSystemCreator_NorthEast_SF_Housing:

    MAIN_FILE = './tests/test_inputs/test_inputs_NorthEast_SF_Housing_Main.json'

    @pytest.fixture()
    def r2d_system_creator(self) -> SystemCreator.SystemCreator:
        return SystemCreator.R2DSystemCreator()

    @pytest.fixture()
    def component_library(self) -> ComponentLibraryCreator.JSONComponentLibraryCreator:
        input_dict = main.read_file(self.MAIN_FILE)
        return main.form_component_library(input_dict)
    
    @pytest.fixture()
    def system_configuration(self) -> dict:
        input_dict = main.read_file(self.MAIN_FILE)
        system_configuration = main.read_file(input_dict['System']['SystemConfigurationFile'])
        return system_configuration

    def test_setup(self, r2d_system_creator: SystemCreator.SystemCreator, 
                   component_library: dict, system_configuration: dict):
        r2d_system_creator.setup(component_library, system_configuration)

        assert isinstance(r2d_system_creator.component_library, dict)
        assert isinstance(r2d_system_creator.system_configuration, dict)
        assert r2d_system_creator.scenario_id == 1
        assert r2d_system_creator.DS4_REPAIR_DURATION == 240
        assert r2d_system_creator.MAX_REPAIR_CREW_DEMAND_PER_BUILDING == 50
        assert r2d_system_creator.REPAIR_CREW_DEMAND_PER_SQFT['DS1'] == 5400
        assert r2d_system_creator.REPAIR_CREW_DEMAND_PER_SQFT['DS3'] == 2700
        assert r2d_system_creator.building_area_per_person['Locality 1'] == 541
        assert isinstance(r2d_system_creator.component_parameters_setter, SystemCreator.R2DResidentialBuildingParametersSetter)

    def test_create_components(self, r2d_system_creator: SystemCreator.SystemCreator, 
                               component_library: dict, system_configuration: dict):
        r2d_system_creator.setup(component_library, system_configuration)
        r2d_system_creator.create_components()
        target_num_components = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality'][
                                    'MaxNumBuildings'] + 1
        assert len(r2d_system_creator.components) == target_num_components

    def test_create_recovery_resource_suppliers(self, r2d_system_creator: SystemCreator.SystemCreator,
                                                component_library: dict, system_configuration: dict):
        r2d_system_creator.setup(component_library, system_configuration)
        suppliers = r2d_system_creator.create_recovery_resource_suppliers('Locality 1',
                                                                          r2d_system_creator.system_configuration['Content'][
                                                                              'Locality 1']['ComponentsInLocality'])
        assert len(suppliers) == 1
        assert suppliers[0].name == 'EmergencyResponseCenter'
        assert suppliers[0].locality == [1]
        assert isinstance(suppliers[0], Component.StandardiReCoDeSComponent)

    def test_create_residential_building_components(self, r2d_system_creator: SystemCreator.SystemCreator,
                                                    component_library: dict, system_configuration: dict):
        r2d_system_creator.setup(component_library, system_configuration)        
        r2d_system_creator.set_building_area_per_person()
        components = r2d_system_creator.create_residential_building_components('Locality 1',
                                                                               r2d_system_creator.system_configuration['Content'][
                                                                                   'Locality 1']['ComponentsInLocality'])
        target_num_components = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality'][
            'MaxNumBuildings']
        assert len(components) == target_num_components
        for component in components:
            assert 'ResidentialBuilding' in component.name
            assert isinstance(component, Component.StandardiReCoDeSComponent)

    def test_load_building_data_information(self, r2d_system_creator: SystemCreator.SystemCreator,
                                            component_library: dict, system_configuration: dict):
        r2d_system_creator.setup(component_library, system_configuration)
        building_info_folder = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality'][
            'BuildingsInfoFolder']
        building_id = '8000'
        building_data = r2d_system_creator.load_building_data(building_id, building_info_folder)
        assert building_data['Information']['GeneralInformation']['BIM_id'] == building_id
        target_coords = [37.803317, -122.4429]
        assert building_data['Information']['GeneralInformation']['Latitude'] == target_coords[0]
        assert building_data['Information']['GeneralInformation']['Longitude'] == target_coords[1]
        target_plan_area = 57242.0
        assert building_data['Information']['GeneralInformation']['PlanArea'] == target_plan_area
        target_num_stories = 1
        assert building_data['Information']['GeneralInformation']['NumberOfStories'] == target_num_stories

    def test_load_building_data_damage(self, r2d_system_creator: SystemCreator.SystemCreator, 
                                       component_library: dict, system_configuration: dict):
        r2d_system_creator.setup(component_library, system_configuration)
        building_info_folder = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality'][
            'BuildingsInfoFolder']
        building_id = 8000
        building_data = r2d_system_creator.load_building_data(building_id, building_info_folder)
        scenario_id = 0
        target_damage_state = 2
        assert building_data['Damage']['highest_damage_state/S'][scenario_id] == target_damage_state
        target_reconstruction_cost = 813408.82
        assert math.isclose(building_data['Damage']['reconstruction/cost'][scenario_id], target_reconstruction_cost)
        target_reconstruction_time = 30
        assert building_data['Damage']['reconstruction/time'][scenario_id] == target_reconstruction_time

    def test_get_building_location(self, r2d_system_creator: SystemCreator.SystemCreator, 
                                   component_library: dict, system_configuration: dict):
        r2d_system_creator.setup(component_library, system_configuration)
        building_info_folder = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality'][
            'BuildingsInfoFolder']
        building_ids = [8000, 8001, 8002, 8003]
        target_locations = [[37.803317, -122.4429], [37.799682, -122.434602], [37.797494, -122.434566],
                            [37.796672, -122.43739]]
        for target_location, building_id in zip(target_locations, building_ids):
            building_data = r2d_system_creator.load_building_data(building_id, building_info_folder)
            building_location = r2d_system_creator.get_building_location(building_data)
            assert all([math.isclose(i, j) for i, j in zip(target_location, building_location)])

    def test_building_location_inside_building_box(self, r2d_system_creator: SystemCreator.SystemCreator,
                                                   component_library: dict, system_configuration: dict):
        r2d_system_creator.setup(component_library, system_configuration)
        building_info_folder = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality'][
            'BuildingsInfoFolder']
        building_ids = [8000, 8001, 8002, 8003]
        bounding_box = {'Latitude': [37.797, 37.797, 37.8, 37.8], 'Longitude': [-122.44, -122.43, -122.43, -122.44]}
        target_bools = [False, True, True, False]
        for target_bool, building_id in zip(target_bools, building_ids):
            building_data = r2d_system_creator.load_building_data(building_id, building_info_folder)
            building_location = r2d_system_creator.get_building_location(building_data)
            building_in_bounding_box = r2d_system_creator.building_location_inside_bounding_box(building_location,
                                                                                                bounding_box)
            assert target_bool == building_in_bounding_box

    def test_building_is_residential(self, r2d_system_creator: SystemCreator.SystemCreator, 
                                     component_library: dict, system_configuration: dict):
        r2d_system_creator.setup(component_library, system_configuration)
        building_info_folder = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality'][
            'BuildingsInfoFolder']
        building_ids = [8000, 8001, 8002, 8003]
        target_bools = [False, True, False, True]
        for target_bool, building_id in zip(target_bools, building_ids):
            building_data = r2d_system_creator.load_building_data(building_id, building_info_folder)
            building_is_residential = r2d_system_creator.building_is_residential(building_data)
            assert target_bool == building_is_residential

    def test_create_residential_building(self, r2d_system_creator: SystemCreator.SystemCreator,
                                            component_library: dict, system_configuration: dict):
        r2d_system_creator.setup(component_library, system_configuration)
        r2d_system_creator.set_building_area_per_person()
        locality = 'Locality 1'
        building_info_folder = r2d_system_creator.system_configuration['Content'][locality]['ComponentsInLocality'][
            'BuildingsInfoFolder']
        r2d_system_creator.system_configuration['Constants']['DEFAULT_REPAIR_DURATION_DICT']['Lognormal']['Dispersion']  = 0.0
        building_ids = [8001, 8005, 8020]
        scenario_ids = [2, 4]
        target_repair_durations = [[30, 120, 240], [0, 5, 5]]
        target_repair_demands = [[2, 22, 11], [0, 11, 6]]
        target_housing_capacities = [[11, 106, 53], [11, 106, 53]]
        target_DSs = [[2, 3, 4], [0, 1, 1]]
        target_repair_costs = [[40300, 3276525.175, 2014177.5], [0, 158669.5, 40283.55]]

        for i, scenario_id in enumerate(scenario_ids):
            r2d_system_creator.scenario_id = scenario_id
            r2d_system_creator.set_component_parameters_setter()
            for ii, building_id in enumerate(building_ids):
                building_data = r2d_system_creator.load_building_data(building_id, building_info_folder)
                component = r2d_system_creator.create_residential_building(locality, building_data)
                assert isinstance(component, Component.StandardiReCoDeSComponent)
                assert component.name == f'DS{target_DSs[i][ii]}_ResidentialBuilding'
                assert component.supply['Supply']['Shelter'].initial_amount == target_housing_capacities[i][ii]
                assert component.demand['OperationDemand']['Shelter'].initial_amount == target_housing_capacities[i][ii]
                if target_DSs[i][ii] != 0:
                    assert math.isclose(component.recovery_model.recovery_activities['Repair'].duration,
                                                  target_repair_durations[i][ii])
                    assert component.recovery_model.recovery_activities['Repair'].demand['RepairCrew'].initial_amount == \
                        target_repair_demands[i][ii]
                else:
                    assert isinstance(component.recovery_model, ComponentRecoveryModel.NoRecoveryActivityModel)
                if target_DSs[i][ii] > 1:
                    target_financing_demand = target_repair_costs[i][ii] / component.recovery_model.recovery_activities['Financing'].duration
                    assert math.isclose(
                        component.recovery_model.recovery_activities['Financing'].demand['Money'].initial_amount,
                        target_financing_demand)
                    
    def test_get_building_damage_state(self, r2d_system_creator: SystemCreator.SystemCreator, 
                                       component_library: dict, system_configuration: dict):
        r2d_system_creator.setup(component_library, system_configuration)
        building_info_folder = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality'][
            'BuildingsInfoFolder']
        building_id = 8000
        building_data = r2d_system_creator.load_building_data(building_id, building_info_folder)
        scenario_ids = list(range(5))
        target_DSs = [2, 3, 2, 0, 4]
        for target_DS, scenario_id in zip(target_DSs, scenario_ids):
            r2d_system_creator.scenario_id = scenario_id
            damage_state = r2d_system_creator.get_building_damage_state(building_data)
            assert damage_state == target_DS

class TestR2DSystemWithInterfacesCreator:

    MAIN_FILE = './tests/test_inputs/test_inputs_NorthEast_SF_Housing_Interface_Infrastructure_Main.json'

    @pytest.fixture()
    def r2d_system_creator(self) -> SystemCreator.SystemCreator:
        return SystemCreator.R2DSystemWithInterfacesCreator()

    @pytest.fixture()
    def component_library(self) -> ComponentLibraryCreator.JSONComponentLibraryCreator:
        input_dict = main.read_file(self.MAIN_FILE)
        return main.form_component_library(input_dict)
    
    @pytest.fixture()
    def system_configuration(self) -> dict:
        input_dict = main.read_file(self.MAIN_FILE)
        system_configuration = main.read_file(input_dict['System']['SystemConfigurationFile'])
        return system_configuration
    
    def test_create_components_in_localities(self, r2d_system_creator: SystemCreator.R2DSystemWithInterfacesCreator,
                                             component_library: dict, system_configuration: dict):
        r2d_system_creator.setup(component_library, system_configuration)
        locality = 'Locality 1'
        content = r2d_system_creator.system_configuration['Content'][locality]['ComponentsInLocality']
        r2d_system_creator.create_components_in_localities(locality, content)
        assert isinstance(r2d_system_creator.components[-4], Component.StandardiReCoDeSComponent)
        assert 'ResidentialBuilding' in r2d_system_creator.components[-4].name
        assert isinstance(r2d_system_creator.components[-3], Component.InfrastructureInterface)
        assert r2d_system_creator.components[-3].name == 'ElectricPowerSupplySystem'
        assert isinstance(r2d_system_creator.components[-2], Component.InfrastructureInterface)
        assert r2d_system_creator.components[-2].name == 'WaterSupplySystem'
        assert isinstance(r2d_system_creator.components[-1], Component.InfrastructureInterface)
        assert r2d_system_creator.components[-1].name == 'CellularCommunicationSystem'

    def test_create_infrastructure_service_suppliers(self, r2d_system_creator: SystemCreator.R2DSystemWithInterfacesCreator,
                                                     component_library: dict, system_configuration: dict):
        r2d_system_creator.setup(component_library, system_configuration)
        locality = 'Locality 1'
        content = r2d_system_creator.system_configuration['Content'][locality]['ComponentsInLocality']
        suppliers = r2d_system_creator.create_infrastructure_service_suppliers(locality, content)
        assert isinstance(suppliers[0], Component.InfrastructureInterface)
        assert suppliers[0].name == 'ElectricPowerSupplySystem'
        assert suppliers[0].locality == [1]
        assert isinstance(suppliers[1], Component.InfrastructureInterface)
        assert suppliers[1].name == 'WaterSupplySystem'
        assert suppliers[1].locality == [1]
        assert isinstance(suppliers[2], Component.InfrastructureInterface)
        assert suppliers[2].name == 'CellularCommunicationSystem'
        assert suppliers[2].locality == [1]
    
    def test_set_infrastructure_system_parameters(self, r2d_system_creator: SystemCreator.R2DSystemWithInterfacesCreator,
                                                     component_library: dict, system_configuration: dict):
        r2d_system_creator.setup(component_library, system_configuration)
        locality = 'Locality 2'
        content = r2d_system_creator.system_configuration['Content'][locality]['ComponentsInLocality']
        component = copy.deepcopy(component_library['ElectricPowerSupplySystem'])
        assert component.supply['Supply']['ElectricPower'].initial_amount == 0
        assert component.supply['Supply']['ElectricPower'].current_amount == 0
        assert component.recovery_model.recovery_activities['Recovery'].duration == 0

        r2d_system_creator.set_infrastructure_system_parameters(component, content['Infrastructure'][0]['ElectricPowerSupplySystem'])
        assert component.supply['Supply']['ElectricPower'].initial_amount == 80
        assert component.recovery_model.recovery_activities['Recovery'].duration == 30
        assert component.recovery_model.damage_to_functionality_relation.step_values == [0.0, 0.5, 1.0]
        assert component.recovery_model.damage_to_functionality_relation.step_limits == [0.0, 0.5, 1.0]
    
class TestComponentParametersSetter:

    MAIN_FILE = './tests/test_inputs/test_inputs_NorthEast_SF_Housing_Interface_Infrastructure_Main.json'

    @pytest.fixture()
    def r2d_system_creator(self) -> SystemCreator.SystemCreator:
        return SystemCreator.R2DSystemWithInterfacesCreator()

    @pytest.fixture()
    def component_library(self) -> ComponentLibraryCreator.JSONComponentLibraryCreator:
        input_dict = main.read_file(self.MAIN_FILE)
        return main.form_component_library(input_dict)
    
    @pytest.fixture()
    def building_component(self, component_library: dict) -> Component.StandardiReCoDeSComponent:
        return copy.deepcopy(component_library['DS3_ResidentialBuilding'])

    @pytest.fixture()
    def component_parameters_setter(self) -> SystemCreator.ComponentParametersSetter:
        return SystemCreator.ComponentParametersSetter()

    def test_set_component_supply(self, 
                                  building_component: Component.StandardiReCoDeSComponent,
                                  component_parameters_setter: SystemCreator.ComponentParametersSetter):
        component_parameters_setter.set_component_supply(building_component,
                                                         'Shelter', 100)
        assert building_component.supply['Supply']['Shelter'].initial_amount == 100
        assert building_component.supply['Supply']['Shelter'].current_amount == 100
    
    def test_set_component_supply_wrong_resource(self, 
                                        building_component: Component.StandardiReCoDeSComponent,
                                        component_parameters_setter: SystemCreator.ComponentParametersSetter):
        with pytest.raises(KeyError):
            component_parameters_setter.set_component_supply(building_component,
                                                             'ElectricPower', 100)
    
    def test_set_component_supply_negative_amount(self,
                                        building_component: Component.StandardiReCoDeSComponent,
                                        component_parameters_setter: SystemCreator.ComponentParametersSetter):
        with pytest.raises(ValueError):
            component_parameters_setter.set_component_supply(building_component,
                                                             'Shelter', -100) 

    def test_set_component_operation_demand(self,
                                            building_component: Component.StandardiReCoDeSComponent,
                                            component_parameters_setter: SystemCreator.ComponentParametersSetter):
        component_parameters_setter.set_component_operation_demand(building_component,
                                                                    'Shelter', 100)
        assert building_component.demand['OperationDemand']['Shelter'].initial_amount == 100
        assert building_component.demand['OperationDemand']['Shelter'].current_amount == 100

    def test_set_component_operation_demand_wrong_resource(self,
                                            building_component: Component.StandardiReCoDeSComponent,
                                            component_parameters_setter: SystemCreator.ComponentParametersSetter):
        with pytest.raises(KeyError):
            component_parameters_setter.set_component_operation_demand(building_component,
                                                                        'DummyResource', 100)
            
    def test_set_component_operation_demand_negative_amount(self,
                                            building_component: Component.StandardiReCoDeSComponent,
                                            component_parameters_setter: SystemCreator.ComponentParametersSetter):
        with pytest.raises(ValueError):
            component_parameters_setter.set_component_operation_demand(building_component,
                                                                        'Shelter', -100)
    
    def test_set_recovery_demand(self,
                                 building_component: Component.StandardiReCoDeSComponent,
                                 component_parameters_setter: SystemCreator.ComponentParametersSetter):
        component_parameters_setter.set_component_recovery_demand(building_component,
                                                                  'Repair', 'RepairCrew', 100)
        assert building_component.recovery_model.recovery_activities['Repair'].demand['RepairCrew'].initial_amount == 100
        assert building_component.recovery_model.recovery_activities['Repair'].demand['RepairCrew'].current_amount == 100

    def test_set_recovery_demand_wrong_resource(self,
                                                building_component: Component.StandardiReCoDeSComponent,
                                                component_parameters_setter: SystemCreator.ComponentParametersSetter):
        with pytest.raises(KeyError):
            component_parameters_setter.set_component_recovery_demand(building_component,
                                                                      'Repair', 'DummyResource', 100)
    
    def test_set_recovery_demand_negative_amount(self,
                                                    building_component: Component.StandardiReCoDeSComponent,
                                                    component_parameters_setter: SystemCreator.ComponentParametersSetter):
        with pytest.raises(ValueError):
            component_parameters_setter.set_component_recovery_demand(building_component,
                                                                      'Repair', 'RepairCrew', -100)     

    def test_set_recovery_demand_wrong_activity(self,
                                                    building_component: Component.StandardiReCoDeSComponent,
                                                    component_parameters_setter: SystemCreator.ComponentParametersSetter):
        component_parameters_setter.set_component_recovery_demand(building_component,
                                                                      'DummyActivity', 'RepairCrew', 100) 
        assert 'DummyActivity' not in building_component.recovery_model.recovery_activities.keys()

class TestR2DComponentParametersSetter:

    MAIN_FILE = './tests/test_inputs/test_inputs_NorthEast_SF_Housing_Interface_Infrastructure_Main.json'
    
    @pytest.fixture()
    def component_library(self) -> ComponentLibraryCreator.JSONComponentLibraryCreator:
        input_dict = main.read_file(self.MAIN_FILE)
        return main.form_component_library(input_dict)

    @pytest.fixture()
    def system_configuration(self) -> dict:
        input_dict = main.read_file(self.MAIN_FILE)
        system_configuration = main.read_file(input_dict['System']['SystemConfigurationFile'])
        return system_configuration

    @pytest.fixture()
    def r2d_system_creator(self, component_library: dict, system_configuration: dict) -> SystemCreator.SystemCreator:
        r2d_system_creator = SystemCreator.R2DSystemWithInterfacesCreator()
        r2d_system_creator.setup(component_library, system_configuration)
        return r2d_system_creator
    
    @pytest.fixture()
    def building_component(self, component_library: dict) -> Component.StandardiReCoDeSComponent:
        return copy.deepcopy(component_library['DS3_ResidentialBuilding'])
    
    @pytest.fixture()
    def component_parameters_setter(self, r2d_system_creator) -> SystemCreator.ComponentParametersSetter:
        system_level_data = {key: r2d_system_creator.__dict__.get(key, None) for key in SystemCreator.R2DResidentialBuildingParametersSetter.SYSTEM_LEVEL_DATA_REQUIRED_FOR_BUILDINGS}
        return SystemCreator.R2DResidentialBuildingParametersSetter(system_level_data)
    
    def test_init(self, component_parameters_setter):
        assert isinstance(component_parameters_setter.system_level_data, dict)
        assert len(component_parameters_setter.system_level_data) == len(SystemCreator.R2DResidentialBuildingParametersSetter.SYSTEM_LEVEL_DATA_REQUIRED_FOR_BUILDINGS)
    
    def test_set_parameters(self, building_component: Component.StandardiReCoDeSComponent, 
                               component_parameters_setter: SystemCreator.ComponentParametersSetter,
                               r2d_system_creator: SystemCreator.SystemCreator):
        building_folder = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality']['BuildingsInfoFolder']
        building_data = r2d_system_creator.load_building_data(8000, building_folder)
        component_parameters_setter.set_parameters(building_component, 'Locality 1', building_data, 3)
        assert building_component.area == 57242.0
        assert building_component.footprint == {"type": "Feature", "geometry": {"type": "Polygon", "coordinates":[[[-122.442624,37.803560],[-122.442634,37.803620],[-122.442965,37.803585],[-122.442954,37.803519],[-122.442784,37.803536],[-122.442785,37.803544],[-122.442624,37.803560]]]}, "properties":{}}
        assert building_component.num_stories == 1
        assert building_component.supply['Supply']['Shelter'].current_amount == 105
        assert building_component.supply['Supply']['Shelter'].initial_amount == 105
        assert building_component.demand['OperationDemand']['Shelter'].current_amount == 105
        assert building_component.demand['OperationDemand']['Shelter'].initial_amount == 105
        assert building_component.demand['OperationDemand']['ElectricPower'].current_amount == 105 * 0.02
        assert building_component.demand['OperationDemand']['ElectricPower'].initial_amount == 105 * 0.02
        assert building_component.demand['OperationDemand']['PotableWater'].current_amount == 105 * 150
        assert building_component.demand['OperationDemand']['PotableWater'].initial_amount == 105 * 150
        assert building_component.demand['OperationDemand']['CellularCommunication'].initial_amount == 105 * 0.033
        assert building_component.demand['OperationDemand']['CellularCommunication'].current_amount == 105 * 0.033
        assert building_component.recovery_model.recovery_activities['Repair'].demand['RepairCrew'].current_amount == 22
        assert building_component.recovery_model.recovery_activities['Repair'].demand['RepairCrew'].initial_amount == 22
        assert building_component.locality == [1]

    def test_set_building_area(self, building_component: Component.StandardiReCoDeSComponent, 
                               component_parameters_setter: SystemCreator.ComponentParametersSetter,
                               r2d_system_creator: SystemCreator.SystemCreator):
        building_folder = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality']['BuildingsInfoFolder']
        building_data = r2d_system_creator.load_building_data(8000, building_folder)
        component_parameters_setter.set_building_area(building_component, building_data)
        assert building_component.area == 57242.0
    
    def test_set_building_footprint(self, building_component: Component.StandardiReCoDeSComponent, 
                               component_parameters_setter: SystemCreator.ComponentParametersSetter,
                               r2d_system_creator: SystemCreator.SystemCreator):
        building_folder = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality']['BuildingsInfoFolder']
        building_data = r2d_system_creator.load_building_data(8000, building_folder)
        component_parameters_setter.set_building_footprint(building_component, building_data)
        target_building_footprint = {"type": "Feature", "geometry": {"type": "Polygon", "coordinates":[[[-122.442624,37.803560],[-122.442634,37.803620],[-122.442965,37.803585],[-122.442954,37.803519],[-122.442784,37.803536],[-122.442785,37.803544],[-122.442624,37.803560]]]}, "properties":{}}
        assert building_component.footprint == target_building_footprint

    def test_set_building_num_stories(self, building_component: Component.StandardiReCoDeSComponent, 
                               component_parameters_setter: SystemCreator.ComponentParametersSetter,
                               r2d_system_creator: SystemCreator.SystemCreator):
        building_folder = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality']['BuildingsInfoFolder']
        building_data = r2d_system_creator.load_building_data(8000, building_folder)
        component_parameters_setter.set_building_num_stories(building_component, building_data)
        assert building_component.num_stories == 1

    def test_get_total_building_area(self,
                               component_parameters_setter: SystemCreator.ComponentParametersSetter,
                               r2d_system_creator: SystemCreator.SystemCreator):
        building_folder = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality']['BuildingsInfoFolder']
        building_ids = [8000, 8001, 8002, 8004]
        target_areas = [57242.0, 6200.0, 6240.0, 13404.0]
        for target_area, building_id in zip(target_areas, building_ids):
            building_data = r2d_system_creator.load_building_data(building_id, building_folder)
            building_area = component_parameters_setter.get_total_building_area(building_data)
            assert building_area == target_area

    def test_get_building_housing_capacity(self, 
                               component_parameters_setter: SystemCreator.ComponentParametersSetter,
                               r2d_system_creator: SystemCreator.SystemCreator):
        building_folder = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality']['BuildingsInfoFolder']
        building_ids = [8000, 8001, 8002, 8004]
        target_housing_capacities = [105, 11, 11, 24]
        r2d_system_creator.set_building_area_per_person()
        for target_housing_capacity, building_id in zip(target_housing_capacities, building_ids):
            building_data = r2d_system_creator.load_building_data(building_id, building_folder)
            building_area = component_parameters_setter.get_total_building_area(building_data)
            building_housing_capacity = component_parameters_setter.get_building_housing_capacity(building_area, 'Locality 1')
            assert building_housing_capacity == target_housing_capacity

    def test_set_housing_parameters(self, building_component: Component.StandardiReCoDeSComponent, 
                               component_parameters_setter: SystemCreator.ComponentParametersSetter,
                               r2d_system_creator: SystemCreator.SystemCreator):
        building_folder = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality']['BuildingsInfoFolder']
        building_data = r2d_system_creator.load_building_data(8000, building_folder)
        component_parameters_setter.set_building_area(building_component, building_data)
        component_parameters_setter.set_housing_parameters(building_component, 'Locality 1')
        assert building_component.supply['Supply']['Shelter'].current_amount == 105
        assert building_component.supply['Supply']['Shelter'].initial_amount == 105
        assert building_component.demand['OperationDemand']['Shelter'].current_amount == 105
        assert building_component.demand['OperationDemand']['Shelter'].initial_amount == 105
    
    def test_set_operation_demand_parameters(self, building_component: Component.StandardiReCoDeSComponent, 
                               component_parameters_setter: SystemCreator.ComponentParametersSetter,
                               r2d_system_creator: SystemCreator.SystemCreator):
        building_folder = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality']['BuildingsInfoFolder']
        building_data = r2d_system_creator.load_building_data(8000, building_folder)
        component_parameters_setter.set_building_area(building_component, building_data)
        component_parameters_setter.set_housing_parameters(building_component, 'Locality 1')
        component_parameters_setter.set_operation_demand_parameters(building_component, 'Locality 1', building_data.get('OperationDemandResources', []))
        assert building_component.demand['OperationDemand']['ElectricPower'].current_amount == 105 * 0.02
        assert building_component.demand['OperationDemand']['ElectricPower'].initial_amount == 105 * 0.02
        assert building_component.demand['OperationDemand']['PotableWater'].current_amount == 105 * 150
        assert building_component.demand['OperationDemand']['PotableWater'].initial_amount == 105 * 150
        assert building_component.demand['OperationDemand']['CellularCommunication'].current_amount == 105 * 0.033
        assert building_component.demand['OperationDemand']['CellularCommunication'].initial_amount == 105 * 0.033
    
    def test_set_repair_demand(self, building_component: Component.StandardiReCoDeSComponent, 
                               component_parameters_setter: SystemCreator.ComponentParametersSetter,
                               r2d_system_creator: SystemCreator.SystemCreator):
        building_folder = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality']['BuildingsInfoFolder']
        building_data = r2d_system_creator.load_building_data(8000, building_folder)
        component_parameters_setter.set_building_area(building_component, building_data)
        component_parameters_setter.set_repair_demand(building_component, 'Locality 1', 2)
        assert building_component.recovery_model.recovery_activities['Repair'].demand['RepairCrew'].current_amount == 11
        assert building_component.recovery_model.recovery_activities['Repair'].demand['RepairCrew'].initial_amount == 11
    
    def test_get_repair_crew_demand(self,
                               component_parameters_setter: SystemCreator.ComponentParametersSetter):
        assert component_parameters_setter.get_repair_crew_demand(0, 1000) == 0
        assert component_parameters_setter.get_repair_crew_demand(1, 5400) == 1
        assert component_parameters_setter.get_repair_crew_demand(2, 5400) == 1
        assert component_parameters_setter.get_repair_crew_demand(3, 5400) == 2
        assert component_parameters_setter.get_repair_crew_demand(4, 5400) == 2
        assert component_parameters_setter.get_repair_crew_demand(4, 5400000) == 50
    
    def test_set_repair_duration(self, building_component: Component.StandardiReCoDeSComponent, 
                               component_parameters_setter: SystemCreator.ComponentParametersSetter,
                               r2d_system_creator: SystemCreator.SystemCreator):
        r2d_system_creator.DEFAULT_REPAIR_DURATION_DICT['Lognormal']['Dispersion'] = 0
        building_folder = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality']['BuildingsInfoFolder']
        building_data = r2d_system_creator.load_building_data(8000, building_folder)
        component_parameters_setter.set_repair_duration(building_component, building_data)
        assert math.isclose(building_component.recovery_model.recovery_activities['Repair'].duration, 120)
    
    def test_get_median_repair_duration(self,
                                 component_parameters_setter: SystemCreator.ComponentParametersSetter,
                                 r2d_system_creator: SystemCreator.SystemCreator):
        building_folder = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality']['BuildingsInfoFolder']
        building_data = r2d_system_creator.load_building_data(8000, building_folder)
        assert component_parameters_setter.get_median_repair_duration(building_data) == 120
        r2d_system_creator.scenario_id = 44
        system_level_data = {key: r2d_system_creator.__dict__.get(key, None) for key in SystemCreator.R2DResidentialBuildingParametersSetter.SYSTEM_LEVEL_DATA_REQUIRED_FOR_BUILDINGS}
        component_parameters_setter.system_level_data = system_level_data
        assert component_parameters_setter.get_median_repair_duration(building_data) == 240
    
    def test_set_building_repair_cost(self, 
                                      component_parameters_setter: SystemCreator.ComponentParametersSetter,
                                      building_component: Component.StandardiReCoDeSComponent,
                                      r2d_system_creator: SystemCreator.SystemCreator):
        building_folder = r2d_system_creator.system_configuration['Content']['Locality 1']['ComponentsInLocality']['BuildingsInfoFolder']
        building_data = r2d_system_creator.load_building_data(8000, building_folder)
        component_parameters_setter.set_building_repair_cost(building_component, building_data)
        assert math.isclose(building_component.recovery_model.recovery_activities['Financing'].demand['Money'].current_amount, 3538328.367/building_component.recovery_model.recovery_activities['Financing'].duration)
        assert math.isclose(building_component.recovery_model.recovery_activities['Financing'].demand['Money'].initial_amount, 3538328.367/building_component.recovery_model.recovery_activities['Financing'].duration)

    