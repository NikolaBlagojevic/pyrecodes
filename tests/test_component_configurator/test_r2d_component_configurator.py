import pytest
import math
import copy
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.utilities import format_locality_id
from pyrecodes.component_library_creator.json_component_library_creator import JSONComponentLibraryCreator
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.component_configurator.r2d_component_configurator import R2DComponentConfigurator, R2DBuildingConfigurator, R2DRoadwayConfigurator, R2DPipeConfigurator
from pyrecodes.component_configurator.r2d_repair_configurator import R2DBuildingRepairConfigurator, R2DRoadwayRepairConfigurator, R2DPipeRepairConfigurator
from pyrecodes.component_configurator.component_configurator import ComponentConfigurator
from pyrecodes.component_configurator.r2d_dict_getter import R2DDictGetter, R2DPipeDictGetter
from test_component_configurator_inputs import MAIN_FILE, SYSTEM_LEVEL_DATA_DICT, RECOVERY_TIME_STEPPING_RULE, R2D_COMPONENT_DATA, LOCALITY_STRING, DAMAGE_STATE, R2D_COMPONENT_DAMAGE_DATA, R2D_ROADWAY_DATA, R2D_PIPE_DATA

@pytest.fixture()
def component_library():
        input_dict = read_json_file(MAIN_FILE)
        return main.form_component_library(input_dict)

@pytest.fixture()
def system_configuration() -> dict:
    input_dict = read_json_file(MAIN_FILE)
    system_configuration = read_json_file(input_dict['System']['SystemConfigurationFile'])
    return system_configuration

@pytest.fixture()
def building_component(component_library: dict) -> StandardiReCoDeSComponent:
    return copy.deepcopy(component_library['DS3_Building'])

@pytest.fixture()
def roadway_component(component_library: dict) -> StandardiReCoDeSComponent:
    return copy.deepcopy(component_library['DS1_Roadway'])

@pytest.fixture()
def pipe_component(component_library: dict) -> StandardiReCoDeSComponent:
    return copy.deepcopy(component_library['DS1_Pipe'])

class TestR2DComponentConfigurator:

    @pytest.fixture()
    def component_configurator(self) -> ComponentConfigurator:
        return R2DComponentConfigurator(SYSTEM_LEVEL_DATA_DICT, RECOVERY_TIME_STEPPING_RULE)
    
    def test_set_general_information(self, building_component, component_configurator):
        component_configurator.set_general_information(building_component, R2D_COMPONENT_DATA)
        assert building_component.general_information == R2D_COMPONENT_DATA['Information']['GeneralInformation']

    def test_set_asset_ids(self, building_component, component_configurator):
        component_configurator.set_asset_ids(building_component, R2D_COMPONENT_DATA)
        assert building_component.asset_type == 'Building'
        assert building_component.asset_subtype == 'Building'
        assert building_component.aim_id == R2D_COMPONENT_DATA['Information']['GeneralInformation']['AIM_id']
        assert building_component.r2d_comp == True

    def test_set_r2d_dict_getter(self, building_component, component_configurator):
        component_configurator.set_r2d_dict_getter(building_component)
        assert isinstance(building_component.r2d_dict_getter, R2DDictGetter)

    def test_get_damage_state(self, component_configurator):
        assert component_configurator.get_damage_state(R2D_COMPONENT_DAMAGE_DATA) == 2
        R2D_COMPONENT_DAMAGE_DATA['Damage']['LF.W1.MC-1'] = 0
        assert component_configurator.get_damage_state(R2D_COMPONENT_DAMAGE_DATA) == 1
        R2D_COMPONENT_DAMAGE_DATA['Damage']['collapse-0'] = 10
        assert component_configurator.get_damage_state(R2D_COMPONENT_DAMAGE_DATA) == 1


