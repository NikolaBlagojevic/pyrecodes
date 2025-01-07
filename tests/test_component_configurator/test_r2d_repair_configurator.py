import pytest
import copy
import math
from pyrecodes.component_configurator.r2d_repair_configurator import R2DRepairConfigurator, R2DBuildingRepairConfigurator, R2DRoadwayRepairConfigurator, R2DPipeRepairConfigurator, R2DBridgeRepairConfigurator, R2DTunnelRepairConfigurator
from pyrecodes.component_configurator.component_configurator import ComponentConfigurator
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.utilities import read_json_file
from pyrecodes import main
from test_component_configurator_inputs import MAIN_FILE, SYSTEM_LEVEL_DATA_DICT, R2D_COMPONENT_DAMAGE_DATA, R2D_COMPONENT_DATA
from pyrecodes.constants import METER_TO_MILE, FEET_TO_MILE, INCH_TO_MILE

@pytest.fixture()
def component_library():
        input_dict = read_json_file(MAIN_FILE)
        return main.form_component_library(input_dict)

@pytest.fixture()
def building_component(component_library: dict) -> StandardiReCoDeSComponent:
    return copy.deepcopy(component_library['DS3_Building'])

@pytest.fixture()
def roadway_component(component_library: dict) -> StandardiReCoDeSComponent:
    return copy.deepcopy(component_library['DS1_Roadway'])

@pytest.fixture()
def pipe_component(component_library: dict) -> StandardiReCoDeSComponent:
    return copy.deepcopy(component_library['DS1_Pipe'])

@pytest.fixture()
def bridge_component(component_library: dict) -> StandardiReCoDeSComponent:
    return copy.deepcopy(component_library['DS1_Bridge'])

class TestR2DRepairConfigurator:

    @pytest.fixture()
    def repair_configurator(self, building_component) -> R2DRepairConfigurator:
        return R2DRepairConfigurator(building_component, SYSTEM_LEVEL_DATA_DICT)
    
    def test_set_repair_demand(self, repair_configurator: R2DRepairConfigurator):
        # To be tested in subclasses, since get_repair_demand is not implemented in R2DRepairConfigurator
        pass

    def test_set_repair_time(self, repair_configurator: R2DRepairConfigurator):
        repair_configurator.set_repair_time(R2D_COMPONENT_DATA)
        assert repair_configurator.component.recovery_model.recovery_activities['Repair'].duration == R2D_COMPONENT_DATA['Loss']['Repair']['Time']['LF.IND2-LF.W1.MC']

    def test_get_repair_time(self, repair_configurator: R2DRepairConfigurator):
        component_data_no_repair_time = {'Loss': {}}
        assert repair_configurator.get_repair_time(component_data_no_repair_time) == None
        assert repair_configurator.get_repair_time(R2D_COMPONENT_DAMAGE_DATA) == 30.0

    def test_get_repair_cost(self, repair_configurator: R2DRepairConfigurator):
        assert repair_configurator.get_repair_cost(R2D_COMPONENT_DATA) == R2D_COMPONENT_DATA['Loss']['Repair']['Cost']['LF.IND2-LF.W1.MC'] * R2D_COMPONENT_DATA['Information']['GeneralInformation']['ReplacementCost']

    def test_get_repair_cost_no_cost(self, repair_configurator: R2DRepairConfigurator):
        component_data_no_repair_cost = {'Loss': {}}
        assert repair_configurator.get_repair_cost(component_data_no_repair_cost) == None

