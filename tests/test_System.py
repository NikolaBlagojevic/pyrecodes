import pytest
import numpy as np
import math
from pyrecodes import System
from pyrecodes import SystemCreator
from pyrecodes import ComponentLibraryCreator
from pyrecodes import DamageInput
from pyrecodes import main

class TestDistributionListCreator:
    main_file = './tests/test_inputs/test_inputs_VirtualCommunity_Main.json'

    @pytest.fixture
    def distribution_list_creator(self):
        input_dict = main.read_file(self.main_file)
        system = main.create_system(input_dict)
        return System.DistributionListCreator(system.components, system.resources)
    
    def test_get_resource_distribution_dict(self, distribution_list_creator: System.DistributionListCreator):
        target_dict = {'IndependentResources': [
                        'BridgeService', 'ElectricPowerTransferService', 
                        'PotableWaterTransferService',
                        'CoolingWaterTransferService', 'Shelter'],

                       'InterdependentResources': [                       
                       'ElectricPower', 'HighLevelCommunication',
                       'LowLevelCommunication', 'PotableWater', 
                       'CoolingWater', 'FunctionalHousing',

                       'ElectricPower', 'HighLevelCommunication',
                       'LowLevelCommunication', 'PotableWater',
                       'CoolingWater', 'FunctionalHousing',

                       'ElectricPower', 'HighLevelCommunication',
                       'LowLevelCommunication', 'PotableWater',
                       'CoolingWater', 'FunctionalHousing',

                       'ElectricPower', 'HighLevelCommunication',
                       'LowLevelCommunication', 'PotableWater',
                       'CoolingWater', 'FunctionalHousing',

                       'ElectricPower', 'HighLevelCommunication',
                       'LowLevelCommunication', 'PotableWater', 
                       'CoolingWater', 'FunctionalHousing',
                       
                       'ElectricPower', 'HighLevelCommunication',
                       'LowLevelCommunication', 'PotableWater', 
                       'CoolingWater', 'FunctionalHousing']}
        
        assert distribution_list_creator.get_resource_distribution_dict() == target_dict
    
    def test_get_resource_group(self, distribution_list_creator):
        assert distribution_list_creator.get_resource_group('Utilities') == ['ElectricPower', 
                                                                             'HighLevelCommunication',
                                                                             'LowLevelCommunication',
                                                                             'PotableWater', 
                                                                             'CoolingWater', 
                                                                             'Shelter', 
                                                                             'FunctionalHousing']
        assert distribution_list_creator.get_resource_group('TransferService') == ['ElectricPowerTransferService',                                                                             
                                                                                   'PotableWaterTransferService', 
                                                                                   'CoolingWaterTransferService']
        assert distribution_list_creator.get_resource_group('BridgeService') == ['BridgeService']

    def test_get_independent_interdependent_resources(self, distribution_list_creator):
        target_interdependent_resources = ['ElectricPower', 'HighLevelCommunication', 'LowLevelCommunication', 'PotableWater', 'CoolingWater', 'FunctionalHousing']
        target_independent_resources = ['BridgeService', 'ElectricPowerTransferService', 'PotableWaterTransferService', 'CoolingWaterTransferService', 'Shelter']
        target_resource_distribution_dict = {'IndependentResources': target_independent_resources, 'InterdependentResources': target_interdependent_resources}
        resource_distribution_dict = distribution_list_creator.get_independent_interdependent_resources({'IndependentResources': ['BridgeService', 'ElectricPowerTransferService', 'PotableWaterTransferService', 'CoolingWaterTransferService'], 
                                                                                                         'InterdependentResources': []})
        assert resource_distribution_dict == target_resource_distribution_dict
    
    def test_resource_is_interdependent(self, distribution_list_creator):
        for component in distribution_list_creator.components:
            if component.name == 'ElectricPowerPlant':
                assert distribution_list_creator.resource_is_interdependent('ElectricPower', component) == True
            elif component.name == 'CoolingWaterFacility':
                assert distribution_list_creator.resource_is_interdependent('CoolingWater', component) == True
            else:
                assert distribution_list_creator.resource_is_interdependent('ElectricPower', component) == False
                assert distribution_list_creator.resource_is_interdependent('CoolingWater', component) == False
                assert distribution_list_creator.resource_is_interdependent('BridgeService', component) == False
                assert distribution_list_creator.resource_is_interdependent('Shelter', component) == False

    def test_form_resource_distribution_vector(self, distribution_list_creator):
        interdependent_resources = ['ElectricPower', 'Communication', 'CoolingWater']
        vector = distribution_list_creator.form_resource_distribution_vector(interdependent_resources)
        assert vector == ['ElectricPower', 'Communication', 'CoolingWater', 'ElectricPower', 'Communication',
                          'CoolingWater', 'ElectricPower', 'Communication', 'CoolingWater']

class TestCompleteDamageRecoveryTargetChecker:

    main_file = './tests/test_inputs/test_inputs_VirtualCommunity_Main.json'

    @pytest.fixture
    def system(self):
        input_dict = main.read_file(self.main_file)
        return main.create_system(input_dict)
    
    def test_recovery_target_met(self, system):
        system.time_step = system.START_TIME_STEP
        recovery_target_checker = System.CompleteDamageRecoveryTargetChecker()
        assert recovery_target_checker.recovery_target_met(system) == False

        not_enough_time_steps_to_recover = 10
        system.set_initial_damage()
        for time_step in range(1, not_enough_time_steps_to_recover):
            system.time_step = time_step
            system.recover()
        assert recovery_target_checker.recovery_target_met(system) == False

        enough_time_steps_to_recovery = 200
        for time_step in range(not_enough_time_steps_to_recover, enough_time_steps_to_recovery):
            system.time_step = time_step
            system.recover()
        assert recovery_target_checker.recovery_target_met(system) == True      

class TestBuiltEnvironmentSystem():

    main_file = ''

    @pytest.fixture()
    def system_creator(self) -> SystemCreator.SystemCreator:
        return SystemCreator.JSONSystemCreator()

    @pytest.fixture()
    def component_library_creator(self) -> ComponentLibraryCreator.ComponentLibraryCreator:
        return ComponentLibraryCreator.JSONComponentLibraryCreator(self.component_library_file)

    @pytest.fixture()
    def system(self) -> System.System:
        input_dict = main.read_file(self.main_file)
        system = main.create_system(input_dict)
        return system

class TestThreeLocalitiesSystem(TestBuiltEnvironmentSystem):

    main_file = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

    def test_init(self, system: System.System):
        assert isinstance(system.system_configuration, dict)
        assert isinstance(system.component_library, dict)
        assert isinstance(system.system_creator, SystemCreator.SystemCreator)
    
    def test_create_system(self, system: System.System):
        assert len(system.components) == 11 # number of components in the ThreeLocalitiesCommunity 
        assert len(system.resources) == 4 # number of resources in the ThreeLocalitiesCommunity
        assert len(system.resilience_calculators) == 2 # number of resilience calculators in the ThreeLocalitiesCommunity
        assert isinstance(system.recovery_target_checker, System.CompleteDamageRecoveryTargetChecker)
        assert isinstance(system.resource_distribution_dict, dict)
        assert isinstance(system.damage_input, DamageInput.ListDamageInput)
        assert system.START_TIME_STEP == 0
        assert system.MAX_TIME_STEP == 500
        assert system.DISASTER_TIME_STEP == 1
    
    def test_start_resilience_assessment(self, system: System.System):
        system.start_resilience_assessment()
        assert system.FINISH == True
    
    def test_set_initial_damage(self, system: System.System):
        target_damage_levels = [0.0, 0.4, 0.0, 0.0, 0.4, 0.0, 0.0, 0.4, 0.4, 0.0, 0.0]
        system.set_initial_damage()
        bool_list = []
        for target_damage_level, component in zip(target_damage_levels, system.components):
            bool_list.append(component.get_damage_level() == target_damage_level)
        assert all(bool_list)
    
    def test_update(self, system: System.System):
        for component in system.components:
            assert component.functionality_level == 1

        system.time_step = system.DISASTER_TIME_STEP
        system.set_initial_damage()
        system.update()
        target_functionality_levels = [1.0, 0.6, 1.0, 1.0, 0.6, 1.0, 1.0, 0.6, 0.0, 1.0, 1.0]
        for target_functionality_level, component in zip(target_functionality_levels, system.components):
            assert component.functionality_level == target_functionality_level

    def test_distribute_resources(self, system: System.System):
        system.distribute_resources()
        target_consumptions = [4, 1, 3]
        demand_col = system.resources['ElectricPower']['DistributionModel'].system_matrix.DEMAND_COL_ID
        demand_met_col = system.resources['ElectricPower']['DistributionModel'].system_matrix.DEMAND_MET_COL_ID
        for target_consumption, resource in zip(target_consumptions, list(system.resources.values())[1:]): # start from second resource, first resource is a Transfer Service
                consumption = np.sum(np.multiply(resource['DistributionModel'].system_matrix.matrix[:, demand_col],
                                                resource['DistributionModel'].system_matrix.matrix[:, demand_met_col]))
                assert math.isclose(consumption, target_consumption, abs_tol=1e-10)

        system.time_step = system.DISASTER_TIME_STEP
        system.set_initial_damage()
        system.update()
        system.distribute_resources()
        target_consumptions = [0, 0, 0]
        for target_consumption, resource in zip(target_consumptions, list(system.resources.values())[1:]): # start from second resource, first resource is a Transfer Service
            if resource['Group'] != 'TransferService':
                consumption = np.sum(np.multiply(resource['DistributionModel'].system_matrix.matrix[:, demand_col],
                                                resource['DistributionModel'].system_matrix.matrix[:, demand_met_col]))
                print(consumption)
                assert math.isclose(consumption, target_consumption, abs_tol=1e-10)
    
    def test_get_supply_of_interdependent_resources(self, system: System.System):
        target_supply = {'ElectricPower': 5, 'Communication': 3, 'CoolingWater': 3}
        system.distribute_resources()
        supply = system.get_supply_of_interdependent_resources()
        assert supply == target_supply
    
    def test_check_system_convergence(self, system: System.System):
        system.distribute_resources()
        supply = system.get_supply_of_interdependent_resources()
        assert system.check_system_convergence(supply, supply) == True

        system.time_step = system.DISASTER_TIME_STEP
        system.set_initial_damage()
        system.update()
        system.distribute_resources()
        damaged_supply = system.get_supply_of_interdependent_resources()
        assert system.check_system_convergence(supply, damaged_supply) == False

    def test_recover(self, system: System.System):
        system.time_step = system.DISASTER_TIME_STEP
        system.set_initial_damage()
        system.recover()
        target_damage_levels = [0.0, 0.36, 0.0, 0.0, 0.36, 0.0, 0.0, 0.36, 0.36, 0.0, 0.0]        
        for target_damage_level, component in zip(target_damage_levels, system.components):
            assert component.get_damage_level() == target_damage_level
        
