import pytest
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.resilience_calculator.component_recovery_time_calculator import ComponentRecoveryTimeCalculator

MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

PARAMETERS = {} 

class TestComponentRecoveryTimeCalculator():    

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(MAIN_FILE)
        return main.create_system(input_dict)

    @pytest.fixture()
    def resilience_calculator(self) -> ComponentRecoveryTimeCalculator:
        return ComponentRecoveryTimeCalculator(PARAMETERS)
    
    def test_init_(self, resilience_calculator):
        assert resilience_calculator.parameters == PARAMETERS
        
    def test_get_component_recovery_time(self, system, resilience_calculator):
        system.start_resilience_assessment()
        resilience_calculator.update(system)
        assert resilience_calculator.get_component_recovery_time(system.components[0]) == 0
        assert resilience_calculator.get_component_recovery_time(system.components[1]) == 10
        assert resilience_calculator.get_component_recovery_time(system.components[2]) == 0

    def test_calculate_resilience(self, system, resilience_calculator):
        system.start_resilience_assessment()
        resilience_calculator.update(system)
        resilience_calculator.calculate_resilience()
        assert resilience_calculator.component_recovery_times == [{'ElectricPowerPlant | ID: 0': 0}, 
                                                                  {'BaseTransceiverStation_1 | ID: 1': 10}, 
                                                                  {'SuperLink | ID: 2': 0},
                                                                  {'SuperLink | ID: 3': 0},
                                                                  {'CoolingWaterFacility | ID: 4': 10},
                                                                  {'SuperLink | ID: 5': 0},
                                                                  {'SuperLink | ID: 6': 0},
                                                                  {'BaseTransceiverStation_2 | ID: 7': 10},
                                                                  {'BuildingStockUnit | ID: 8': 10},
                                                                    {'SuperLink | ID: 9': 0},
                                                                    {'SuperLink | ID: 10': 0}
                                                                  ]