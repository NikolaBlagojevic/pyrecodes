import pytest
from pyrecodes import main
from pyrecodes import ComponentLibraryCreator
from pyrecodes import DistributionPriority
from pyrecodes import System
from pyrecodes import SystemCreator
import copy
import numpy as np


class TestDistributionPriority():

    @pytest.fixture
    def system(self):
        input_dict = main.read_file(self.MAIN_FILE)
        system = main.create_system(input_dict)
        return system

class TestComponentTypeBasedPriority(TestDistributionPriority):

    MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

    @pytest.fixture
    def distribution_priority(self, system: System.System):
        distribution_priority = DistributionPriority.ComponentTypeBasedPriority(resource_name='Resource 1', 
                                                                                parameters=[['ElectricPowerPlant', 'OperationDemand'], 
                                                                                            ['CoolingWaterFacility', 'OperationDemand'], 
                                                                                            ['BuildingStockUnit', 'OperationDemand']],
                                                                                components=system.components)
        return distribution_priority

    def test_categorize_components_based_on_type(self, distribution_priority: DistributionPriority.DistributionPriority):
        categorized_components_dict = distribution_priority.categorize_components_based_on_type()
        assert categorized_components_dict['BaseTransceiverStation_1'] == [0]
        assert categorized_components_dict['ElectricPowerPlant'] == [1]
        assert categorized_components_dict['SuperLink'] == [2, 3, 5, 6, 9, 10]
        assert categorized_components_dict['CoolingWaterFacility'] == [4]
        assert categorized_components_dict['BuildingStockUnit'] == [7]
        assert categorized_components_dict['BaseTransceiverStation_2'] == [8]

    def test_set_distribution_priority(self, distribution_priority: DistributionPriority.DistributionPriority):
        assert distribution_priority.get_component_priorities() == ([1, 4, 7], ['OperationDemand', 'OperationDemand', 'OperationDemand'])

class TestSupplierOnlyDistributionPriority_NorthEastSF(TestDistributionPriority):
    
    MAIN_FILE = './tests/test_inputs/test_inputs_NorthEast_SF_Housing_Main.json'

    def test_set_distribution_priority(self, system: System.System):
        target_ids = [component_id for component_id in range(len(system.components)) if
                      'ResidentialBuilding' in system.components[component_id].name]
        print(target_ids)
        housing_priorities_ids, demand_types = system.resources['Shelter'][
            'DistributionModel'].priority.get_component_priorities()
        print(housing_priorities_ids)
        print(demand_types)
        assert target_ids == housing_priorities_ids and all(
            [demand_type == 'OperationDemand' for demand_type in demand_types])

class TestRandomDistributionPriority_NorthEastSF(TestDistributionPriority):

    MAIN_FILE = './tests/test_inputs/test_inputs_NorthEast_SF_Housing_Main.json'

    def test_set_distribution_priority(self, system: System.System):
        target_remaining_component_ids = list(range(1, len(system.components)))
        target_remaining_demand_types = ['RecoveryDemand' for _ in target_remaining_component_ids]
        target_supplier_ids = 0
        target_supplier_dummy_demand_types = 'OperationDemand'
        recovery_resource_names = ['FirstResponderEngineer', 'SeniorEngineer', 'PlanCheckEngineeringTeam', 'Money',
                                   'Contractor', 'RepairCrew']
        for recovery_resource in recovery_resource_names:
            component_ids, component_demand_types = system.resources[recovery_resource][
                'DistributionModel'].priority.get_component_priorities()
            print(component_ids)
            assert target_supplier_ids == component_ids[0]
            assert target_supplier_dummy_demand_types == component_demand_types[0]
            sorted_user_component_ids = sorted(component_ids[1:])
            assert target_remaining_component_ids == sorted_user_component_ids
            assert target_remaining_demand_types == component_demand_types[1:]
            newly_generated_component_ids, newly_generated_component_demand_types = system.resources[recovery_resource][
                'DistributionModel'].priority.get_component_priorities()
            assert component_ids == newly_generated_component_ids
            assert component_demand_types == newly_generated_component_demand_types
            parameters = {"Seed": 40.0, "DemandType": ["RecoveryDemand"]}
            system.resources[recovery_resource]['DistributionModel'].priority.set_distribution_priority(parameters)
            different_seed_component_ids, different_seed_component_demand_types = system.resources[recovery_resource][
                'DistributionModel'].priority.get_component_priorities()
            assert different_seed_component_ids != newly_generated_component_ids
            assert different_seed_component_demand_types == newly_generated_component_demand_types

    def test_get_suppliers_id(self, system: System.System):
        target_remaining_component_ids = list(range(1, len(system.components)))
        target_supplier_ids = [0]
        recovery_resource_names = ['FirstResponderEngineer', 'PlanCheckEngineeringTeam', 'Money']
        for recovery_resource in recovery_resource_names:
            remaining_component_ids = list(range(len(system.components)))
            supplier_ids, remaining_component_ids = system.resources[recovery_resource][
                'DistributionModel'].priority.get_suppliers_id(remaining_component_ids)
            assert target_supplier_ids == supplier_ids
            assert target_remaining_component_ids == remaining_component_ids
   
    def test_randomize_ids_multiple_components_one_demand_types(self, system: System.System):
        component_ids = list(range(100))
        demand_types = ['OperationDemand']
        randomized_ids, randomized_demand_types = system.resources['RepairCrew'][
                'DistributionModel'].priority.randomize_ids(component_ids, demand_types)
        target_id_count = [1] * 100
        assert [randomized_ids.count(id) for id in component_ids] == target_id_count
        assert randomized_demand_types.count('OperationDemand') == 100

    def test_randomize_ids_one_component_two_demand_types(self, system: System.System):
        component_ids = [0]
        demand_types = ['RecoveryDemand', 'OperationDemand']
        randomized_ids, randomized_demand_types = system.resources['RepairCrew'][
                'DistributionModel'].priority.randomize_ids(component_ids, demand_types)
        bool_list = []
        assert randomized_ids == [0, 0]
        assert 'RecoveryDemand' in randomized_demand_types and 'OperationDemand' in randomized_demand_types
    
    def test_randomize_ids_multiple_components_two_demand_types(self, system: System.System):
        component_ids = [0, 1, 2]
        demand_types = ['RecoveryDemand', 'OperationDemand']
        randomized_ids, randomized_demand_types = system.resources['RepairCrew'][
                'DistributionModel'].priority.randomize_ids(component_ids, demand_types)
        bool_list = []
        assert [randomized_ids.count(id) for id in component_ids] == [2, 2, 2]
        assert randomized_demand_types.count('RecoveryDemand') == 3
        assert randomized_demand_types.count('OperationDemand') == 3