class TestVirtualCommunity(TestBuiltEnvironmentSystem):

    main_file = './tests/test_inputs/test_inputs_VirtualCommunity_Main.json'

    def test_distribute_interdependent_resources(self, system: System.System):
        target_supplies = [80.0, 600.0, 495.0, 0.8, 0.24, 3600.0]
        system.distribute_interdependent_resources()
        for target_supply, resource_name in zip(target_supplies, system.resource_distribution_dict['InterdependentResources']):
            assert target_supply == system.resources[resource_name]['DistributionModel'].get_total_supply()
        
        system.time_step = system.DISASTER_TIME_STEP
        system.set_initial_damage()
        system.update()
        system.distribute_interdependent_resources()
        target_supplies = [0, 0, 0, 0, 0, 0]
        for target_supply, resource_name in zip(target_supplies, system.resource_distribution_dict['InterdependentResources']):
            assert target_supply == system.resources[resource_name]['DistributionModel'].get_total_supply()

   

#         # test when only the bridge is damaged
#         damage_vector = [0.0, 0.1, 0.0, 0.0, 0.0]
#         self.sys_test.set_damage(damage_vector)
#         self.sys_test.update()
#         self.sys_test.distribute_bridge_transfer_service()
#         self.assertEqual(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 1 to 2'][0][0].supply['transfer_services'].current['CoolingWaterTransferService'], 0.8*0.0)
#         self.assertEqual(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 2 to 1'][0][0].supply['transfer_services'].current['CoolingWaterTransferService'], 0.8*0.0)
#         self.assertEqual(self.sys_test.potential_paths_links['ElectricPowerTransferService']['from 1 to 2'][0][0].supply['transfer_services'].current['ElectricPowerTransferService'], 40*0.0)
#         self.assertEqual(self.sys_test.potential_paths_links['ElectricPowerTransferService']['from 2 to 1'][0][0].supply['transfer_services'].current['ElectricPowerTransferService'], 40*0.0)


#         # test with a three localities system and multiple potential path between two localities
#         self.sys_test.create_system(self.five_comp_sys_wlinks)
#         # define the dict key as a string from i-th locality to j-th locality, as a list of 
#         # localities that the path will go through
#         potential_paths['CoolingWaterTransferService'] = {'from 1 to 2': [[1, 2], [1, 3, 2]], 'from 2 to 1': [[2, 1], [2, 3, 1]],
#                                                                         'from 2 to 3': [[2, 1, 3], [2, 3]]}
#         potential_paths['ElectricPowerTransferService'] = {'from 1 to 2': [[1, 2]], 'from 2 to 1': [[2, 1]],
#                                                                           'from 2 to 3': [[2, 3], [2, 1, 3]], 'from 3 to 2': [[3, 2], [3, 1, 2]]}
#         potential_paths['PotableWaterTransferService'] = {'from 1 to 2': [[1, 2]], 'from 2 to 1': [[2, 1]],
#                                                                           'from 2 to 3': [[2, 3], [2, 1, 3]], 'from 3 to 2': [[3, 2], [3, 1, 2]]}
#         self.sys_test.set_potential_paths(potential_paths)
#         self.sys_test.create_potential_paths()
#         # test create potential paths for undamaged two localities system
#         self.assertTrue(isinstance(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 1 to 2'][0][0], Component.CWP))
#         self.assertTrue(isinstance(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 1 to 2'][1][0], Component.CWP))
#         self.assertTrue(isinstance(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 1 to 2'][1][1], Component.CWP))
#         self.assertEqual(len(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 1 to 2'][1]), 2)
#         self.assertTrue(isinstance(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 2 to 3'][0][0], Component.CWP))
#         self.assertTrue(isinstance(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 2 to 3'][0][1], Component.CWP))
#         self.assertEqual(len(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 2 to 3'][1]), 1)
#         self.assertEqual(len(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 2 to 3'][0]), 2)
#         self.assertTrue(isinstance(self.sys_test.potential_paths_links['ElectricPowerTransferService']['from 2 to 1'][0][0], Component.EPTL))
#         self.assertTrue(isinstance(self.sys_test.potential_paths_links['ElectricPowerTransferService']['from 1 to 2'][0][0], Component.EPTL))
#         self.assertEqual(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 1 to 2'][0][0].supply['transfer_services'].current['CoolingWaterTransferService'], 0.8)
#         self.assertEqual(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 2 to 1'][0][0].supply['transfer_services'].current['CoolingWaterTransferService'], 0.8)
#         self.assertEqual(self.sys_test.potential_paths_links['ElectricPowerTransferService']['from 1 to 2'][0][0].supply['transfer_services'].current['ElectricPowerTransferService'], 40)
#         self.assertEqual(self.sys_test.potential_paths_links['ElectricPowerTransferService']['from 2 to 1'][0][0].supply['transfer_services'].current['ElectricPowerTransferService'], 40)
#         self.assertEqual(self.sys_test.potential_paths_links['PotableWaterTransferService']['from 1 to 2'][0][0].supply['transfer_services'].current['PotableWaterTransferService'], 0.8)
#         self.assertEqual(self.sys_test.potential_paths_links['PotableWaterTransferService']['from 2 to 1'][0][0].supply['transfer_services'].current['PotableWaterTransferService'], 0.8)
#         # create the damage vector to test the damaged potential paths
#         damage_vector = [0.0, 0.0, 0.0, 0.3, 0.0, 0.4, 0.01, 0.01, 0.0, 0.0, 0.0, 0.0, 0.35, 0.0, 0.0, 0.0, 0.0]
#         self.sys_test.set_damage(damage_vector)
#         self.sys_test.update()
#         # test the damaged potential paths   - Cooling Water      
#         self.assertEqual(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 1 to 2'][0][0].supply['transfer_services'].current['CoolingWaterTransferService'], 0.8*0.7)
#         self.assertEqual(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 1 to 2'][1][0].supply['transfer_services'].current['CoolingWaterTransferService'], 0.8*0.6)
#         self.assertEqual(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 1 to 2'][1][1].supply['transfer_services'].current['CoolingWaterTransferService'], 0.8*0.65)
#         self.assertEqual(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 2 to 1'][0][0].supply['transfer_services'].current['CoolingWaterTransferService'], 0.8*0.7)
#         self.assertEqual(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 2 to 1'][1][0].supply['transfer_services'].current['CoolingWaterTransferService'], 0.8*0.65)
#         self.assertEqual(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 2 to 1'][1][1].supply['transfer_services'].current['CoolingWaterTransferService'], 0.8*0.6)
#         self.assertEqual(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 2 to 3'][0][0].supply['transfer_services'].current['CoolingWaterTransferService'], 0.8*0.7)
#         self.assertEqual(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 2 to 3'][0][1].supply['transfer_services'].current['CoolingWaterTransferService'], 0.8*0.6)
#         self.assertEqual(self.sys_test.potential_paths_links['CoolingWaterTransferService']['from 2 to 3'][1][0].supply['transfer_services'].current['CoolingWaterTransferService'], 0.8*0.65)
#         # test the damaged paths - Electric Power
#         self.assertEqual(self.sys_test.potential_paths_links['ElectricPowerTransferService']['from 1 to 2'][0][0].supply['transfer_services'].current['ElectricPowerTransferService'], 0.0)
#         self.assertEqual(self.sys_test.potential_paths_links['ElectricPowerTransferService']['from 2 to 1'][0][0].supply['transfer_services'].current['ElectricPowerTransferService'], 0.0)
#         self.assertEqual(self.sys_test.potential_paths_links['ElectricPowerTransferService']['from 2 to 3'][0][0].supply['transfer_services'].current['ElectricPowerTransferService'], 40.0)
#         self.assertEqual(self.sys_test.potential_paths_links['ElectricPowerTransferService']['from 2 to 3'][1][0].supply['transfer_services'].current['ElectricPowerTransferService'], 0.0)
#         self.assertEqual(self.sys_test.potential_paths_links['ElectricPowerTransferService']['from 2 to 3'][1][1].supply['transfer_services'].current['ElectricPowerTransferService'], 0.0)
#         self.assertEqual(self.sys_test.potential_paths_links['ElectricPowerTransferService']['from 3 to 2'][0][0].supply['transfer_services'].current['ElectricPowerTransferService'], 40.0)
#         self.assertEqual(self.sys_test.potential_paths_links['ElectricPowerTransferService']['from 3 to 2'][1][0].supply['transfer_services'].current['ElectricPowerTransferService'], 0.0)
#         self.assertEqual(self.sys_test.potential_paths_links['ElectricPowerTransferService']['from 3 to 2'][1][1].supply['transfer_services'].current['ElectricPowerTransferService'], 0.0)
#         self.assertEqual(self.sys_test.potential_paths_links['ElectricPowerTransferService']['from 3 to 2'][1][0].supply['transfer_services'].current['ElectricPowerTransferService'], 0.0)

