import pytest
from pyrecodes.utilities import read_json_file, get_locality_coordinates_from_geojson
from pyrecodes import main
import shapely
from pyrecodes.subsystem_creator.r2d_subsystem_creator import R2DSubsystemCreator, R2DSubsystemCreatorWithHouseholds
from tests.test_subsystem_creator.test_subsystem_creator_inputs import FOLDER_NAME, MAIN_FILE_REWET, MAIN_FILE_ALAMEDA, LOCALITY_1_BOUNDING_BOX, LOCALITY_2_BOUNDING_BOX, LOCALITY_ALAMEDA_GEOJSON, CONSTANTS, PARAMETERS_R2D_WATER_SYSTEM, PARAMETERS_R2D_BUILDINGS, DAMAGE_INPUT_R2D, PARAMETERS_R2D_ALAMEDA, DAMAGE_INPUT_ALAMEDA, MAIN_FILE_HOUSEHOLDS, LOCALITY_ALAMEDA_963_GEOJSON, CONSTANTS_WITH_HOUSEHOLDS, PARAMETERS_R2D_ALAMEDA_WITH_HOUSEHOLDS, DAMAGE_INPUT_ALAMEDA_SHORT_RECOVERY
from pyrecodes.component_configurator.r2d_component_configurator import R2DPipeConfigurator, R2DBuildingConfigurator, R2DBuildingWithHouseholdsConfigurator