class TestR2DBuildingRepairConfigurator:

    @pytest.fixture()
    def repair_configurator(self, building_component) -> R2DRepairConfigurator:
        return R2DBuildingRepairConfigurator(building_component, SYSTEM_LEVEL_DATA_DICT)
    
    def test_get_repair_demand(self, repair_configurator, building_component):
        building_component.area = 10000
        component_damage_state = 0
        assert repair_configurator.get_repair_demand(component_damage_state) == 0

        component_damage_state = 2
        assert repair_configurator.get_repair_demand(component_damage_state) == 5

        component_damage_state = 3
        assert repair_configurator.get_repair_demand(component_damage_state) == 10

        building_component.area = 10000000
        assert repair_configurator.get_repair_demand(component_damage_state) == 100

    def test_set_repair_demand(self, repair_configurator: R2DRepairConfigurator):
        component_damage_state = 0
        repair_configurator.component.area = 10000
        repair_configurator.set_repair_demand(component_damage_state, ComponentConfigurator.set_component_recovery_demand)
        assert repair_configurator.component.recovery_model.recovery_activities['Repair'].demand['RepairCrew_Buildings'].current_amount == 0
        assert repair_configurator.component.recovery_model.recovery_activities['Repair'].demand['RepairCrew_Buildings'].initial_amount == 0

        component_damage_state = 2
        repair_configurator.set_repair_demand(component_damage_state, ComponentConfigurator.set_component_recovery_demand)
        assert repair_configurator.component.recovery_model.recovery_activities['Repair'].demand['RepairCrew_Buildings'].current_amount == 5
        assert repair_configurator.component.recovery_model.recovery_activities['Repair'].demand['RepairCrew_Buildings'].initial_amount == 5

        component_damage_state = 4
        repair_configurator.set_repair_demand(component_damage_state, ComponentConfigurator.set_component_recovery_demand)
        assert repair_configurator.component.recovery_model.recovery_activities['Repair'].demand['RepairCrew_Buildings'].current_amount == 10
        assert repair_configurator.component.recovery_model.recovery_activities['Repair'].demand['RepairCrew_Buildings'].initial_amount == 10

        repair_configurator.component.area = 10000000
        repair_configurator.set_repair_demand(component_damage_state, ComponentConfigurator.set_component_recovery_demand)
        assert repair_configurator.component.recovery_model.recovery_activities['Repair'].demand['RepairCrew_Buildings'].current_amount == 100
        assert repair_configurator.component.recovery_model.recovery_activities['Repair'].demand['RepairCrew_Buildings'].initial_amount == 100

class TestR2DRoadwayRepairConfigurator:

    @pytest.fixture()
    def repair_configurator(self, roadway_component) -> R2DRepairConfigurator:
        return R2DRoadwayRepairConfigurator(roadway_component, SYSTEM_LEVEL_DATA_DICT)
    
    def test_get_repair_demand(self, repair_configurator, roadway_component):
        roadway_component.length = 1000
        component_damage_state = 0
        assert repair_configurator.get_repair_demand(component_damage_state) == 0

        component_damage_state = 2
        assert repair_configurator.get_repair_demand(component_damage_state) == math.ceil(roadway_component.length/METER_TO_MILE * SYSTEM_LEVEL_DATA_DICT['REPAIR_CREW_DEMAND_PER_MILE_ROADWAY'])

class TestR2DPipeRepairConfigurator:

    @pytest.fixture()
    def repair_configurator(self, pipe_component) -> R2DRepairConfigurator:
        return R2DPipeRepairConfigurator(pipe_component, SYSTEM_LEVEL_DATA_DICT)
    
    def test_get_repair_demand(self, repair_configurator, pipe_component):
        pipe_component.length = 1000
        component_damage_state = 0
        assert repair_configurator.get_repair_demand(component_damage_state) == 0

        component_damage_state = 3
        assert repair_configurator.get_repair_demand(component_damage_state) == math.ceil(pipe_component.length/METER_TO_MILE * SYSTEM_LEVEL_DATA_DICT['REPAIR_CREW_DEMAND_PER_MILE_PIPE'])

class TestR2DBridgeRepairConfigurator:
    
    @pytest.fixture()
    def repair_configurator(self, bridge_component) -> R2DRepairConfigurator:
        return R2DBridgeRepairConfigurator(bridge_component, SYSTEM_LEVEL_DATA_DICT)
    
    def test_get_repair_demand(self, repair_configurator, bridge_component):
        bridge_component.max_span_length = 1000
        bridge_component.num_spans = 2

        component_damage_state = 0
        assert repair_configurator.get_repair_demand(component_damage_state) == 0

        component_damage_state = 3
        assert repair_configurator.get_repair_demand(component_damage_state) == math.ceil(bridge_component.max_span_length*bridge_component.num_spans/INCH_TO_MILE * SYSTEM_LEVEL_DATA_DICT['REPAIR_CREW_DEMAND_PER_MILE_BRIDGE'])

class TestR2DTunnelRepairConfigurator:

    @pytest.fixture()
    def repair_configurator(self, building_component) -> R2DRepairConfigurator:
        return R2DTunnelRepairConfigurator(building_component, SYSTEM_LEVEL_DATA_DICT)
    
    def test_get_repair_demand(self, repair_configurator, building_component):
        building_component.length = 1000
        component_damage_state = 0
        assert repair_configurator.get_repair_demand(component_damage_state) == 0

        component_damage_state = 3
        assert repair_configurator.get_repair_demand(component_damage_state) == math.ceil(building_component.length/FEET_TO_MILE * SYSTEM_LEVEL_DATA_DICT['REPAIR_CREW_DEMAND_PER_MILE_TUNNEL'])


    