#     def test_get_optimal_path(self):
#         # test the algorithm that finds the optimal path from the list of potential paths
#         self.sys_test.create_system(self.two_comp_sys_wlinks)
#         potential_paths = dict()
#         potential_paths['CoolingWaterTransferService'] = {'from 1 to 2': [[1, 2]], 'from 2 to 1': [[2, 1]]}
#         potential_paths['ElectricPowerTransferService'] = {'from 1 to 2': [[1, 2]], 'from 2 to 1': [[2, 1]]} 
#         potential_paths['PotableWaterTransferService'] = {'from 1 to 2': [[1, 2]], 'from 2 to 1': [[2, 1]]} 
#         self.sys_test.set_potential_paths(potential_paths)
#         self.sys_test.create_potential_paths()
#         # test the two localities undamaged system
#         opt_cost, opt_path = self.sys_test.get_optimal_path(1, 2, 'CoolingWaterTransferService')
#         self.assertEqual(opt_cost, 0.8)
#         self.assertEqual(opt_path, 0)        
#         opt_cost, opt_path = self.sys_test.get_optimal_path(2, 1, 'CoolingWaterTransferService')
#         self.assertEqual(opt_cost, 0.8)
#         self.assertEqual(opt_path, 0)        
#         opt_cost, opt_path = self.sys_test.get_optimal_path(1, 2, 'ElectricPowerTransferService')
#         self.assertEqual(opt_cost, 40)
#         self.assertEqual(opt_path, 0)                
#         opt_cost, opt_path = self.sys_test.get_optimal_path(2, 1, 'ElectricPowerTransferService')
#         self.assertEqual(opt_cost, 40)
#         self.assertEqual(opt_path, 0)        
#         # test damaged system        
#         damage_vector = [0.4, 0.0, 0.4, 0.4, 0.4, 0.0]
#         self.sys_test.set_damage(damage_vector)
#         self.sys_test.update()
#         opt_cost, opt_path = self.sys_test.get_optimal_path(1, 2, 'CoolingWaterTransferService')
#         self.assertEqual(opt_cost, 0.8*0.6)
#         self.assertEqual(opt_path, 0)        
#         opt_cost, opt_path = self.sys_test.get_optimal_path(2, 1, 'CoolingWaterTransferService')
#         self.assertEqual(opt_cost, 0.8*0.6)
#         self.assertEqual(opt_path, 0)        
#         opt_cost, opt_path = self.sys_test.get_optimal_path(1, 2, 'ElectricPowerTransferService')
#         self.assertEqual(opt_cost, 0.0)
#         self.assertEqual(opt_path, 0)                
#         opt_cost, opt_path = self.sys_test.get_optimal_path(2, 1, 'ElectricPowerTransferService')
#         self.assertEqual(opt_cost, 0.0)
#         self.assertEqual(opt_path, 0)

#         # test the system with three localities
#         self.sys_test.create_system(self.five_comp_sys_wlinks)
#         # define the dict key as a string from i-th locality to j-th locality, as a list of 
#         # localities that the path will go through
#         self.sys_test.potential_paths['CoolingWaterTransferService'] = {'from 1 to 2': [[1, 2], [1, 3, 2]], 'from 2 to 1': [[2, 1], [2, 3, 1]],
#                                                                         'from 2 to 3': [[2, 1, 3], [2, 3]]}
#         self.sys_test.potential_paths['ElectricPowerTransferService'] = {'from 1 to 2': [[1, 2]], 'from 2 to 1': [[2, 1]],
#                                                                           'from 2 to 3': [[2, 3], [2, 1, 3]], 'from 3 to 2': [[3, 2], [3, 1, 2]]}
#         self.sys_test.create_potential_paths()
#         # test undamaged system
#         opt_cost, opt_path = self.sys_test.get_optimal_path(1, 2, 'CoolingWaterTransferService')
#         self.assertEqual(opt_cost, 0.8)
#         self.assertEqual(opt_path, 0)        
#         opt_cost, opt_path = self.sys_test.get_optimal_path(2, 1, 'CoolingWaterTransferService')
#         self.assertEqual(opt_cost, 0.8)
#         self.assertEqual(opt_path, 0)           
#         opt_cost, opt_path = self.sys_test.get_optimal_path(1, 3, 'CoolingWaterTransferService')
#         self.assertEqual(opt_cost, 0.0)
#         self.assertEqual(opt_path, None) 
#         opt_cost, opt_path = self.sys_test.get_optimal_path(2, 3, 'CoolingWaterTransferService')
#         self.assertEqual(opt_cost, 0.8)
#         self.assertEqual(opt_path, 0) 
#         opt_cost, opt_path = self.sys_test.get_optimal_path(1, 2, 'ElectricPowerTransferService')
#         self.assertEqual(opt_cost, 40)
#         self.assertEqual(opt_path, 0)                
#         opt_cost, opt_path = self.sys_test.get_optimal_path(2, 1, 'ElectricPowerTransferService')
#         self.assertEqual(opt_cost, 40)
#         self.assertEqual(opt_path, 0)
#         opt_cost, opt_path = self.sys_test.get_optimal_path(3, 2, 'ElectricPowerTransferService')
#         self.assertEqual(opt_cost, 40)
#         self.assertEqual(opt_path, 0) 
#         opt_cost, opt_path = self.sys_test.get_optimal_path(1, 3, 'ElectricPowerTransferService')
#         self.assertEqual(opt_cost, 0.0)
#         self.assertEqual(opt_path, None) 
#         # create the damage vector to test the damaged potential paths
#         damage_vector = [0.0, 0.0, 0.0, 0.3, 0.0, 0.4, 0.01, 0.01, 0.0, 0.0, 0.0, 0.0, 0.35, 0.0, 0.0, 0.0, 0.0]
#         self.sys_test.set_damage(damage_vector)
#         self.sys_test.update()
#         # test the damaged potential paths - Cooling Water       
#         opt_cost, opt_path = self.sys_test.get_optimal_path(1, 2, 'CoolingWaterTransferService')
#         self.assertEqual(opt_cost, 0.8*0.7)
#         self.assertEqual(opt_path, 0)        
#         opt_cost, opt_path = self.sys_test.get_optimal_path(2, 1, 'CoolingWaterTransferService')
#         self.assertEqual(opt_cost, 0.8*0.7)
#         self.assertEqual(opt_path, 0)           
#         opt_cost, opt_path = self.sys_test.get_optimal_path(1, 3, 'CoolingWaterTransferService')
#         self.assertEqual(opt_cost, 0.0)
#         self.assertEqual(opt_path, None) 
#         opt_cost, opt_path = self.sys_test.get_optimal_path(2, 3, 'CoolingWaterTransferService')
#         self.assertEqual(opt_cost, 0.65*0.8)
#         self.assertEqual(opt_path, 1) 
#         opt_cost, opt_path = self.sys_test.get_optimal_path(1, 2, 'ElectricPowerTransferService')
#         self.assertEqual(opt_cost, 0.0)
#         self.assertEqual(opt_path, 0)                
#         opt_cost, opt_path = self.sys_test.get_optimal_path(2, 1, 'ElectricPowerTransferService')
#         self.assertEqual(opt_cost, 0.0)
#         self.assertEqual(opt_path, 0)
#         opt_cost, opt_path = self.sys_test.get_optimal_path(3, 2, 'ElectricPowerTransferService')
#         self.assertEqual(opt_cost, 40)
#         self.assertEqual(opt_path, 0) 
#         opt_cost, opt_path = self.sys_test.get_optimal_path(1, 3, 'ElectricPowerTransferService')
#         self.assertEqual(opt_cost, 0.0)
#         self.assertEqual(opt_path, None)

