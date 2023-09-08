import pytest
import math
from pyrecodes import main
from pyrecodes import ResilienceCalculator
from pyrecodes import System

class TestReCoDeSResilienceCalculator():

    MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

    @pytest.fixture
    def system(self):
        input_dict = main.read_file(self.MAIN_FILE)
        return main.create_system(input_dict)

    @pytest.fixture()
    def resilience_calculator(self, system: System.System) -> ResilienceCalculator.ResilienceCalculator:
        return ResilienceCalculator.ReCoDeSResilienceCalculator(system.system_configuration['ResilienceCalculator'][0]['Parameters'])

    def test_init_(self, system: System.System, resilience_calculator):
        resource_names = ['ElectricPower', 'CoolingWater', 'Communication']
        assert resilience_calculator.resource_names == resource_names

    def test_update_no_damage(self, system: System.System,
                              resilience_calculator: ResilienceCalculator.ResilienceCalculator):
        system.distribute_resources()
        resilience_calculator.update(system.resources)
        target_values = [[5.0, 4.0, 4.0], [3.0, 1.0, 1.0], [3.0, 3.0, 3.0]]
        for target_value, resource_name in zip(target_values, resilience_calculator.resource_names):
            assert math.isclose(target_value[0], resilience_calculator.system_supply[resource_name][0])
            assert math.isclose(target_value[1], resilience_calculator.system_demand[resource_name][0])
            assert math.isclose(target_value[2], resilience_calculator.system_consumption[resource_name][0])

    def test_update_with_damage(self, system: System.System,
                                resilience_calculator: ResilienceCalculator.ResilienceCalculator):
        system.set_initial_damage()
        system.time_step = 1
        system.update()
        system.resources['ElectricPower']['DistributionModel'].distribute()
        system.resources['CoolingWater']['DistributionModel'].distribute()
        system.resources['Communication']['DistributionModel'].distribute()
        resilience_calculator.update(system.resources)
        target_values = [[3.0, 2.6, 2.6], [1.8, 1.0, 1.0], [1.0, 12.0, 1.0]]
        for target_value, resource_name in zip(target_values, resilience_calculator.resource_names):
            assert math.isclose(target_value[0], resilience_calculator.system_supply[resource_name][0])
            print(resilience_calculator.system_supply[resource_name])
            assert math.isclose(target_value[1], resilience_calculator.system_demand[resource_name][0])
            assert math.isclose(target_value[2], resilience_calculator.system_consumption[resource_name][0])

    def test_update_with_damage_and_interdependency(self, system: System.System,
                                                    resilience_calculator: ResilienceCalculator.ResilienceCalculator):
        system.set_initial_damage()
        system.time_step = 1
        system.update()
        system.distribute_resources()
        resilience_calculator.update(system.resources)
        target_values = [[0.0, 2.6, 0.0], [0.0, 1.0, 0.0], [0.0, 12.0, 0.0]]
        for target_value, resource_name in zip(target_values, resilience_calculator.resource_names):
            assert math.isclose(target_value[0], resilience_calculator.system_supply[resource_name][0])
            assert math.isclose(target_value[1], resilience_calculator.system_demand[resource_name][0])
            assert math.isclose(target_value[2], resilience_calculator.system_consumption[resource_name][0])

    def test_calculate_resilience(self, system: System.System,
                                  resilience_calculator: ResilienceCalculator.ResilienceCalculator):
        system.set_initial_damage()
        system.time_step = 1
        system.update()
        system.distribute_resources()
        resilience_calculator.update(system.resources)
        lack_of_resilience = resilience_calculator.calculate_resilience()
        target_values = [2.6, 1.0, 12.0]
        for target_value, resource_name in zip(target_values, resilience_calculator.resource_names):
            assert math.isclose(lack_of_resilience[resource_name], target_value)

class TestNISTGoalsResilienceCalculator:

    MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

    @pytest.fixture
    def system(self):
        input_dict = main.read_file(self.MAIN_FILE)
        return main.create_system(input_dict)

    @pytest.fixture()
    def resilience_calculator(self, system: System.System) -> ResilienceCalculator.ResilienceCalculator:
        return ResilienceCalculator.NISTGoalsResilienceCalculator(system.system_configuration['ResilienceCalculator'][1]['Parameters'])
    
    def test_init_(self, resilience_calculator):
        assert len(resilience_calculator.resilience_goals) == 3

    def test_update(self, system, resilience_calculator):
        system.distribute_resources()
        resilience_calculator.update(system.resources)
        assert resilience_calculator.resilience_goals[0]['GoalMet'][0] == True
        assert resilience_calculator.resilience_goals[1]['GoalMet'][0] == True
        assert resilience_calculator.resilience_goals[2]['GoalMet'][0] == True

        system.set_initial_damage()
        system.time_step = 1
        system.update()
        system.distribute_resources()
        resilience_calculator.update(system.resources)
        assert resilience_calculator.resilience_goals[0]['GoalMet'][1] == False
        assert resilience_calculator.resilience_goals[1]['GoalMet'][1] == False
        assert resilience_calculator.resilience_goals[2]['GoalMet'][1] == False

        for time_step in range(1, 12):
            system.time_step = time_step
            system.recover()
            system.update()
            system.distribute_resources()
            resilience_calculator.update(system.resources)
        assert resilience_calculator.resilience_goals[0]['GoalMet'][-1] == True
        assert resilience_calculator.resilience_goals[1]['GoalMet'][-1] == True
        assert resilience_calculator.resilience_goals[2]['GoalMet'][-1] == True
    
    def test_calculate_resilience(self, system, resilience_calculator):
        system.start_resilience_assessment()
        system.calculate_resilience()
        assert system.resilience_calculators[1].resilience_goals[0]['MetAtTimeStep'] == [12]
        assert system.resilience_calculators[1].resilience_goals[1]['MetAtTimeStep'] == [12]
        assert system.resilience_calculators[1].resilience_goals[2]['MetAtTimeStep'] == [12]