class TestR2DSubsystemCreator:

    @pytest.fixture
    def component_library(self):
        input_dict = read_json_file(f'{FOLDER_NAME}/{MAIN_FILE_REWET}')
        return main.form_component_library(FOLDER_NAME, input_dict)

    @pytest.fixture
    def component_library_alameda(self):
        input_dict = read_json_file(f'{FOLDER_NAME}/{MAIN_FILE_ALAMEDA}')
        return main.form_component_library(FOLDER_NAME, input_dict)

    @pytest.fixture
    def r2d_subsystem_creator_alameda(self, component_library_alameda):
        bounding_box = get_locality_coordinates_from_geojson(LOCALITY_ALAMEDA_GEOJSON)
        return R2DSubsystemCreator(component_library_alameda, {"LocalityName": "Alameda 964", "Coordinates": bounding_box}, PARAMETERS_R2D_ALAMEDA, constants=CONSTANTS, damage_input=DAMAGE_INPUT_ALAMEDA)

    def test_create_components_in_localities_three_localities_community(self, component_library):
        r2d_subsystem_creator = R2DSubsystemCreator(component_library, LOCALITY_1_BOUNDING_BOX, PARAMETERS_R2D_WATER_SYSTEM, constants=CONSTANTS, damage_input=DAMAGE_INPUT_R2D)
        components = r2d_subsystem_creator.create_components_in_localities()
        assert len(components) == 1
        assert components[0].name == 'DS0_Pipe'

        r2d_subsystem_creator = R2DSubsystemCreator(component_library, LOCALITY_2_BOUNDING_BOX, PARAMETERS_R2D_WATER_SYSTEM, constants=CONSTANTS, damage_input=DAMAGE_INPUT_R2D)
        components = r2d_subsystem_creator.create_components_in_localities()
        assert len(components) == 1
        assert components[0].name == 'DS0_Pipe'

    def test_create_components_alameda_buildings(self, component_library_alameda, r2d_subsystem_creator_alameda):
        components = r2d_subsystem_creator_alameda.create_components_in_localities()
        assert len(components) == 5
        assert components[0].name == 'DS2_Building'
        assert components[1].name == 'DS1_Building'
        assert components[2].name == 'DS2_Building'
        assert components[3].name == 'DS1_Building'
        assert components[4].name == 'DS2_Building'

        r2d_subsystem_creator_alameda.parameters['MaxNumComponents'] = 3
        components = r2d_subsystem_creator_alameda.create_components_in_localities()
        assert len(components) == 3

    def test_set_component_configurator(self, component_library):
        r2d_subsystem_creator = R2DSubsystemCreator(component_library, LOCALITY_1_BOUNDING_BOX, PARAMETERS_R2D_WATER_SYSTEM, constants=CONSTANTS, damage_input=DAMAGE_INPUT_R2D)
        r2d_subsystem_creator.set_component_configurator()
        assert isinstance(r2d_subsystem_creator.component_configurator['Pipe'], R2DPipeConfigurator)

        r2d_subsystem_creator = R2DSubsystemCreator(component_library, LOCALITY_1_BOUNDING_BOX, PARAMETERS_R2D_BUILDINGS, constants=CONSTANTS, damage_input=DAMAGE_INPUT_R2D)
        r2d_subsystem_creator.set_component_configurator()
        assert isinstance(r2d_subsystem_creator.component_configurator['Building'], R2DBuildingConfigurator)

    def test_create_component(self, component_library, r2d_subsystem_creator_alameda):
        component_info = {'GeneralInformation': {'type': 'Building',
                                                 'PlanArea': 5400,
                                                 'NumberOfStories': 2,
                                                 'AIM_id': 1,
                                                 'Footprint': "{\"type\":\"Feature\",\"geometry\":{\"type\":\"Polygon\",\"coordinates\":[[[-122.293878,37.771004],[-122.293973,37.771029],[-122.294025,37.770903],[-122.293931,37.770878],[-122.293878,37.771004]]]},\"properties\":{}}",}}
        damage_info = {"Damage": {
          "GF.H.S-1": 0,
          "GF.V.S-1": 0,
          "LF.W1.MC-1": 2,
          "collapse-0": 0
        },
        "Loss": {
          "Repair": {
            "Cost": {
              "LF.IND2-LF.W1.MC": 10.0,
              "replacement-collapse": 0.0
            },
            "Time": {
              "LF.IND2-LF.W1.MC": 30.0,
              "replacement-collapse": 0.0
            }
          }
        }}
        asset_type = 'Buildings'
        asset_subtype = 'Building'
        component = r2d_subsystem_creator_alameda.create_component(component_info, damage_info, asset_type, asset_subtype)
        assert component[0].name == 'DS2_Building'
        assert component[0].recovery_model.recovery_activities['Repair'].duration > 0
        assert component[0].recovery_model.recovery_activities['Repair'].demand['RepairCrew_Buildings'].current_amount == 2

    def test_get_component_geometry(self, r2d_subsystem_creator_alameda):
        component_info = {'GeneralInformation': {'location': {'latitude': 37.771004, 'longitude': -122.293878}}}
        component_geometry = r2d_subsystem_creator_alameda.get_component_geometry(component_info)
        assert isinstance(component_geometry, shapely.Point)
        assert [component_geometry.y, component_geometry.x] == [-122.293878, 37.771004]

    def test_get_component_damage_state(self, r2d_subsystem_creator_alameda):
        damage_info = {"Damage": {
          "GF.H.S-1": 0,
          "GF.V.S-1": 0,
          "LF.W1.MC-1": 2,
          "collapse-0": 0
        }}
        assert r2d_subsystem_creator_alameda.get_component_damage_state(damage_info, 'Building') == 2

        damage_info = {"Damage": {
          "GF.H.S-1": 0,
          "GF.V.S-1": 0,
          "LF.W1.MC-1": 0,
          "collapse-0": 1
        }}
        assert r2d_subsystem_creator_alameda.get_component_damage_state(damage_info, 'Building') == 4

        damage_info = {"Damage": {
          "GF.H.S-1": 1,
          "GF.V.S-1": 0,
          "LF.W1.MC-1": 0,
          "collapse-0": 1
        }}
        assert r2d_subsystem_creator_alameda.get_component_damage_state(damage_info, 'Building') == 4

        damage_info = {"Damage": {
          "GF.H.S-1": 1,
          "GF.V.S-1": 0,
          "LF.W1.MC-1": 0,
          "collapse-0": 0
        }}
        assert r2d_subsystem_creator_alameda.get_component_damage_state(damage_info, 'Building') == 1

    def test_get_component_name(self, r2d_subsystem_creator_alameda):
        out_of_town_info = {'GeneralInformation': {'OccupancyClass': 'OutOfTown'}}
        assert r2d_subsystem_creator_alameda.get_component_name(out_of_town_info, 0, 'Building') == 'NeighboringTown'

        normal_info = {'GeneralInformation': {'OccupancyClass': 'RES1'}}
        assert r2d_subsystem_creator_alameda.get_component_name(normal_info, 2, 'Building') == 'DS2_Building'
        assert r2d_subsystem_creator_alameda.get_component_name(normal_info, 0, 'Pipe') == 'DS0_Pipe'