#         # test when the bridge is damaged
#         damage_vector = np.zeros(17)
#         damage_vector[2] = 0.01
#         damage_vector[4] = 0.01
#         self.sys_test.set_damage(damage_vector)
#         self.sys_test.update()
#         self.sys_test.distribute_bridge_transfer_service()
#         opt_cost, opt_path = self.sys_test.get_optimal_path(1, 2, 'CoolingWaterTransferService')
#         self.assertEqual(opt_cost, 0.0)
#         self.assertEqual(opt_path, 0) 
#         opt_cost, opt_path = self.sys_test.get_optimal_path(1, 2, 'ElectricPowerTransferService')
#         self.assertEqual(opt_cost, 0.0)
#         self.assertEqual(opt_path, 0)
#         opt_cost, opt_path = self.sys_test.get_optimal_path(1, 3, 'ElectricPowerTransferService')
#         self.assertEqual(opt_cost, 0.0)
#         self.assertEqual(opt_path, None)
#         opt_cost, opt_path = self.sys_test.get_optimal_path(2, 3, 'CoolingWaterTransferService')
#         self.assertEqual(opt_cost, 0.8)
#         self.assertEqual(opt_path, 1)
#         opt_cost, opt_path = self.sys_test.get_optimal_path(2, 3, 'ElectricPowerTransferService')
#         self.assertEqual(opt_cost, 40)
#         self.assertEqual(opt_path, 0)


#     def test_resource_distribution_two_localities(self):            
#         # test when system is undamaged
#         self.sys_test.create_system(self.two_comp_sys_wlinks)
#         self.sys_test.assemble_system_matrix()
#         self.sys_test.priorities = Priorities.PrioritiesTwoCompSys()
#         self.sys_test.priorities.set_all_priorities(self.sys_test)
#         # set the potential paths
#         potential_paths = dict()
#         potential_paths['CoolingWaterTransferService'] = {'from 1 to 2': [[1, 2]], 'from 2 to 1': [[2, 1]]}
#         potential_paths['ElectricPowerTransferService'] = {'from 1 to 2': [[1, 2]], 'from 2 to 1': [[2, 1]]}
#         potential_paths['PotableWaterTransferService'] = {'from 1 to 2': [[1, 2]], 'from 2 to 1': [[2, 1]]}
#         self.sys_test.set_potential_paths(potential_paths)
#         self.sys_test.create_potential_paths()
#         ep_id = 0
#         self.sys_test.resource_distribution(ep_id)
#         # nothing should change in the system matrix
#         epp_vector = [1, 1, 0.0, 1.0, 1]
#         epp_supply = [40, 0.0, 0.0, 0.0, 0.0]
#         epp_demand = [0.2, 0.0, 0.001, 0.0, 0.05]
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, :5] == epp_vector))   
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, 5:10] == epp_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, 10:15] == epp_supply))
#         bsu_vector = [2, 2, 0, 1, 6]
#         bsu_supply = [0, 0.0, 0.0, 0.0, 0.0]
#         bsu_demand = [7.7, 0.0, 33.3, 0.086, 0.0]
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][4, :5] == bsu_vector))      
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][4, 5:10] == bsu_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][4, 10:15] == bsu_supply))   
#         # test the demand met columns
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][:, self.sys_test.system_matrix_demand_met_col_ids] == 1.0))

#         # test when two comp system is damage - the damage is low enough so that the demand is still met        
#         damage_vector = [0.4, 0.0, 0.0, 0.0, 0.4]
#         self.sys_test.set_damage(damage_vector)
#         self.sys_test.update()
#         self.sys_test.assemble_system_matrix()            
#         self.sys_test.resource_distribution(ep_id)
#         epp_vector = [1, 1, 0.4, 0.6, 1]
#         epp_supply = [40*0.6, 0.0, 0.0, 0.0, 0.0]
#         epp_demand = [0.2, 0.0, 0.001, 0.0, 0.05]
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, :5] == epp_vector))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, 5:10] == epp_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, 10:15] == epp_supply))
#         bsu_vector = [2, 2, 0.4, 0.0, 6]
#         bsu_supply = [0, 0.0, 0.0, 0.0, 0.0]
#         bsu_demand = [7.7*0.0, 0.0, 33.3, 0.086*0.0, 0.0]
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][4, :5] == bsu_vector))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][4, 5:10] == bsu_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][4, 10:15] == bsu_supply))     
#         # test the demand met columns
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][:, self.sys_test.system_matrix_demand_met_col_ids] == 1.0))

#         # test when two comp system is damage - the damage is high enough so that the demand is not met
#         damage_vector = [0.9, 0.0, 0.0, 0.0, 0.0]
#         self.sys_test.set_damage(damage_vector)
#         self.sys_test.update()
#         self.sys_test.assemble_system_matrix()
#         self.sys_test.resource_distribution(ep_id)
#         epp_vector = [1, 1, 0.9, 0.1, 1]
#         epp_supply = [40*0.1, 0.0, 0.0, 0.0, 0.0]
#         epp_demand = [0.2, 0.0, 0.001, 0.0, 0.05]
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, :5] == epp_vector))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, 5:10] == epp_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, 10:15] == epp_supply))
#         bsu_vector = [2, 2, 0, 1, 6]
#         bsu_supply = [0, 0.0, 0.0, 0.0, 0.0]
#         bsu_demand = [7.7, 0.0, 33.3, 0.086, 0.0]
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][4, :5] == bsu_vector))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][4, 5:10] == bsu_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][4, 10:15] == bsu_supply))     
#         # test the demand met columns
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, self.sys_test.system_matrix_demand_met_col_ids] == 1.0))
#         # demand met indicator for ep for bsu should be zero
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][4, self.sys_test.system_matrix_demand_met_col_ids[ep_id]] == 0.0))

#         # test with multiple users and one supplier
#         # add one more user to the input dict
#         self.two_comp_sys_wlinks[1] = {'LocalityID': 2,
#                                 'Coord. X': 5,
#                                 'Coord. Y': 5,
#                                 'Content': {'BSU': 2},
#                                 # LinkTo field determines which link types is connected to which locality_id
#                                 # here locality 1 is connected to locality 2 with one CWP and one EPTL
#                                 'LinkTo': {'CWP': [1], 'EPTL': [1]},
#                                 'BridgeTo': {'CWP': [1],
#                                            'EPTL': [1],
#                                            }} 
#         self.sys_test.create_system(self.two_comp_sys_wlinks)
#         # recreate potential paths - because the components have changed
#         self.sys_test.create_potential_paths()
#         # first test with low damage - there should be enough supply
#         damage_vector = [0.1, 0.0, 0.0, 0.0, 0.4, 0.3]
#         self.sys_test.set_damage(damage_vector)
#         self.sys_test.update()
#         self.sys_test.assemble_system_matrix()
#         self.sys_test.priorities = Priorities.PrioritiesTwoCompSys()
#         self.sys_test.priorities.set_all_priorities(self.sys_test)
#         self.sys_test.resource_distribution(ep_id)
#         epp_vector = [1, 1, 0.1, 0.9, 1]
#         epp_supply = [40*0.9, 0.0, 0.0, 0.0, 0.0]
#         epp_demand = [0.2, 0.0, 0.001, 0.0, 0.05]
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, :5] == epp_vector))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, 5:10] == epp_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, 10:15] == epp_supply))
#         bsu1_vector = [2, 2, 0.4, 0.0, 6]
#         bsu1_supply = [0, 0.0, 0.0, 0.0, 0.0]
#         bsu1_demand = [7.7*0.0, 0.0, 33.3, 0.086*0.0, 0.0]
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][4, :5] == bsu1_vector))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][4, 5:10] == bsu1_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][4, 10:15] == bsu1_supply))  
#         bsu2_vector = [2, 2, 0.3, 1.0, 6]
#         bsu2_supply = [0, 0.0, 0.0, 0.0, 0.0]
#         bsu2_demand = [7.7*1.0, 0.0, 33.3, 0.086*1.0, 0.0]
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][5, :5] == bsu2_vector))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][5, 5:10] == bsu2_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][5, 10:15] == bsu2_supply))
#         # test the demand met columns
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][:, self.sys_test.system_matrix_demand_met_col_ids] == 1.0))
#         # now test with high damage - no user gets enough ep
#         damage_vector = [0.9, 0.0, 0.0, 0.0, 0.1, 0.1]
#         self.sys_test.set_damage(damage_vector)
#         self.sys_test.update()
#         self.sys_test.assemble_system_matrix()
#         self.sys_test.resource_distribution(ep_id)
#         epp_vector = [1, 1, 0.9, 0.1, 1]
#         epp_supply = [40*0.1, 0.0, 0.0, 0.0, 0.0]
#         epp_demand = [0.2, 0.0, 0.001, 0.0, 0.05]
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, :5] == epp_vector))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, 5:10] == epp_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, 10:15] == epp_supply))
#         bsu1_vector = [2, 2, 0.1, 1.0, 6]
#         bsu1_supply = [0, 0.0, 0.0, 0.0, 0.0]
#         bsu1_demand = [7.7*1.0, 0.0, 33.3, 0.086*1.0, 0.0]
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][4, :5] == bsu1_vector))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][4, 5:10] == bsu1_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][4, 10:15] == bsu1_supply))  
#         bsu2_vector = [2, 2, 0.1, 1.0, 6]
#         bsu2_supply = [0, 0.0, 0.0, 0.0, 0.0]
#         bsu2_demand = [7.7*1.0, 0.0, 33.3, 0.086*1.0, 0.0]
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][5, :5] == bsu2_vector))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][5, 5:10] == bsu2_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][5, 10:15] == bsu2_supply))
#         # test the demand met columns
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, self.sys_test.system_matrix_demand_met_col_ids] == 1.0))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][4:, self.sys_test.system_matrix_demand_met_col_ids[ep_id]] == 0.0))

