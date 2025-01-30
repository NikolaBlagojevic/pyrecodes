import pytest
import math
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.resilience_calculator.resilience_calculator import ResilienceCalculator
from pyrecodes.resilience_calculator.recodes_calculator import ReCoDeSCalculator
from pyrecodes.system.system import System

MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

PARAMETERS = {"Scope": "All", 
            "Resources": ["ElectricPower", "CoolingWater", "Communication"]} 

class TestReCoDeSCalculator():    

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(MAIN_FILE)
        return main.create_system(input_dict)

    @pytest.fixture()
    def resilience_calculator(self) -> ResilienceCalculator:
        return ReCoDeSCalculator(PARAMETERS)

    def test_init_(self, resilience_calculator):
        assert resilience_calculator.resource_names == PARAMETERS["Resources"]
        assert resilience_calculator.scope == PARAMETERS["Scope"]
        assert resilience_calculator.system_supply == {key: [] for key in PARAMETERS["Resources"]}
        assert resilience_calculator.system_demand == {key: [] for key in PARAMETERS["Resources"]}
        assert resilience_calculator.system_consumption == {key: [] for key in PARAMETERS["Resources"]}

    def test_update_no_damage(self, system: System,
                              resilience_calculator: ResilienceCalculator):
        system.time_step = 0
        system.distribute_resources()
        resilience_calculator.update(system)
        target_values = [[5.0, 4.0, 4.0], [3.0, 1.0, 1.0], [3.0, 3.0, 3.0]]
        for target_value, resource_name in zip(target_values, resilience_calculator.resource_names):
            assert math.isclose(target_value[0], resilience_calculator.system_supply[resource_name][0])
            assert math.isclose(target_value[1], resilience_calculator.system_demand[resource_name][0])
            assert math.isclose(target_value[2], resilience_calculator.system_consumption[resource_name][0])

    def test_update_with_damage(self, system: System,
                                resilience_calculator: ResilienceCalculator):
        system.time_step = 1
        system.set_initial_damage() 
        system.update()
        system.resources['ElectricPower']['DistributionModel'].distribute(system.time_step)
        system.resources['CoolingWater']['DistributionModel'].distribute(system.time_step)
        system.resources['Communication']['DistributionModel'].distribute(system.time_step)
        resilience_calculator.update(system)
        target_values = [[5.0, 1.6, 1.6], [1.8, 1.0, 1.0], [0.0, 12.0, 0.0]]
        for target_value, resource_name in zip(target_values, resilience_calculator.resource_names):
            assert math.isclose(target_value[0], resilience_calculator.system_supply[resource_name][0])
            print(resilience_calculator.system_supply[resource_name])
            assert math.isclose(target_value[1], resilience_calculator.system_demand[resource_name][0])
            assert math.isclose(target_value[2], resilience_calculator.system_consumption[resource_name][0])

    def test_update_with_damage_and_interdependency(self, system: System,
                                                    resilience_calculator: ResilienceCalculator):
        system.set_initial_damage()
        system.time_step = 1
        system.update()
        system.distribute_resources()
        resilience_calculator.update(system)
        target_values = [[0.0, 1.6, 0.0], [0.0, 1.0, 0.0], [0.0, 12.0, 0.0]]
        for target_value, resource_name in zip(target_values, resilience_calculator.resource_names):
            assert math.isclose(target_value[0], resilience_calculator.system_supply[resource_name][0])
            assert math.isclose(target_value[1], resilience_calculator.system_demand[resource_name][0])
            assert math.isclose(target_value[2], resilience_calculator.system_consumption[resource_name][0])

    def test_update_with_damaged_links(self, system: System,
                                                    resilience_calculator: ResilienceCalculator):
        # Assign damage to links going from Locality 1 to Localities 2 and 3.
        system.damage_input.damage_levels[2] = 1.0
        system.damage_input.damage_levels[3] = 1.0
        system.set_initial_damage()
        system.time_step = 1
        system.update()
        system.resources['ElectricPower']['DistributionModel'].distribute(system.time_step)
        system.resources['CoolingWater']['DistributionModel'].distribute(system.time_step)
        system.resources['Communication']['DistributionModel'].distribute(system.time_step)
        resilience_calculator.update(system)
        target_values = [[5.0, 1.6, 0.0], [0.0, 1.0, 0.0], [0.0, 12.0, 0.0]]
        for target_value, resource_name in zip(target_values, resilience_calculator.resource_names):
            assert math.isclose(target_value[0], resilience_calculator.system_supply[resource_name][0])
            assert math.isclose(target_value[1], resilience_calculator.system_demand[resource_name][0])
            assert math.isclose(target_value[2], resilience_calculator.system_consumption[resource_name][0])

    def test_calculate_resilience_single_time_step(self, system: System,
                                  resilience_calculator: ResilienceCalculator):
        system.set_initial_damage()
        system.time_step = 1
        system.update()
        system.distribute_resources()
        resilience_calculator.update(system)
        lack_of_resilience = resilience_calculator.calculate_resilience()
        target_values = [1.6, 1.0, 12.0]
        for target_value, resource_name in zip(target_values, resilience_calculator.resource_names):
            assert math.isclose(lack_of_resilience[resource_name], target_value)

    def test_calculate_resilience_multiple_time_steps(self, system: System,
                                  resilience_calculator: ResilienceCalculator):
        system.set_initial_damage()
        for time_step in range(1, 4):
            system.time_step = time_step
            system.update()
            system.distribute_resources()
            resilience_calculator.update(system)
        lack_of_resilience = resilience_calculator.calculate_resilience()
        target_values = [1.6*3, 1.0*3, 12.0+9.408+7.488]
        for target_value, resource_name in zip(target_values, resilience_calculator.resource_names):
            assert math.isclose(lack_of_resilience[resource_name], target_value, rel_tol=1e-3)