class TestR2DSubsystemCreatorWithHouseholds:

    @pytest.fixture
    def component_library_households(self):
        input_dict = read_json_file(f'{FOLDER_NAME}/{MAIN_FILE_HOUSEHOLDS}')
        return main.form_component_library(FOLDER_NAME, input_dict)

    @pytest.fixture
    def r2d_subsystem_creator_with_households(self, component_library_households):
        bounding_box = get_locality_coordinates_from_geojson(LOCALITY_ALAMEDA_963_GEOJSON)
        return R2DSubsystemCreatorWithHouseholds(
            component_library_households,
            {"LocalityName": "Alameda 963", "Coordinates": bounding_box},
            PARAMETERS_R2D_ALAMEDA_WITH_HOUSEHOLDS,
            constants=CONSTANTS_WITH_HOUSEHOLDS,
            damage_input=DAMAGE_INPUT_ALAMEDA_SHORT_RECOVERY
        )

    def test_get_component_configurator(self, r2d_subsystem_creator_with_households):
        assert r2d_subsystem_creator_with_households.get_component_configurator('Building') == R2DBuildingWithHouseholdsConfigurator
        assert r2d_subsystem_creator_with_households.get_component_configurator('Pipe') == R2DPipeConfigurator

    def test_get_component_name(self, r2d_subsystem_creator_with_households):
        out_of_town_info = {'GeneralInformation': {'OccupancyClass': 'OutOfTown'}}
        assert r2d_subsystem_creator_with_households.get_component_name(out_of_town_info, 0, 'Building') == 'NeighboringTown'

        normal_info = {'GeneralInformation': {'OccupancyClass': 'RES1'}}
        assert r2d_subsystem_creator_with_households.get_component_name(normal_info, 2, 'Building') == 'DS2_Building'

    def test_create_components_in_localities(self, r2d_subsystem_creator_with_households):
        components = r2d_subsystem_creator_with_households.create_components_in_localities()
        assert len(components) == 4
        assert components[0].name == 'NeighboringTown'
        assert components[1].name == 'DS2_Building'
        assert components[2].name == 'DS1_Building'
        assert components[3].name == 'DS3_Building'

    def test_create_components_initializes_households(self, r2d_subsystem_creator_with_households):
        r2d_subsystem_creator_with_households.create_components_in_localities()
        assert len(r2d_subsystem_creator_with_households.households) == 2

    def test_prepare_component_info_clears_households_when_max_exceeded(self, r2d_subsystem_creator_with_households):
        r2d_subsystem_creator_with_households.households = ['mock_household_1']
        r2d_subsystem_creator_with_households.parameters['MaxNumHouseholds'] = 0
        component_info = {'GeneralInformation': {'Households': [{'HouseholdID': 'h1'}, {'HouseholdID': 'h2'}]}}
        r2d_subsystem_creator_with_households._prepare_component_info(component_info)
        assert component_info['GeneralInformation']['Households'] == []

    def test_prepare_component_info_keeps_households_when_under_max(self, r2d_subsystem_creator_with_households):
        r2d_subsystem_creator_with_households.households = []
        r2d_subsystem_creator_with_households.parameters['MaxNumHouseholds'] = 10
        original_households = [{'HouseholdID': 'h1'}]
        component_info = {'GeneralInformation': {'Households': original_households}}
        r2d_subsystem_creator_with_households._prepare_component_info(component_info)
        assert component_info['GeneralInformation']['Households'] == original_households

    def test_after_component_created_collects_households(self, r2d_subsystem_creator_with_households):
        r2d_subsystem_creator_with_households.households = []

        class MockComponent:
            households = ['h1', 'h2']

        class MockComponentNoHouseholds:
            pass

        r2d_subsystem_creator_with_households._after_component_created(MockComponent())
        assert r2d_subsystem_creator_with_households.households == ['h1', 'h2']

        r2d_subsystem_creator_with_households._after_component_created(MockComponentNoHouseholds())
        assert r2d_subsystem_creator_with_households.households == ['h1', 'h2']

    def test_create_components_max_num_components(self, r2d_subsystem_creator_with_households):
        r2d_subsystem_creator_with_households.parameters['MaxNumComponents'] = 2
        components = r2d_subsystem_creator_with_households.create_components_in_localities()
        assert len(components) == 2