#         # test with damaged links - damaged CWP
#         damage_vector = [0.0, 0.0, 1.0, 0.0, 0.0, 0.0]
#         self.sys_test.set_damage(damage_vector)
#         self.sys_test.update()
#         self.sys_test.assemble_system_matrix() 
#         # distribute power - everything should still be working since only the CWP is damaged
#         self.sys_test.resource_distribution(ep_id)
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][:, self.sys_test.system_matrix_demand_met_col_ids] == 1.0))
#         # set the damage to the EPTL - minimal damage should still cause a loss of transfer supply
#         damage_vector = [0.0, 0.0, 0.0, 0.01, 0.0, 0.0]
#         self.sys_test.set_damage(damage_vector)
#         self.sys_test.update()
#         self.sys_test.assemble_system_matrix()
#         self.sys_test.resource_distribution(ep_id)
#         # the demand of BSUs for power should not be met
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][-2:, self.sys_test.system_matrix_demand_met_col_ids[0]] == 0.0))
#         # repair the system once and check again - now the EPTL should be functional
#         self.sys_test.repair()
#         self.sys_test.update()
#         self.sys_test.assemble_system_matrix()
#         self.sys_test.resource_distribution(ep_id)
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][-2:, self.sys_test.system_matrix_demand_met_col_ids[0]] == 1.0))       


#     def test_resource_distribution_five_components(self):             
#         # test with multiple suppliers and multiple users - 5-comp system
#         self.sys_test.create_system(self.five_comp_sys_wlinks)
#         self.sys_test.assemble_system_matrix()
#         self.sys_test.priorities = Priorities.PrioritiesFiveCompSys()
#         self.sys_test.priorities.set_all_priorities(self.sys_test)
#         potential_paths = dict()
#         potential_paths['CoolingWaterTransferService'] = {'from 1 to 2': [[1, 2], [1, 3, 2]], 'from 2 to 1': [[2, 1], [2, 3, 1]],
#                                                           'from 1 to 3': [[1, 3], [1, 2, 3]], 'from 3 to 1': [[3, 1], [3, 2, 1]],
#                                                           'from 2 to 3': [[2, 3]], 'from 3 to 2': [[3, 2]]}
#         potential_paths['ElectricPowerTransferService'] = {'from 1 to 2': [[1, 2], [1, 3, 2]], 'from 2 to 1': [[2, 1], [2, 3, 1]],
#                                                           'from 1 to 3': [[1, 3], [1, 2, 3]], 'from 3 to 1': [[3, 1], [3, 2, 1]],
#                                                           'from 2 to 3': [[2, 3]], 'from 3 to 2': [[3, 2]]}
#         potential_paths['PotableWaterTransferService'] = {'from 1 to 2': [[1, 2], [1, 3, 2]], 'from 2 to 1': [[2, 1], [2, 3, 1]],
#                                                           'from 1 to 3': [[1, 3], [1, 2, 3]], 'from 3 to 1': [[3, 1], [3, 2, 1]],
#                                                           'from 2 to 3': [[2, 3]], 'from 3 to 2': [[3, 2]]}
#         self.sys_test.set_potential_paths(potential_paths)
#         self.sys_test.create_potential_paths()
#         # distribute all rss 
#         ep_id = 0
#         self.sys_test.resource_distribution(ep_id)
#         llc_id = 2
#         self.sys_test.resource_distribution(llc_id)
#         cw_id = 4
#         self.sys_test.resource_distribution(cw_id)
#         # nothing should change in the system matrix - no damage
#         # only testing EPP and BSU
#         epp_vector = [1, 1, 0.0, 1.0, 1]
#         epp_supply = [40, 0.0, 0.0, 0.0, 0.0]
#         epp_demand = [0.2, 0.0, 0.001, 0.0, 0.05]
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, :5] == epp_vector))   
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, 5:10] == epp_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, 10:15] == epp_supply))
#         bsu_vector = [3, 3, 0, 1, 6]
#         bsu_supply = [0, 0.0, 0.0, 0.0, 0.0]
#         bsu_demand = [7.7, 0.0, 33.3, 0.086, 0.0]        
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][16, :5] == bsu_vector))      
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][16, 5:10] == bsu_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][16, 10:15] == bsu_supply))   
#         # test the demand met columns
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][:, self.sys_test.system_matrix_demand_met_col_ids] == 1.0))        

#         # test with damaged community - EPP is damaged
#         damage_vector = np.zeros(len(self.sys_test.components))
#         damage_vector[0] = 0.999
#         self.sys_test.set_damage(damage_vector)
#         self.sys_test.time_step = 2
#         self.sys_test.update()
#         self.sys_test.assemble_system_matrix()
#         # test the system matrix
#         epp_vector = [1, 1, 0.999, 0.001, 1]
#         epp_supply = [0.001 * 40, 0.0, 0.0, 0.0, 0.0]
#         epp_demand = [0.2, 0.0, 0.001, 0.0, 0.05]  
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][0, :5] == epp_vector))   
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][0, 5:10] == epp_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][0, 10:15] == epp_supply))
#         bts_1_vector = [1, 1, 0.0, 1.0, 3]
#         bts_1_supply = [0.0, 0.0, 45.0, 0.0, 0.0]
#         bts_1_demand = [0.1, 50.0, 0.0, 0.0, 0.0]
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][1, :5] == bts_1_vector))   
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][1, 5:10] == bts_1_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][1, 10:15] == bts_1_supply))   
#         # test rs distribution
#         # distribute EP
#         ep_id = 0
#         self.sys_test.resource_distribution(ep_id, consider_interdep = True)     
#         # check the demand met columns
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][[0, 1, 10, 15, 16], self.sys_test.system_matrix_demand_met_col_ids[0]] == 0.0))

#         # test damaged links - damage the bridge from 1 to 2
#         damage_vector = np.zeros(len(self.sys_test.components))
#         damage_vector[2] = 0.01
#         self.sys_test.set_damage(damage_vector)
#         self.sys_test.update()
#         self.sys_test.assemble_system_matrix()
#         # distribute EP
#         ep_id = 0
#         self.sys_test.resource_distribution(ep_id, consider_interdep = True)  
#         # because the paths are redundant, even though the bridge is damaged, the demand of all components should be met
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][:, self.sys_test.system_matrix_demand_met_col_ids] == 1.0))      

#         # damage the CWP from 1 to 2 - nothing should change
#         damage_vector = np.zeros(len(self.sys_test.components))
#         damage_vector[3] = 1.0
#         self.sys_test.set_damage(damage_vector)
#         self.sys_test.update()
#         self.sys_test.assemble_system_matrix()       
#         # distribute CW
#         cw_id = 4
#         self.sys_test.resource_distribution(cw_id, consider_interdep = True)
#         # test the demand met columns
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][:, self.sys_test.system_matrix_demand_met_col_ids] == 1.0))      

