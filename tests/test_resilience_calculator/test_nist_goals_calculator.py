import pytest
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.resilience_calculator.resilience_calculator import ResilienceCalculator
from pyrecodes.resilience_calculator.nist_goals_calculator import NISTGoalsCalculator
from pyrecodes.system.system import System

MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

PARAMETERS = [{"Resource": "ElectricPower", "DesiredFunctionalityLevel": 0.95, "Scope": "All"},
                        {"Resource": "CoolingWater", "DesiredFunctionalityLevel": 0.9, "Scope": "All"},
                        {"Resource": "Communication", "DesiredFunctionalityLevel": 0.8, "Scope": "All"}]

class TestNISTGoalsResilienceCalculator:    

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(MAIN_FILE)
        return main.create_system(input_dict)

    @pytest.fixture()
    def resilience_calculator(self) -> ResilienceCalculator:
        return NISTGoalsCalculator(PARAMETERS)
    
    def test_init_(self, resilience_calculator):
        assert len(resilience_calculator.resilience_goals) == 3

    def test_update(self, system, resilience_calculator):
        system.time_step = 0
        system.distribute_resources()
        resilience_calculator.update(system)
        assert resilience_calculator.resilience_goals[0]['GoalMet'][0] == True
        assert resilience_calculator.resilience_goals[1]['GoalMet'][0] == True
        assert resilience_calculator.resilience_goals[2]['GoalMet'][0] == True

        system.set_initial_damage()
        system.time_step = 1
        system.update()
        system.distribute_resources()
        resilience_calculator.update(system)
        assert resilience_calculator.resilience_goals[0]['GoalMet'][1] == False
        assert resilience_calculator.resilience_goals[1]['GoalMet'][1] == False
        assert resilience_calculator.resilience_goals[2]['GoalMet'][1] == False

        for time_step in range(1, 12):
            system.time_step = time_step
            system.recover()
            system.update()
            system.distribute_resources()
            resilience_calculator.update(system)
        assert resilience_calculator.resilience_goals[0]['GoalMet'][-1] == True
        assert resilience_calculator.resilience_goals[1]['GoalMet'][-1] == True
        assert resilience_calculator.resilience_goals[2]['GoalMet'][-1] == True
    
    def test_calculate_resilience(self, system):
        system.start_resilience_assessment()
        system.calculate_resilience()
        assert system.resilience_calculators[1].resilience_goals[0]['MetAtTimeStep'] == [12]
        assert system.resilience_calculators[1].resilience_goals[1]['MetAtTimeStep'] == [12]
        assert system.resilience_calculators[1].resilience_goals[2]['MetAtTimeStep'] == [12]
