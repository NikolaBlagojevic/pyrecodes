import pytest
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.resilience_calculator.full_recovery_time_calculator import FullRecoveryTimeCalculator

FOLDER_NAME = './tests/test_inputs'
MAIN_FILE = 'test_inputs_ThreeLocalitiesCommunity_Main.json'

PARAMETERS = {} 

class TestReCoDeSCalculator():    

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(f'{FOLDER_NAME}/{MAIN_FILE}')
        return main.create_system(FOLDER_NAME, input_dict)

    @pytest.fixture()
    def resilience_calculator(self) -> FullRecoveryTimeCalculator:
        return FullRecoveryTimeCalculator()
    
    def test_update(self, resilience_calculator, system):
        system.MAX_TIME_STEP = 1
        system.start_resilience_assessment()
        resilience_calculator.update(system)
        assert resilience_calculator.current_recovery_time == None

        system.MAX_TIME_STEP = 2
        system.start_resilience_assessment()
        resilience_calculator.update(system)
        assert resilience_calculator.current_recovery_time == None

        system.MAX_TIME_STEP = 11
        system.start_resilience_assessment()
        resilience_calculator.update(system)
        assert resilience_calculator.current_recovery_time == None

        system.MAX_TIME_STEP = 13
        system.start_resilience_assessment()
        resilience_calculator.update(system)
        assert resilience_calculator.current_recovery_time == 12

        system.MAX_TIME_STEP = 20
        system.start_resilience_assessment()
        resilience_calculator.update(system)
        assert resilience_calculator.current_recovery_time == 12