#         # change potential paths - reduce redundancy
#         potential_paths['CoolingWaterTransferService'] = {'from 1 to 2': [[1, 2]], 'from 2 to 1': [[2, 1]],
#                                                           'from 1 to 3': [[1, 3]], 'from 3 to 1': [[3, 1]],
#                                                           'from 2 to 3': [[2, 3]], 'from 3 to 2': [[3, 2]]}
#         potential_paths['ElectricPowerTransferService'] = {'from 1 to 2': [[1, 2]], 'from 2 to 1': [[2, 1]],
#                                                           'from 1 to 3': [[1, 3]], 'from 3 to 1': [[3, 1]],
#                                                           'from 2 to 3': [[2, 3]], 'from 3 to 2': [[3, 2]]}
#         potential_paths['PotableWaterTransferService'] = {'from 1 to 2': [[1, 2]], 'from 2 to 1': [[2, 1]],
#                                                           'from 1 to 3': [[1, 3]], 'from 3 to 1': [[3, 1]],
#                                                           'from 2 to 3': [[2, 3]], 'from 3 to 2': [[3, 2]]}
#         self.sys_test.set_potential_paths(potential_paths)
#         self.sys_test.create_potential_paths()
#         # damage the CWP from 1 to 2
#         damage_vector = np.zeros(len(self.sys_test.components))
#         damage_vector[3] = 1.0
#         self.sys_test.set_damage(damage_vector)
#         self.sys_test.update()
#         self.sys_test.assemble_system_matrix()  
#         # EPP should not get CW - CWP is too damaged
#         self.sys_test.resource_distribution(cw_id, consider_interdep = True)
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][0, self.sys_test.system_matrix_demand_met_col_ids[cw_id]] == 0.0))   

#         damage_vector = np.zeros(len(self.sys_test.components))
#         damage_vector[3] = 0.5
#         self.sys_test.set_damage(damage_vector)
#         self.sys_test.update()
#         # self.sys_test.create_potential_paths()
#         self.sys_test.assemble_system_matrix()  
#         # EPP should get CW - CWP is damaged but its transfer supply is still laarger than the demand
#         self.sys_test.resource_distribution(cw_id, consider_interdep = True)
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][0, self.sys_test.system_matrix_demand_met_col_ids[cw_id]] == 1.0)) 

#         # damage the bridge from 1 to 2
#         damage_vector = np.zeros(len(self.sys_test.components))
#         damage_vector[2] = 1.0
#         self.sys_test.set_damage(damage_vector)
#         self.sys_test.update()
#         self.sys_test.distribute_bridge_transfer_service()
#         self.sys_test.assemble_system_matrix()
#         self.sys_test.resource_distribution(cw_id, consider_interdep = True)
#         # EPP should not get CW
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][0, self.sys_test.system_matrix_demand_met_col_ids[cw_id]] == 0.0))  

#         # continue writing test for situations you find out are sketchy


#     def test_get_supply_capacities(self):
#         self.sys_test.create_system(self.five_comp_sys_wlinks)
#         self.sys_test.assemble_system_matrix()
#         expected_supply_caps = [40, 0, 45, 0.2, 0.06]
#         supply_capacities = self.sys_test.get_supply_capacities()
#         self.assertTrue(np.all(expected_supply_caps == supply_capacities))

#         # test when system is damaged
#         damage_vector = np.zeros(len(self.sys_test.components))
#         # damage only the facilities
#         damage_vector[0] = 0.5
#         damage_vector[1] = 0.1
#         damage_vector[10] = 0.5
#         damage_vector[15] = 0.1
#         self.sys_test.set_damage(damage_vector)      
#         self.sys_test.update()
#         self.sys_test.assemble_system_matrix()        
#         expected_supply_caps = [20, 0.0, 0.0, 0.0, 0.03]
#         supply_capacities = np.round(self.sys_test.get_supply_capacities(), 5)
#         self.assertTrue(np.all(expected_supply_caps == supply_capacities))

#     def test_get_total_demand(self):
#         self.sys_test.create_system(self.five_comp_sys_wlinks)
#         self.sys_test.assemble_system_matrix()
#         expected_demands = [8.3, 50, 33.302, 0.086, 0.05]
#         total_demand = np.round(self.sys_test.get_total_demand(), 5)        
#         self.assertTrue(np.all(expected_demands == total_demand))

#         # test when system is damaged
#         damage_vector = np.zeros(len(self.sys_test.components))
#         # damage only the facilities
#         damage_vector[0] = 0.5
#         damage_vector[1] = 0.1
#         damage_vector[10] = 0.5
#         damage_vector[15] = 0.1
#         damage_vector[16] = 0.1
#         self.sys_test.set_damage(damage_vector)      
#         self.sys_test.update()
#         self.sys_test.assemble_system_matrix()
#         expected_demands = [8.1, 0.0, 33.302, 0.086, 0.05]        
#         total_demand = np.round(self.sys_test.get_total_demand(), 5)   
#         self.assertTrue(np.all(expected_demands == total_demand))

#         # test when llc surges
#         self.sys_test.time_step = 2
#         self.sys_test.update()
#         self.sys_test.assemble_system_matrix()
#         expected_demands = [8.1, 0.0, 333.002, 0.086, 0.05]        
#         total_demand = np.round(self.sys_test.get_total_demand(), 5)   
#         self.assertTrue(np.all(expected_demands == total_demand))

#     def test_get_total_consumption(self):
#         self.sys_test.create_system(self.five_comp_sys_wlinks)
#         self.sys_test.assemble_system_matrix()
#         expected_cons = [8.3, 50, 33.302, 0.086, 0.05]
#         total_cons = np.round(self.sys_test.get_total_consumption(), 5)        
#         self.assertTrue(np.all(expected_cons == total_cons))

#         # test when system is damaged
#         damage_vector = np.zeros(len(self.sys_test.components))
#         # damage only the facilities
#         damage_vector[0] = 0.5
#         damage_vector[1] = 0.1
#         damage_vector[10] = 0.5
#         damage_vector[15] = 0.1
#         damage_vector[16] = 0.4
#         self.sys_test.set_damage(damage_vector)      
#         self.sys_test.update()
#         self.sys_test.assemble_system_matrix()
#         self.sys_test.priorities = Priorities.PrioritiesFiveCompSys()
#         self.sys_test.priorities.set_all_priorities(self.sys_test)
#         # set up potential paths
#         potential_paths = dict()
#         potential_paths['CoolingWaterTransferService'] = {'from 1 to 2': [[1, 2]], 'from 2 to 1': [[2, 1]],
#                                                           'from 1 to 3': [[1, 3]], 'from 3 to 1': [[3, 1]],
#                                                           'from 2 to 3': [[2, 3]], 'from 3 to 2': [[3, 2]]}
#         potential_paths['ElectricPowerTransferService'] = {'from 1 to 2': [[1, 2]], 'from 2 to 1': [[2, 1]],
#                                                           'from 1 to 3': [[1, 3]], 'from 3 to 1': [[3, 1]],
#                                                           'from 2 to 3': [[2, 3]], 'from 3 to 2': [[3, 2]]}
#         potential_paths['PotableWaterTransferService'] = {'from 1 to 2': [[1, 2]], 'from 2 to 1': [[2, 1]],
#                                                           'from 1 to 3': [[1, 3]], 'from 3 to 1': [[3, 1]],
#                                                           'from 2 to 3': [[2, 3]], 'from 3 to 2': [[3, 2]]}
#         self.sys_test.set_potential_paths(potential_paths)
#         self.sys_test.create_potential_paths()
#         ep_id = 0
#         self.sys_test.resource_distribution(ep_id, consider_interdep = True)  
#         # test consumption after distributing electricity - for this level of damage, all demands should be met
#         expected_cons = [0.4, 0.0, 33.302, 0.0, 0.05]
#         total_cons = np.round(self.sys_test.get_total_consumption(), 5)        
#         self.assertTrue(np.all(expected_cons == total_cons))        
#         cw_id = 4
#         self.sys_test.resource_distribution(cw_id, consider_interdep = True)
#         # test consumption after distributing CW - EPP should not get enough
#         expected_cons = [0.4, 0.0, 33.302, 0.0, 0.0]
#         total_cons = np.round(self.sys_test.get_total_consumption(), 5)        
#         self.assertTrue(np.all(expected_cons == total_cons))       
#         # test the consumption after distributing LLC - 
#         llc_id = 2
#         self.sys_test.resource_distribution(llc_id, consider_interdep = True) 
#         expected_cons = [0.4, 0.0, 0.0, 0.0, 0.0]
#         total_cons = np.round(self.sys_test.get_total_consumption(), 5)        
#         self.assertTrue(np.all(expected_cons == total_cons))       

#         # test when links are damaged

