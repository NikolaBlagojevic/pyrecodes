import pytest
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.system.recovery_target_checker import NoDamageRecoveryTargetChecker

MAIN_FILE = './tests/test_inputs/test_inputs_VirtualCommunity_Main.json'

class TestNoDamageRecoveryTargetChecker:

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(MAIN_FILE)
        return main.create_system(input_dict)
    
    def test_recovery_target_met(self, system):
        system.time_step = system.START_TIME_STEP
        recovery_target_checker = NoDamageRecoveryTargetChecker()
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