import pytest
import copy
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.component_configurator.repair_configurator import RepairConfigurator
from pyrecodes.component_configurator.component_configurator import ComponentConfigurator
from test_component_configurator_inputs import MAIN_FILE, SYSTEM_LEVEL_DATA_DICT, R2D_COMPONENT_DAMAGE_DATA

COMPONENT_FINANCING_DATA = {'RecoveryModel': {'Parameters': {'Financing': {'Duration': {'Lognormal': {'Median': 1, 'Dispersion': 0.0}}, 'Demand': [{'Resource': 'Money', 'Amount': 0.1}], 'PrecedingActivities': []}}}}

@pytest.fixture()
def component_library():
        input_dict = read_json_file(MAIN_FILE)
        return main.form_component_library(input_dict)

@pytest.fixture()
def building_component(component_library: dict) -> StandardiReCoDeSComponent:
    return copy.deepcopy(component_library['DS3_Building'])

class TestRepairConfigurator:

    @pytest.fixture
    def repair_configurator(self, building_component: StandardiReCoDeSComponent):
        return RepairConfigurator(building_component, SYSTEM_LEVEL_DATA_DICT)
     
    def test_init(self, repair_configurator):
        assert repair_configurator.component.name == 'DS3_Building'
        assert repair_configurator.system_level_data == SYSTEM_LEVEL_DATA_DICT

    def test_get_repair_cost(self, repair_configurator):
        assert repair_configurator.get_repair_cost(COMPONENT_FINANCING_DATA) == 0.1

    def test_set_repair_cost(self, repair_configurator):
        repair_configurator.set_repair_cost(COMPONENT_FINANCING_DATA, ComponentConfigurator.set_component_recovery_demand)
        assert repair_configurator.get_repair_cost(COMPONENT_FINANCING_DATA) == 0.1
    
        