import pytest
from pyrecodes.resilience_calculator.r2d_component_recovery_time_calculator import R2DComponentRecoveryTimeCalculator
from tests.conftest import make_system

PARAMETERS = {}

class TestR2DComponentRecoveryTimeCalculator():

    @pytest.fixture
    def system(self, three_localities_rewet_system_template):
        return make_system(three_localities_rewet_system_template)

    @pytest.fixture()
    def resilience_calculator(self) -> R2DComponentRecoveryTimeCalculator:
        return R2DComponentRecoveryTimeCalculator(PARAMETERS)
    
    def test_calculate_resilience(self, resilience_calculator, system):
        system.start_resilience_assessment()
        resilience_calculator.update(system)
        resilience_calculator.calculate_resilience()
        assert resilience_calculator.component_recovery_times == [{'ElectricPowerPlant | AIM ID: None': 0}, 
                                                                  {'DS0_Pipe | AIM ID: 1': 0},
                                                                  {'BaseTransceiverStation_1 | AIM ID: None': 0}, 
                                                                  {'SuperLink | AIM ID: None': 0},
                                                                  {'SuperLink | AIM ID: None': 0},
                                                                  {'CoolingWaterFacility | AIM ID: None': 0},
                                                                  {'DS0_Pipe | AIM ID: 2': 0},
                                                                  {'SuperLink | AIM ID: None': 0},
                                                                  {'SuperLink | AIM ID: None': 0},
                                                                  {'BaseTransceiverStation_2 | AIM ID: None': 0},
                                                                  {'DS0_Pipe | AIM ID: 3': 0},
                                                                  {'DS2_Pipe | AIM ID: 4': 21},                                                                  
                                                                  {'DS1_Building | AIM ID: 1': 10},
                                                                  {'SuperLink | AIM ID: None': 0},
                                                                  {'SuperLink | AIM ID: None': 0}
                                                                ]   