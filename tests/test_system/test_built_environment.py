import pytest
import numpy as np
import math
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.system_creator.concrete_system_creator import ConcreteSystemCreator
from pyrecodes.system_creator.system_creator import SystemCreator
from pyrecodes.damage_input.list_damage_input import ListDamageInput
from pyrecodes.system.recovery_target_checker import NoDamageRecoveryTargetChecker
from pyrecodes.system.system import System
   

class TestBuiltEnvironmentSystem():

    MAIN_FILE = ''

    @pytest.fixture()
    def system_creator(self):
        return ConcreteSystemCreator()

    @pytest.fixture()
    def system(self):
        input_dict = read_json_file(self.MAIN_FILE)
        system = main.create_system(input_dict)
        system.time_step = 0
        return system

class TestThreeLocalitiesSystem(TestBuiltEnvironmentSystem):

    MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

    def test_init(self, system):
        assert isinstance(system.system_configuration, dict)
        assert isinstance(system.component_library, dict)
        assert isinstance(system.system_creator, SystemCreator)
    
    def test_create_system(self, system):
        assert len(system.components) == 11 # number of components in the ThreeLocalitiesCommunity 
        assert len(system.resources) == 4 # number of resources in the ThreeLocalitiesCommunity
        assert len(system.resilience_calculators) == 2 # number of resilience calculators in the ThreeLocalitiesCommunity
        assert isinstance(system.recovery_target_checker, NoDamageRecoveryTargetChecker)
        assert isinstance(system.resource_distribution_dict, dict)
        assert isinstance(system.damage_input, ListDamageInput)
        assert system.START_TIME_STEP == 0
        assert system.MAX_TIME_STEP == 500
        assert system.DISASTER_TIME_STEP == 1
    
    def test_start_resilience_assessment(self, system):
        system.start_resilience_assessment()
        assert system.FINISH == True
    
    def test_set_initial_damage(self, system):
        target_damage_levels = [0.0, 0.4, 0.0, 0.0, 0.4, 0.0, 0.0, 0.4, 0.4, 0.0, 0.0]
        system.set_initial_damage()
        bool_list = []
        for target_damage_level, component in zip(target_damage_levels, system.components):
            bool_list.append(component.get_damage_level() == target_damage_level)
        assert all(bool_list)
    
    def test_update(self, system):
        for component in system.components:
            assert component.functionality_level == 1

        system.time_step = system.DISASTER_TIME_STEP
        system.set_initial_damage()
        system.update()
        target_functionality_levels = [1.0, 0.0, 1.0, 1.0, 0.6, 1.0, 1.0, 0.0, 0.6, 1.0, 1.0]
        for target_functionality_level, component in zip(target_functionality_levels, system.components):
            assert component.functionality_level == target_functionality_level

    def test_distribute_resources(self, system):
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
    
    def test_get_supply_of_interdependent_resources(self, system):
        target_supply = {'ElectricPower': 5, 'Communication': 3, 'CoolingWater': 3}
        system.distribute_resources()
        supply = system.get_supply_of_interdependent_resources()
        assert supply == target_supply
    
    def test_check_system_convergence(self, system):
        system.distribute_resources()
        supply = system.get_supply_of_interdependent_resources()
        assert system.check_system_convergence(supply, supply) == True

        system.time_step = system.DISASTER_TIME_STEP
        system.set_initial_damage()
        system.update()
        system.distribute_resources()
        damaged_supply = system.get_supply_of_interdependent_resources()
        assert system.check_system_convergence(supply, damaged_supply) == False

    def test_recover(self, system):
        system.time_step = system.DISASTER_TIME_STEP
        system.set_initial_damage()
        system.recover()
        target_damage_levels = [0.0, 0.36, 0.0, 0.0, 0.36, 0.0, 0.0, 0.36, 0.36, 0.0, 0.0]        
        for target_damage_level, component in zip(target_damage_levels, system.components):
            assert component.get_damage_level() == target_damage_level

    def test_save_and_load_as_pickle(self, system):
        system.save_as_pickle('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunitySystem.pickle')
        system_loaded = system.load_as_pickle('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunitySystem.pickle')
        assert isinstance(system_loaded, System)
        
class TestVirtualCommunity(TestBuiltEnvironmentSystem):

    MAIN_FILE = './tests/test_inputs/test_inputs_VirtualCommunity_Main.json'

    def test_distribute_interdependent_resources(self, system):
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