class TestRandomDistributionPriorityWithPrioritizedInterfaces_NorthEastSFWithInterfaces(TestDistributionPriority):

    MAIN_FILE = './tests/test_inputs/test_inputs_NorthEast_SF_Housing_Interface_Infrastructure_Main.json'
    INTERFACE_IDS = {'ElectricPower': [433, 553, 606, 749, 756],
                     'PotableWater': [434, 554, 607, 750, 757],
                     'CellularCommunication': [435, 555, 608, 751, 758]}

    def test_set_distribution_priority(self, system: System.System):
        all_resources = ['ElectricPower', 'PotableWater', 'CellularCommunication']
        for resource in all_resources:
            component_priorities = system.resources[resource][
                'DistributionModel'].priority.get_component_priorities()
            other_resources = [some_resource for some_resource in all_resources if some_resource != resource]            
            assert all(interface_id in component_priorities[0][:len(self.INTERFACE_IDS[resource])] for interface_id in self.INTERFACE_IDS[resource])
            number_of_other_resource_interface_components = sum([len(self.INTERFACE_IDS[other_resource]) for other_resource in other_resources])
            for other_resource in other_resources:                 
                start_index = len(self.INTERFACE_IDS[resource])
                end_index = start_index + number_of_other_resource_interface_components
                assert all(interface_id in component_priorities[0][start_index:end_index]
                                    for interface_id in self.INTERFACE_IDS[other_resource])

    def test_get_infrastructure_interface_id(self, system: System.System):
        all_interface_ids = system.resources['ElectricPower'][
                'DistributionModel'].priority.get_infrastructure_interface_id(list(range(len(system.components))))
        for resource, interface_ids in self.INTERFACE_IDS.items():
            assert all(interface_id for interface_id in interface_ids if interface_id in all_interface_ids)
        
class TestComponentBasedDistributionPriority_ThreeLocalitiesCommunity(TestDistributionPriority):

    MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

    def test_get_locality_id_from_string(self):
        example_strings = [['Locality 1'], ['Locality 123'], ['Locality 435'], ['Locality 1', 'Locality 100']]
        target_ids = [[1], [123], [435], [1, 100]]
        for example_string, target_id in zip(example_strings, target_ids):
            locality_id = DistributionPriority.ComponentBasedPriority.get_locality_id_from_string(example_string)
            assert locality_id == target_id

    def test_component_not_already_in_priority_list(self, system: System.System):
        component = system.components[0]
        assert not (DistributionPriority.ComponentBasedPriority.component_not_already_in_priority_list(None))
        assert DistributionPriority.ComponentBasedPriority.component_not_already_in_priority_list(component)        

    def test_find_component_position(self, system: System.System):
        components = system.components
        distribution_priority = system.resources['ElectricPower']['DistributionModel'].priority
        target_components = [['BaseTransceiverStation_1', ['Locality 1']], ['ElectricPowerPlant', ['Locality 1']],
                             ['BuildingStockUnit', ['Locality 3']], ['SuperLink', ['Locality 1', 'Locality 2']]]
        target_positions = [0, 1, 7, 2]
        for target_component, target_position in zip(target_components, target_positions):
            component_position, temp_components = distribution_priority.find_component_position(target_component[0],
                                                                                                target_component[1],
                                                                                                components)
            assert component_position == target_position

    def test_find_component_position_error(self, system: System.System):
        distribution_priority = system.resources['ElectricPower']['DistributionModel'].priority
        with pytest.raises(ValueError):
            distribution_priority.find_component_position('ElectricPowerPlant', ['Locality 3'], system.components)

    def test_set_distribution_priority(self, system: System.System):
        target_priorities = [[1, 0, 4, 8, 7], [4, 1, 0, 8, 7], [0, 8, 1, 4, 7]]
        for target_priority, resource_parameters in zip(target_priorities, list(system.resources.values())[1:]):
            component_positions, demand_types = resource_parameters[
                'DistributionModel'].priority.get_component_priorities()
            assert target_priority == component_positions
            assert all([demand_type == 'OperationDemand' for demand_type in demand_types])

        