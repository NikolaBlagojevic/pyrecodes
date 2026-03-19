import pytest
from pyrecodes.resilience_calculator.full_recovery_time_calculator import FullRecoveryTimeCalculator
from tests.conftest import make_system

PARAMETERS = {}

class TestReCoDeSCalculator():

    @pytest.fixture
    def system(self, three_localities_system_template):
        return make_system(three_localities_system_template)

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