class TestR2DBuildingConfigurator:       
    
    @pytest.fixture()
    def component_configurator(self) -> ComponentConfigurator:
        return R2DBuildingConfigurator(SYSTEM_LEVEL_DATA_DICT, RECOVERY_TIME_STEPPING_RULE)
    
    def test_set_parameters(self, building_component: StandardiReCoDeSComponent, 
                               component_configurator: ComponentConfigurator):
        component_configurator.set_parameters(building_component, LOCALITY_STRING, R2D_COMPONENT_DATA, DAMAGE_STATE)
        assert building_component.area == R2D_COMPONENT_DATA['Information']['GeneralInformation']['PlanArea'] * R2D_COMPONENT_DATA['Information']['GeneralInformation']['NumberOfStories']
        assert building_component.footprint == {"type": "Feature", "geometry": {"type": "Polygon", "coordinates":[[[-122.293878,37.771004],[-122.293973,37.771029],[-122.294025,37.770903],[-122.293931,37.770878],[-122.293878,37.771004]]]}, "properties":{}}
        assert building_component.num_stories == 3
        assert building_component.supply['Supply']['Shelter'].current_amount == R2D_COMPONENT_DATA['Information']['GeneralInformation']['Population']
        assert building_component.supply['Supply']['Shelter'].initial_amount == R2D_COMPONENT_DATA['Information']['GeneralInformation']['Population']
        assert building_component.demand['OperationDemand']['Shelter'].current_amount == R2D_COMPONENT_DATA['Information']['GeneralInformation']['Population']
        assert building_component.demand['OperationDemand']['Shelter'].initial_amount == R2D_COMPONENT_DATA['Information']['GeneralInformation']['Population']
        assert building_component.demand['OperationDemand']['ElectricPower'].current_amount == R2D_COMPONENT_DATA['Information']['GeneralInformation']['Population'] * SYSTEM_LEVEL_DATA_DICT['DEMAND_PER_PERSON']['ElectricPower']
        assert building_component.demand['OperationDemand']['ElectricPower'].initial_amount == R2D_COMPONENT_DATA['Information']['GeneralInformation']['Population'] * SYSTEM_LEVEL_DATA_DICT['DEMAND_PER_PERSON']['ElectricPower']
        assert building_component.demand['OperationDemand']['PotableWater'].current_amount == R2D_COMPONENT_DATA['Information']['GeneralInformation']['Population'] * SYSTEM_LEVEL_DATA_DICT['DEMAND_PER_PERSON']['PotableWater']
        assert building_component.demand['OperationDemand']['PotableWater'].initial_amount == R2D_COMPONENT_DATA['Information']['GeneralInformation']['Population'] * SYSTEM_LEVEL_DATA_DICT['DEMAND_PER_PERSON']['PotableWater']
        assert building_component.demand['OperationDemand']['CellularCommunication'].initial_amount == R2D_COMPONENT_DATA['Information']['GeneralInformation']['Population'] * SYSTEM_LEVEL_DATA_DICT['DEMAND_PER_PERSON']['CellularCommunication']
        assert building_component.demand['OperationDemand']['CellularCommunication'].current_amount == R2D_COMPONENT_DATA['Information']['GeneralInformation']['Population'] * SYSTEM_LEVEL_DATA_DICT['DEMAND_PER_PERSON']['CellularCommunication']
        assert building_component.recovery_model.recovery_activities['Repair'].demand['RepairCrew_Buildings'].current_amount == math.ceil(building_component.area/component_configurator.system_level_data['REPAIR_CREW_DEMAND_PER_SQFT'][f'DS{DAMAGE_STATE}'])
        assert building_component.recovery_model.recovery_activities['Repair'].demand['RepairCrew_Buildings'].initial_amount == math.ceil(building_component.area/component_configurator.system_level_data['REPAIR_CREW_DEMAND_PER_SQFT'][f'DS{DAMAGE_STATE}'])
        assert building_component.locality == [format_locality_id(LOCALITY_STRING[0])]

    def test_set_repair_configurator(self, building_component: StandardiReCoDeSComponent, 
                               component_configurator: ComponentConfigurator):
        component_configurator.set_repair_configurator(building_component)
        assert isinstance(component_configurator.repair_configurator, R2DBuildingRepairConfigurator)
        assert component_configurator.repair_configurator.system_level_data == SYSTEM_LEVEL_DATA_DICT

    def test_set_building_area(self, building_component: StandardiReCoDeSComponent,
                               component_configurator: ComponentConfigurator):      
        component_configurator.set_building_area(building_component, R2D_COMPONENT_DATA)
        assert building_component.area == R2D_COMPONENT_DATA['Information']['GeneralInformation']['PlanArea'] * R2D_COMPONENT_DATA['Information']['GeneralInformation']['NumberOfStories']
    
    def test_set_building_footprint(self, building_component: StandardiReCoDeSComponent, 
                               component_configurator: ComponentConfigurator):
        component_configurator.set_building_footprint(building_component, R2D_COMPONENT_DATA)
        target_building_footprint = {"type": "Feature", "geometry": {"type": "Polygon", "coordinates":[[[-122.293878,37.771004],[-122.293973,37.771029],[-122.294025,37.770903],[-122.293931,37.770878],[-122.293878,37.771004]]]}, "properties":{}}
        assert building_component.footprint == target_building_footprint

    def test_set_building_num_stories(self, building_component: StandardiReCoDeSComponent, 
                               component_configurator: ComponentConfigurator):
        component_configurator.set_building_num_stories(building_component, R2D_COMPONENT_DATA)
        assert building_component.num_stories == 3

    def test_get_total_building_area(self, component_configurator: ComponentConfigurator):
        building_area = component_configurator.get_total_building_area(R2D_COMPONENT_DATA)
        assert building_area == R2D_COMPONENT_DATA['Information']['GeneralInformation']['PlanArea'] * R2D_COMPONENT_DATA['Information']['GeneralInformation']['NumberOfStories']

    def test_get_building_housing_capacity(self, component_configurator: ComponentConfigurator):
        assert component_configurator.get_building_housing_capacity(R2D_COMPONENT_DATA) == R2D_COMPONENT_DATA['Information']['GeneralInformation']['Population']

    def test_set_supply_parameters(self, building_component: StandardiReCoDeSComponent, 
                               component_configurator: ComponentConfigurator):
        component_configurator.set_supply_parameters(building_component, R2D_COMPONENT_DATA)
        assert building_component.supply['Supply']['Shelter'].current_amount == R2D_COMPONENT_DATA['Information']['GeneralInformation']['Population']
        assert building_component.supply['Supply']['FunctionalHousing'].current_amount == R2D_COMPONENT_DATA['Information']['GeneralInformation']['Population']

    def test_set_housing_demand_parameters(self, building_component: StandardiReCoDeSComponent, 
                               component_configurator: ComponentConfigurator):
        component_configurator.set_housing_demand_parameters(building_component, R2D_COMPONENT_DATA)
        assert building_component.demand['OperationDemand']['Shelter'].current_amount == R2D_COMPONENT_DATA['Information']['GeneralInformation']['Population']
        assert building_component.demand['OperationDemand']['FunctionalHousing'].current_amount == R2D_COMPONENT_DATA['Information']['GeneralInformation']['Population']

    def test_set_infrastructure_demand_parameters(self, building_component: StandardiReCoDeSComponent, 
                               component_configurator: ComponentConfigurator):
        component_configurator.set_infrastructure_demand_parameters(building_component, R2D_COMPONENT_DATA)
        assert building_component.demand['OperationDemand']['ElectricPower'].current_amount == R2D_COMPONENT_DATA['Information']['GeneralInformation']['Population'] * SYSTEM_LEVEL_DATA_DICT['DEMAND_PER_PERSON']['ElectricPower']
        assert building_component.demand['OperationDemand']['PotableWater'].current_amount == R2D_COMPONENT_DATA['Information']['GeneralInformation']['Population'] * SYSTEM_LEVEL_DATA_DICT['DEMAND_PER_PERSON']['PotableWater']
        assert building_component.demand['OperationDemand']['CellularCommunication'].current_amount == R2D_COMPONENT_DATA['Information']['GeneralInformation']['Population'] * SYSTEM_LEVEL_DATA_DICT['DEMAND_PER_PERSON']['CellularCommunication']