#         # damage EPTLs
#         damage_vector = np.zeros(len(self.sys_test.components))
#         # damage EPTL from 1 to 2
#         damage_vector[6] = 0.99
#         self.sys_test.set_damage(damage_vector)      
#         self.sys_test.update()
#         self.sys_test.assemble_system_matrix()
#         # should have no effect on CWF and LLC
#         self.sys_test.resource_distribution(cw_id, consider_interdep = True)
#         self.sys_test.resource_distribution(llc_id, consider_interdep = True) 
#         expected_cons = [8.3, 50, 33.302, 0.086, 0.05]
#         total_cons = np.round(self.sys_test.get_total_consumption(), 5)        
#         self.assertTrue(np.all(expected_cons == total_cons))
#         # should prevent EP from reaching CWF at locality 2
#         self.sys_test.resource_distribution(ep_id, consider_interdep = True)
#         expected_cons = [8.1, 50, 33.302, 0.086, 0.05]
#         total_cons = np.round(self.sys_test.get_total_consumption(), 5)        
#         self.assertTrue(np.all(expected_cons == total_cons))

#         # damage also the EPTL from 2 to 3 - should have no effect
#         damage_vector[13] = 0.01
#         self.sys_test.set_damage(damage_vector)      
#         self.sys_test.update()
#         self.sys_test.assemble_system_matrix()
#         self.sys_test.resource_distribution(ep_id, consider_interdep = True)
#         expected_cons = [8.1, 50, 33.302, 0.086, 0.05]
#         total_cons = np.round(self.sys_test.get_total_consumption(), 5)        
#         self.assertTrue(np.all(expected_cons == total_cons))

#         # damage the EPTL from 1 to 3 - should prevent EP from reaching PWF and BSU
#         damage_vector[7] = 0.01
#         self.sys_test.set_damage(damage_vector)      
#         self.sys_test.update()
#         self.sys_test.assemble_system_matrix()
#         self.sys_test.resource_distribution(ep_id, consider_interdep = True)
#         expected_cons = [0.3, 50, 33.302, 0.086, 0.05]
#         total_cons = np.round(self.sys_test.get_total_consumption(), 5)        
#         self.assertTrue(np.all(expected_cons == total_cons))       


#     def test_interdependency_modelling(self):
#         # add a BSC to the five comp system - to enable the functioning of BTS
#         # add one more CWF - to meet the demand of the BSC
#         self.five_comp_sys_wlinks[1] = {'LocalityID': 2,
#                                 'Coord. X': 0,
#                                 'Coord. Y': 0,
#                                 'Content': {'CWF': 2,
#                                             'BSC': 1},
#                                 'LinkTo': {'CWP': [1, 3],
#                                            'EPTL': [1, 3],
#                                            'PWP': [1, 3]},
#                                 'BridgeTo': {'CWP': [1, 3],
#                                            'EPTL': [1, 3]}}
#         # test interdependency modelling with the five_comp system
#         self.sys_test.create_system(self.five_comp_sys_wlinks)
#         self.sys_test.priorities = Priorities.PrioritiesFiveCompSys()
#         self.sys_test.priorities.set_all_priorities(self.sys_test)
#         # set up potential paths
#         potential_paths = dict()
#         potential_paths['CoolingWaterTransferService'] = {'from 1 to 2': [[1, 2]], 'from 2 to 1': [[2, 1]],
#                                                           'from 1 to 3': [[1, 3]], 'from 3 to 1': [[3, 1]],
#                                                           'from 2 to 3': [[2, 3]], 'from 3 to 2': [[3, 2]]}
#         potential_paths['ElectricPowerTransferService'] = {'from 1 to 2': [[1, 2]], 'from 2 to 1': [[2, 1]],
#                                                           'from 1 to 3': [[1, 3]], 'from 3 to 1': [[3, 1]],
#                                                           'from 2 to 3': [[2, 3]], 'from 3 to 2': [[3, 2]]}
#         potential_paths['PotableWaterTransferService'] = {'from 1 to 2': [[1, 2]], 'from 2 to 1': [[2, 1]],
#                                                           'from 1 to 3': [[1, 3]], 'from 3 to 1': [[3, 1]],
#                                                           'from 2 to 3': [[2, 3]], 'from 3 to 2': [[3, 2]]}
#         self.sys_test.set_potential_paths(potential_paths)
#         self.sys_test.create_potential_paths()
#         self.sys_test.interdependency_modelling(consider_interdep = True)
#         # there should be enough supply for all components - check the demand met columns
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][:, self.sys_test.system_matrix_demand_met_col_ids] == 1.0))

#         # damage the bridge from 1 to 3 - should prevent the functionality of PWF and BSU
#         damage_vector = np.zeros(len(self.sys_test.components))
#         # damage EPTL from 1 to 2
#         damage_vector[4] = 0.1
#         self.sys_test.set_damage(damage_vector)      
#         self.sys_test.update()
#         self.sys_test.interdependency_modelling(consider_interdep = True)
#         # BSU should have no power and potable water
#         ep_id = 0
#         pw_id = 3        
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][18, self.sys_test.system_matrix_demand_met_col_ids[ep_id]] == 0.0))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][18, self.sys_test.system_matrix_demand_met_col_ids[pw_id]] == 0.0))
#         # PWF should have no power
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][17, self.sys_test.system_matrix_demand_met_col_ids[ep_id]] == 0.0))

#         # damage the CWP from 1 to 2 - should prevent the EPP from getting CWF and cause chaos (components do not have power)
#         damage_vector = np.zeros(len(self.sys_test.components))   
#         damage_vector[3] = 0.99 # CWP will have a transfer capacity of 0.008
#         self.sys_test.set_damage(damage_vector)      
#         self.sys_test.update()
#         self.sys_test.interdependency_modelling(consider_interdep = True)
#         # test whether the demands are met
#         cw_id = 4
#         llc_id = 2
#         hlc_id = 1
#         # EPP should not get CW, and therefore the BSC won't get power and EPP won't also get LLC
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, self.sys_test.system_matrix_demand_met_col_ids[cw_id]] == 0.0))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][0, self.sys_test.system_matrix_demand_met_col_ids[llc_id]] == 0.0))
#         # BTS should not get power and HLC
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][1, self.sys_test.system_matrix_demand_met_col_ids[ep_id]] == 0.0))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][1, self.sys_test.system_matrix_demand_met_col_ids[hlc_id]] == 0.0))
#         # BSC should not get EP and CW
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][12, self.sys_test.system_matrix_demand_met_col_ids[ep_id]] == 0.0))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][12, self.sys_test.system_matrix_demand_met_col_ids[cw_id]] == 0.0))
#         # CWFs should not get EP and LLC
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][10, self.sys_test.system_matrix_demand_met_col_ids[ep_id]] == 0.0))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][10, self.sys_test.system_matrix_demand_met_col_ids[llc_id]] == 0.0))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][11, self.sys_test.system_matrix_demand_met_col_ids[ep_id]] == 0.0))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][11, self.sys_test.system_matrix_demand_met_col_ids[llc_id]] == 0.0))
#         # PWF should not get EP 
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][17, self.sys_test.system_matrix_demand_met_col_ids[ep_id]] == 0.0))
#         # BSU should not get EP, LLC and PW
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][18, self.sys_test.system_matrix_demand_met_col_ids[ep_id]] == 0.0))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][18, self.sys_test.system_matrix_demand_met_col_ids[llc_id]] == 0.0))
#         self.assertTrue(np.all(self.sys_test.system_matrix[0][18, self.sys_test.system_matrix_demand_met_col_ids[pw_id]] == 0.0))

#     def test_check_recovery_target(self):
#         self.sys_test.create_system(self.five_comp_sys)
#         # when initialized the recovery traget should be met - all components are initialized with 0 damage level
#         self.assertTrue(self.sys_test.check_recovery_target())

#         # test when system is damaged
#         damage_vector = np.zeros(len(self.sys_test.components))
#         # damage one facility
#         damage_vector[0] = 0.5

#         self.sys_test.set_damage(damage_vector)     
#         self.sys_test.update() 
#         self.assertTrue(not(self.sys_test.check_recovery_target()))

#         # repair the system and then test the condition - assumed repair rate is 0.1, so it recovers in 4 time steps
#         for i in range(50):
#             self.sys_test.repair()

#         self.assertTrue(self.sys_test.check_recovery_target())

#     def test_recovery_simulation(self):
#         self.sys_test.create_system(self.five_comp_sys)
#         self.sys_test.priorities = Priorities.PrioritiesFiveCompSys()
#         self.sys_test.priorities.set_all_priorities(self.sys_test)
#         damage_vector = [0.4, 0.0, 0.4, 0.4, 0.4]
#         self.sys_test.recovery_simulation(damage_vector, plot_LoR=False)
#         self.assertEqual(len(self.sys_test.system_matrix), 7)        
#         # TODO: Implement more tests - test the system matrix at each time_step!


#     def test_calculate_LoR(self):
#         self.sys_test.create_system(self.five_comp_sys)
#         self.sys_test.priorities = Priorities.PrioritiesFiveCompSys()
#         self.sys_test.priorities.set_all_priorities(self.sys_test)
#         damage_vector = [0.4, 0.0, 0.4, 0.4, 0.4]
#         self.sys_test.recovery_simulation(damage_vector, plot_LoR = False)

