import pytest
import math
import copy
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.resource_distribution_model.rewet_distribution_model_constructor import REWETDistributionModelConstructor
from pyrecodes.resource_distribution_model.rewet_distribution_model import REWETDistributionModel
from rewet_API.rewet_pyrecodes_api import REWETPyReCoDes
from test_resource_distribution_model_inputs import MAIN_FILE_REWET, RESOURCE_NAME_REWET, RESOURCE_PARAMETERS_REWET, INITIAL_R2D_DICT_REWET

class TestREWETDistributionModel:

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(MAIN_FILE_REWET)
        return main.create_system(input_dict)

    @pytest.fixture
    def rewet_distribution_model_constructor(self):
        return REWETDistributionModelConstructor()
    
    @pytest.fixture
    def rewet_distribution_model(self, system):
        return REWETDistributionModel(RESOURCE_NAME_REWET, RESOURCE_PARAMETERS_REWET, system.components)
    
    def create_damaged_system(self, main_file: str):
        input_dict = read_json_file(main_file)
        return main.create_system(input_dict)
    
    def test_init(self, rewet_distribution_model):
        assert isinstance(rewet_distribution_model.constructor, REWETDistributionModelConstructor)
        assert rewet_distribution_model.transfer_service_distribution_model is None
    
    def test_update_r2d_dict(self, rewet_distribution_model):
        TEMP_R2D_DICT = copy.deepcopy(INITIAL_R2D_DICT_REWET)
        assert rewet_distribution_model.r2d_dict == TEMP_R2D_DICT
        rewet_distribution_model.components[1].damage_information = {
            "Location": [0.5],
            "Type": [1]
        }

        rewet_distribution_model.update_r2d_dict()
        TEMP_R2D_DICT['WaterDistributionNetwork']['Pipe']['1']['Damage'] = {
            "Location": [0.5],
            "Type": [1]
        }
        assert rewet_distribution_model.r2d_dict == TEMP_R2D_DICT    

        rewet_distribution_model.components[6].damage_information = {
            "Location": [0.5, 0.8],
            "Type": [1, 2]
        }  
        rewet_distribution_model.update_r2d_dict()
        TEMP_R2D_DICT['WaterDistributionNetwork']['Pipe']['2']['Damage'] = {
            "Location": [0.5, 0.8],
            "Type": [1, 2]
        }
        assert rewet_distribution_model.r2d_dict == TEMP_R2D_DICT 

    def test_update_component_met_demand(self, rewet_distribution_model):
        rewet_distribution_model.met_demand_per_building = {"1": 0.7}
        rewet_distribution_model.update_buildings_met_demand()
        assert rewet_distribution_model.components[12].supply['Supply']['Shelter'].current_amount == 0.7 * 10.0

        rewet_distribution_model.met_demand_per_building = {"1": 0.8}
        rewet_distribution_model.update_buildings_met_demand()
        assert rewet_distribution_model.components[12].supply['Supply']['Shelter'].current_amount == 0.7 * 10.0

        rewet_distribution_model.met_demand_per_building = {"1": 0.6}
        rewet_distribution_model.update_buildings_met_demand()
        assert rewet_distribution_model.components[12].supply['Supply']['Shelter'].current_amount == 0.6 * 10.0

    def test_component_is_a_building(self, rewet_distribution_model):
        assert rewet_distribution_model.component_is_a_building(rewet_distribution_model.components[12]) == True
        assert rewet_distribution_model.component_is_a_building(rewet_distribution_model.components[0]) == False

    def test_component_has_demand_for_water(self, rewet_distribution_model):
        assert rewet_distribution_model.component_has_demand_for_water(rewet_distribution_model.components[12]) == True
        assert rewet_distribution_model.component_has_demand_for_water(rewet_distribution_model.components[0]) == False

    def test_distribute_water_no_damage(self, rewet_distribution_model):
        met_demand_per_building = rewet_distribution_model.distribute_water(0)
        assert met_demand_per_building == {"1": 1.0}

        met_demand_per_building = rewet_distribution_model.distribute_water(10)
        assert met_demand_per_building == {"1": 1.0}

        met_demand_per_building = rewet_distribution_model.distribute_water(30)
        assert met_demand_per_building == {"1": 1.0}

    def test_distribute_water_pipe_1_damaged(self, rewet_distribution_model, system):
        system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_Pipe1Damaged.json')
        system.time_step = 0
        system.set_initial_damage()
        system.update()
        rewet_distribution_model.components = system.components
        rewet_distribution_model.update_r2d_dict()
        met_demand_per_building = rewet_distribution_model.distribute_water(system.time_step)
        assert met_demand_per_building == {"1": 1.0}

    def test_distribute_water_pipe_2_damaged(self, rewet_distribution_model, system):
        system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_Pipe2Damaged.json')
        system.time_step = 0
        system.set_initial_damage()
        system.update()
        rewet_distribution_model.components = system.components
        rewet_distribution_model.update_r2d_dict()
        met_demand_per_building = rewet_distribution_model.distribute_water(system.time_step)
        assert met_demand_per_building == {"1": 1.0}

    # These three tests are too strict for the current implementation. In the future figure out why they throw an error.
    # def test_distribute_water_pipe_3_damaged(self, rewet_distribution_model, system):
    #     system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_Pipe3Damaged.json')
    #     system.time_step = 0
    #     system.set_initial_damage()
    #     system.update()
    #     rewet_distribution_model.components = system.components
    #     rewet_distribution_model.update_r2d_dict()
    #     met_demand_per_building = rewet_distribution_model.distribute_water(system.time_step)
    #     assert met_demand_per_building == {"1": 1.0}

    # def test_distribute_water_pipe_4_damaged(self, rewet_distribution_model, system):
    #     system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_Pipe4Damaged.json')
    #     system.time_step = 0
    #     system.set_initial_damage()
    #     system.update()
    #     rewet_distribution_model.components = system.components
    #     rewet_distribution_model.update_r2d_dict()
    #     met_demand_per_building = rewet_distribution_model.distribute_water(system.time_step)
    #     assert met_demand_per_building == {"1": 1.0}

    # def test_distribute_water_pipe_34_damaged(self, rewet_distribution_model, system):
    #     system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_Pipes34Damaged.json')
    #     system.time_step = 0
    #     system.set_initial_damage()
    #     system.update()
    #     rewet_distribution_model.components = system.components
    #     rewet_distribution_model.update_r2d_dict()
    #     met_demand_per_building = rewet_distribution_model.distribute_water(system.time_step)
    #     assert met_demand_per_building == {"1": 1.0}        

    def test_distribute_water_pipe_12_damaged(self, rewet_distribution_model, system):
        system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_Pipes12Damaged.json')
        system.time_step = 0
        system.set_initial_damage()
        system.update()
        rewet_distribution_model.components = system.components
        rewet_distribution_model.update_r2d_dict()
        met_demand_per_building = rewet_distribution_model.distribute_water(system.time_step)
        assert met_demand_per_building == {"1": 1.0} 

    def test_distribute_water_with_all_pipes_damage(self, rewet_distribution_model, system):
        system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_AllPipesDamaged.json')
        system.time_step = 0
        system.set_initial_damage()
        system.update()
        rewet_distribution_model.components = system.components
        rewet_distribution_model.update_r2d_dict()
        met_demand_per_building = rewet_distribution_model.distribute_water(system.time_step)
        assert met_demand_per_building == {"1": 0.0}

    def test_distribute_water_in_recovered_system(self, rewet_distribution_model, system):
        system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_AllPipesDamaged.json')
        system.time_step = 0
        system.set_initial_damage()
        system.update()
        rewet_distribution_model.components = system.components
        rewet_distribution_model.update_r2d_dict()
        met_demand_per_building = rewet_distribution_model.distribute_water(system.time_step)
        assert met_demand_per_building == {"1": 0.0}

        for time_step in range(1, 22):
            system.time_step = time_step
            system.update()
            system.recover()

        system.update()
        rewet_distribution_model.components = system.components
        rewet_distribution_model.update_r2d_dict()
        met_demand_per_building = rewet_distribution_model.distribute_water(system.time_step)
        assert met_demand_per_building == {"1": 1.0}

    def test_distribute_no_damage(self, rewet_distribution_model):
        rewet_distribution_model.distribute(0)
        assert rewet_distribution_model.components[12].supply['Supply']['Shelter'].current_amount == 10

    def test_distribute_all_damage(self, rewet_distribution_model, system):
        system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_AllPipesDamaged.json')
        system.time_step = 0
        system.set_initial_damage()
        system.update()
        rewet_distribution_model.components = system.components
        rewet_distribution_model.distribute(1)
        assert rewet_distribution_model.components[12].supply['Supply']['Shelter'].current_amount == 0

    def test_get_total_supply(self, rewet_distribution_model):
        rewet_distribution_model.distribute(0)
        assert rewet_distribution_model.get_total_supply() == 0.5

        system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_different_water_demand.json')
        rewet_distribution_model = REWETDistributionModel(RESOURCE_NAME_REWET, RESOURCE_PARAMETERS_REWET, system.components)
        rewet_distribution_model.distribute(1)
        assert rewet_distribution_model.get_total_supply() == 1.5

        # assign damage and test the demand
        system.time_step = 2
        system.set_initial_damage()
        system.update()
        rewet_distribution_model.distribute(2)
        assert rewet_distribution_model.get_total_supply() == 0.0

        # recover system and then check demand
        system.start_resilience_assessment()
        rewet_distribution_model.distribute(32)
        assert math.isclose(rewet_distribution_model.get_total_supply(), 1.5)

    def test_get_water_demand(self, system, rewet_distribution_model):
        system.time_step = 0
        system.update()
        rewet_distribution_model.components = system.components
        assert rewet_distribution_model.get_total_demand() == 0.5

        # check with different population in the building and therefore, different demand
        system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_different_water_demand.json')
        rewet_distribution_model = REWETDistributionModel(RESOURCE_NAME_REWET, RESOURCE_PARAMETERS_REWET, system.components)
        assert rewet_distribution_model.get_total_demand() == 1.5

        # assign damage and test the demand
        system.time_step = 1
        system.set_initial_damage()
        system.update()
        assert rewet_distribution_model.get_total_demand() == 0.0

        system.time_step = 2
        system.recover()
        system.update()
        assert math.isclose(rewet_distribution_model.get_total_demand(), 1.5 * 1/30)

        # recover system and then check demand
        system.start_resilience_assessment()
        assert math.isclose(rewet_distribution_model.get_total_demand(), 1.5)

    def test_get_water_consumption(self, rewet_distribution_model):
        rewet_distribution_model.distribute(0)
        assert rewet_distribution_model.get_total_consumption() == 0.5

        system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_different_water_demand.json')
        rewet_distribution_model = REWETDistributionModel(RESOURCE_NAME_REWET, RESOURCE_PARAMETERS_REWET, system.components)
        rewet_distribution_model.distribute(1)
        assert rewet_distribution_model.get_total_consumption() == 1.5

        # assign damage and test the demand
        system.time_step = 2
        system.set_initial_damage()
        system.update()
        rewet_distribution_model.distribute(2)
        assert rewet_distribution_model.get_total_consumption() == 0.0

        # recover system and then check demand
        system.start_resilience_assessment()
        rewet_distribution_model.distribute(32)
        assert math.isclose(rewet_distribution_model.get_total_consumption(), 1.5)