class TestR2DRoadywayConfigurator:

    @pytest.fixture()
    def component_configurator(self) -> ComponentConfigurator:
        return R2DRoadwayConfigurator(SYSTEM_LEVEL_DATA_DICT, RECOVERY_TIME_STEPPING_RULE)
    
    def test_set_geometry(self, roadway_component, component_configurator):
        component_data = {}
        component_data['Information'] = R2D_ROADWAY_DATA
        component_configurator.set_geometry(roadway_component, component_data)
        assert roadway_component.geometry == R2D_ROADWAY_DATA['GeneralInformation']['geometry']
        assert math.isclose(roadway_component.length, 96.89, rel_tol=1e-2)

    def test_get_road_length(self, roadway_component, component_configurator):
        Hundred_Meter_linestring = "LINESTRING (-122.285881 37.776324, -122.285881 37.777224963751124)"
        roadway_component.geometry = Hundred_Meter_linestring
        assert math.isclose(component_configurator.get_road_length(roadway_component), 100, rel_tol=1e-2)

    def test_set_repair_configurator(self, roadway_component, component_configurator):
        component_configurator.set_repair_configurator(roadway_component)
        assert isinstance(component_configurator.repair_configurator, R2DRoadwayRepairConfigurator)
        assert component_configurator.repair_configurator.system_level_data == SYSTEM_LEVEL_DATA_DICT

class TestR2DPipeConfigurator:
    
    @pytest.fixture()
    def component_configurator(self) -> ComponentConfigurator:
        return R2DPipeConfigurator(SYSTEM_LEVEL_DATA_DICT, RECOVERY_TIME_STEPPING_RULE)
    
    def test_set_geometry(self, pipe_component, component_configurator):
        component_data = {}
        component_data['Information'] = R2D_PIPE_DATA
        component_configurator.set_geometry(pipe_component, component_data)
        assert pipe_component.length == R2D_PIPE_DATA['GeneralInformation']['Len']

    def test_set_repair_configurator(self, pipe_component, component_configurator):
        component_configurator.set_repair_configurator(pipe_component)
        assert isinstance(component_configurator.repair_configurator, R2DPipeRepairConfigurator)
        assert component_configurator.repair_configurator.system_level_data == SYSTEM_LEVEL_DATA_DICT

    def test_set_r2d_dict_getter(self, pipe_component, component_configurator):
        component_configurator.set_r2d_dict_getter(pipe_component)
        assert isinstance(pipe_component.r2d_dict_getter, R2DPipeDictGetter)
        
# TODO: Test component configurators for other R2D components once classes are fully implemented.
class TestR2DBridgeConfigurator:
    pass

class TestR2DTunnelConfigurator:
    pass