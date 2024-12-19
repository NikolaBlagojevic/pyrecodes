import pytest
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.resilience_calculator.r2d_component_recovery_time_calculator import R2DComponentRecoveryTimeCalculator

MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main.json'

PARAMETERS = {} 

class TestR2DComponentRecoveryTimeCalculator():    

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(MAIN_FILE)
        return main.create_system(input_dict)

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
                                                                  {'DS1_Building | AIM ID: 1': 30},
                                                                  {'SuperLink | AIM ID: None': 0},
                                                                  {'SuperLink | AIM ID: None': 0}
                                                                ]   