#         # TODO: test the LoR values for the five component community without links

#     def test_create_links(self):
#         self.sys_test.create_system(self.two_comp_sys_wlinks)        
#         cwp = [self.sys_test.components[i] for i,component in enumerate(self.sys_test.components) if type(component)==Component.CWP]
#         eptl = [self.sys_test.components[i] for i,component in enumerate(self.sys_test.components) if type(component)==Component.EPTL]
#         # check if there is only one CWP - there is no duplication of links
#         self.assertEqual(len(cwp), 1)
#         self.assertEqual(len(eptl), 1)
#         # check link type  
#         # get the variables from the list
#         cwp = cwp[0]
#         eptl = eptl[0]
#         self.assertTrue(Component.CWP == type(cwp))
#         self.assertTrue(Component.EPTL == type(eptl))
#         self.assertTrue(cwp.start_locality == 1)
#         self.assertTrue(cwp.end_locality == 2)
#         self.assertTrue(eptl.start_locality == 1)
#         self.assertTrue(eptl.end_locality == 2)
#         # TODO: Test with five comp system

#     def test_assemble_transfer_supply_matrix(self):
#         self.sys_test.create_system(self.two_comp_sys_wlinks)
#         self.sys_test.assemble_transfer_supply_matrix()
#         transfer_supply_matrix = self.sys_test.transfer_supply_matrix[0]
#         # test whether the matrix picked up all the considered transfer services
#         self.assertTrue(np.all([transfer_service in transfer_supply_matrix for transfer_service in self.sys_test.considered_transfer_services]))
#         self.assertTrue(np.shape(transfer_supply_matrix['ElectricPowerTransferService']) == (2, 2))
#         # test whether diagonal values are infinite
#         self.assertTrue(np.all([transfer_supply_matrix['ElectricPowerTransferService'][0, 0] == math.inf,
#                                 transfer_supply_matrix['ElectricPowerTransferService'][1, 1] == math.inf]))
#         # test offdiagonal values
#         self.assertTrue(np.all([transfer_supply_matrix['ElectricPowerTransferService'][0, 1] == 5,
#                                 transfer_supply_matrix['ElectricPowerTransferService'][1, 0] == 5]))
#         # test the offdiagonal values
#         self.assertTrue(np.all([transfer_supply_matrix['CoolingWaterTransferService'][0, 1] == 3,
#                                 transfer_supply_matrix['CoolingWaterTransferService'][1, 0] == 3]))
#         # test five comp sys with links
#         self.sys_test.create_system(self.five_comp_sys_wlinks)
#         self.sys_test.assemble_transfer_supply_matrix()
#         transfer_supply_matrix = self.sys_test.transfer_supply_matrix[0]
#         self.assertTrue(np.shape(transfer_supply_matrix['ElectricPowerTransferService']) == (3, 3))
#         # test offdiagonal values
#         self.assertTrue(np.all([transfer_supply_matrix['ElectricPowerTransferService'][0, 1] == 5,                              
#                                 transfer_supply_matrix['ElectricPowerTransferService'][1, 0] == 5,
#                                 transfer_supply_matrix['ElectricPowerTransferService'][2, 0] == 5,
#                                 transfer_supply_matrix['ElectricPowerTransferService'][0, 2] == 5,
#                                 transfer_supply_matrix['ElectricPowerTransferService'][1, 2] == 5,
#                                 transfer_supply_matrix['ElectricPowerTransferService'][2, 1] == 5,
#                                 transfer_supply_matrix['ElectricPowerTransferService'][0, 0] == math.inf,
#                                 transfer_supply_matrix['ElectricPowerTransferService'][1, 1] == math.inf,
#                                 transfer_supply_matrix['ElectricPowerTransferService'][2, 2] == math.inf]))
#         # test the offdiagonal values
#         self.assertTrue(np.all([transfer_supply_matrix['CoolingWaterTransferService'][0, 1] == 3,
#                                 transfer_supply_matrix['CoolingWaterTransferService'][1, 0] == 3]))

#         # test when system is damaged
#         # set all components to 0.4 damage level
#         damage_vector = [0.4 for _ in self.sys_test.components]
#         self.sys_test.set_damage(damage_vector)
#         self.sys_test.update()
#         self.sys_test.assemble_transfer_supply_matrix()
#         transfer_supply_matrix = self.sys_test.transfer_supply_matrix[0]
#         # test EPTLs - binary links
#         self.assertTrue(np.all([transfer_supply_matrix['ElectricPowerTransferService'][0, 1] == 0,                              
#                                 transfer_supply_matrix['ElectricPowerTransferService'][1, 0] == 0,
#                                 transfer_supply_matrix['ElectricPowerTransferService'][2, 0] == 0,
#                                 transfer_supply_matrix['ElectricPowerTransferService'][0, 2] == 0,
#                                 transfer_supply_matrix['ElectricPowerTransferService'][1, 2] == 0,
#                                 transfer_supply_matrix['ElectricPowerTransferService'][2, 1] == 0,
#                                 transfer_supply_matrix['ElectricPowerTransferService'][0, 0] == math.inf,
#                                 transfer_supply_matrix['ElectricPowerTransferService'][1, 1] == math.inf,
#                                 transfer_supply_matrix['ElectricPowerTransferService'][2, 2] == math.inf]))

#         # test CWPs - linear links
#         self.assertTrue(np.all([transfer_supply_matrix['CoolingWaterTransferService'][0, 1] == 3*0.6,                              
#                                 transfer_supply_matrix['CoolingWaterTransferService'][1, 0] == 3*0.6,
#                                 transfer_supply_matrix['CoolingWaterTransferService'][2, 0] == 3*0.6,
#                                 transfer_supply_matrix['CoolingWaterTransferService'][0, 2] == 3*0.6,
#                                 transfer_supply_matrix['CoolingWaterTransferService'][1, 2] == 3*0.6,
#                                 transfer_supply_matrix['CoolingWaterTransferService'][2, 1] == 3*0.6,
#                                 transfer_supply_matrix['CoolingWaterTransferService'][0, 0] == math.inf,
#                                 transfer_supply_matrix['CoolingWaterTransferService'][1, 1] == math.inf,
#                                 transfer_supply_matrix['CoolingWaterTransferService'][2, 2] == math.inf]))

# =============================================================================
#     def test_interdependency_modelling_irecodes_small_example(self):
#         # TODO: Needs to be properly initialized - component properties need to be set
#         # test damaged system
#         damage_vector = [0.4, 0.0, 0.4, 0.4, 0.4]
#         self.sys_test.set_damage(damage_vector)
#         self.sys_test.time_step = 2
#         self.sys_test.update()        
#         self.sys_test.interdependency_modelling()
#         # test the system matrix - following the example from the iReCoDeS paper
#         epp_vector = [1, 1, 0.4, 0.6, 1]
#         epp_supply = [0.0, 0.0, 0.0, 0.0, 0.0]
#         epp_demand = [0.0, 0.0, 1.0, 0.0, 1.0]  
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][0, :5] == epp_vector))   
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][0, 5:10] == epp_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][0, 10:15] == epp_supply))
#         bts_1_vector = [1, 1, 0.0, 1.0, 3]
#         bts_1_supply = [0.0, 0.0, 0.0, 0.0, 0.0]
#         bts_1_demand = [1.0, 0.0, 0.0, 0.0, 0.0]
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][1, :5] == bts_1_vector))   
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][1, 5:10] == bts_1_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][1, 10:15] == bts_1_supply))
#         cwf_vector = [2, 2, 0.4, 0.6, 5]
#         cwf_supply = [0.0, 0.0, 0.0, 0.0, 0.0]
#         cwf_demand = [1.0, 0.0, 1.0, 0.0, 0.0]        
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][2, :5] == cwf_vector))   
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][2, 5:10] == cwf_demand))
#         self.assertTrue(np.all(np.round(self.sys_test.system_matrix[2][2, 10:15], 10) == cwf_supply))
#         bts_2_vector = [3, 3, 0.4, 0.0, 4]
#         bts_2_supply = [0.0, 0.0, 0.0, 0.0, 0.0]
#         bts_2_demand = [0.0, 0.0, 0.0, 0.0, 0.0]
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][3, :5] == bts_2_vector))   
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][3, 5:10] == bts_2_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][3, 10:15] == bts_2_supply))
#         bsu_vector = [3, 3, 0.4, 0.6, 6]
#         bsu_supply = [0.0, 0.0, 0.0, 0.0, 0.0]
#         bsu_demand = [0.6, 0.0, 10.0, 0.0, 0.0]
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][4, :5] == bsu_vector))   
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][4, 5:10] == bsu_demand))
#         self.assertTrue(np.all(self.sys_test.system_matrix[2][4, 10:15] == bsu_supply))       
# =============================================================================

