import pytest
import math
import copy
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.resource_distribution_model.residual_demand_traffic_distribution_model_constructor import ResidualDemandTrafficDistributionModelConstructor
from pyrecodes.resource_distribution_model.residual_demand_traffic_distribution_model import ResidualDemandTrafficDistributionModel
from tests.test_resource_distribution_model.test_resource_distribution_model_inputs import MAIN_FILE_RESIDUAL_DEMAND, RESOURCE_NAME_RESIDUAL_DEMAND, RESOURCE_PARAMETERS_RESIDUAL_DEMAND, INITIAL_R2D_DICT_RESIDUAL_DEMAND

UNDAMAGED_TRAVEL_TIMES = [2660.83, 2660.83, 1874.03, 1874.03]

class TestResidualDemandTrafficDistributionModel:

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(MAIN_FILE_RESIDUAL_DEMAND)
        return main.create_system(input_dict)

    @pytest.fixture
    def residual_demand_traffic_distribution_model_constructor(self):
        return ResidualDemandTrafficDistributionModelConstructor()
    
    @pytest.fixture
    def residual_demand_traffic_distribution_model(self, system):
        return ResidualDemandTrafficDistributionModel(RESOURCE_NAME_RESIDUAL_DEMAND, RESOURCE_PARAMETERS_RESIDUAL_DEMAND, system.components)
    
    def create_damaged_system(self, main_file: str):
        input_dict = read_json_file(main_file)
        return main.create_system(input_dict)
    
    def test_init(self, residual_demand_traffic_distribution_model):
        assert isinstance(residual_demand_traffic_distribution_model.constructor, ResidualDemandTrafficDistributionModelConstructor)
        assert residual_demand_traffic_distribution_model.transfer_service_distribution_model is None
        assert residual_demand_traffic_distribution_model.travel_times == []
    
    def test_update_r2d_dict(self, residual_demand_traffic_distribution_model):
        TEMP_R2D_DICT = copy.deepcopy(INITIAL_R2D_DICT_RESIDUAL_DEMAND)
        assert residual_demand_traffic_distribution_model.r2d_dict == TEMP_R2D_DICT
        residual_demand_traffic_distribution_model.components[1].general_information['FunctionalityLevel'] = 0.5

        residual_demand_traffic_distribution_model.update_r2d_dict()
        TEMP_R2D_DICT['TransportationNetwork']['Roadway']['2']['GeneralInformation']['FunctionalityLevel'] = 0.5
        assert residual_demand_traffic_distribution_model.r2d_dict == TEMP_R2D_DICT   

        residual_demand_traffic_distribution_model.components[6].general_information['FunctionalityLevel'] = 0.8
        residual_demand_traffic_distribution_model.update_r2d_dict()
        TEMP_R2D_DICT['TransportationNetwork']['Roadway']['1']['GeneralInformation']['FunctionalityLevel'] = 0.8
        assert residual_demand_traffic_distribution_model.r2d_dict == TEMP_R2D_DICT 

    def test_distribute_traffic_undamaged(self, residual_demand_traffic_distribution_model):
        residual_demand_traffic_distribution_model.distribute_traffic()
        assert len(residual_demand_traffic_distribution_model.travel_times) == 1
        for travel_time_used, target_travel_time in zip(residual_demand_traffic_distribution_model.travel_times[0]['travel_time_used'], UNDAMAGED_TRAVEL_TIMES):
            assert travel_time_used == target_travel_time

    def test_distribute_traffic_damaged_all_roads(self, residual_demand_traffic_distribution_model, system):
        system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityResidualDemand_Main_AllRoadsDamaged.json')
        system.time_step = 0
        system.set_initial_damage()
        system.update()
        residual_demand_traffic_distribution_model.components = system.components
        residual_demand_traffic_distribution_model.update_r2d_dict()
        residual_demand_traffic_distribution_model.distribute_traffic()
        assert len(residual_demand_traffic_distribution_model.travel_times) == 1
        for travel_time_used in residual_demand_traffic_distribution_model.travel_times[0]['travel_time_used']:
            assert travel_time_used == math.inf

        for time_step in range(1, 50):
            system.time_step = time_step
            system.update()
            system.recover()

        system.update()
        residual_demand_traffic_distribution_model.components = system.components
        residual_demand_traffic_distribution_model.update_r2d_dict()
        residual_demand_traffic_distribution_model.distribute_traffic()
        assert len(residual_demand_traffic_distribution_model.travel_times) == 2
        for travel_time_used in residual_demand_traffic_distribution_model.travel_times[1]['travel_time_used']:
            assert travel_time_used == math.inf

        for time_step in range(51, 103):
            system.time_step = time_step
            system.update()
            system.recover()  

        system.update()
        residual_demand_traffic_distribution_model.components = system.components
        residual_demand_traffic_distribution_model.update_r2d_dict()
        residual_demand_traffic_distribution_model.distribute_traffic()
        assert len(residual_demand_traffic_distribution_model.travel_times) == 3
        for travel_time_used, target_travel_time in zip(residual_demand_traffic_distribution_model.travel_times[2]['travel_time_used'], UNDAMAGED_TRAVEL_TIMES):
            assert travel_time_used == target_travel_time

    def test_distribute_traffic_partially_damaged_all_roads(self, residual_demand_traffic_distribution_model, system):
        system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityResidualDemand_Main_AllRoadsInDS2.json')
        system.time_step = 0
        system.set_initial_damage()
        system.update()
        residual_demand_traffic_distribution_model.components = system.components
        residual_demand_traffic_distribution_model.update_r2d_dict()
        residual_demand_traffic_distribution_model.distribute_traffic()
        assert len(residual_demand_traffic_distribution_model.travel_times) == 1
        for travel_time_used, undamaged_travel_time in zip(residual_demand_traffic_distribution_model.travel_times[0]['travel_time_used'], UNDAMAGED_TRAVEL_TIMES):
            assert math.isclose(travel_time_used, 2 * undamaged_travel_time, rel_tol=1e-2)

        for time_step in range(1, 20):
            system.time_step = time_step
            system.update()
            system.recover()

        system.update()
        residual_demand_traffic_distribution_model.components = system.components
        residual_demand_traffic_distribution_model.update_r2d_dict()
        residual_demand_traffic_distribution_model.distribute_traffic()
        assert len(residual_demand_traffic_distribution_model.travel_times) == 2
        for travel_time_used, undamaged_travel_time in zip(residual_demand_traffic_distribution_model.travel_times[1]['travel_time_used'], UNDAMAGED_TRAVEL_TIMES):
            assert math.isclose(travel_time_used, 2 * undamaged_travel_time, rel_tol=1e-2)

        for time_step in range(21, 43):
            system.time_step = time_step
            system.update()
            system.recover()  

        system.update()
        residual_demand_traffic_distribution_model.components = system.components
        residual_demand_traffic_distribution_model.update_r2d_dict()
        residual_demand_traffic_distribution_model.distribute_traffic()
        assert len(residual_demand_traffic_distribution_model.travel_times) == 3
        for travel_time_used, target_travel_time in zip(residual_demand_traffic_distribution_model.travel_times[2]['travel_time_used'], UNDAMAGED_TRAVEL_TIMES):
            assert travel_time_used == target_travel_time

    def test_distribute_traffic_damaged_road_2(self, residual_demand_traffic_distribution_model, system):
        TARGET_TRAVEL_TIMES = [2660.83, 2660.83, 1874.03+2660.83, 1874.03+2660.83]
        
        system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityResidualDemand_Main_Road2Damaged.json')
        system.time_step = 0
        system.set_initial_damage()
        system.update()
        residual_demand_traffic_distribution_model.components = system.components
        residual_demand_traffic_distribution_model.update_r2d_dict()
        residual_demand_traffic_distribution_model.distribute_traffic()
        assert len(residual_demand_traffic_distribution_model.travel_times) == 1
        for travel_time_used, target_travel_time in zip(residual_demand_traffic_distribution_model.travel_times[0]['travel_time_used'], TARGET_TRAVEL_TIMES):
            assert math.isclose(travel_time_used, target_travel_time, rel_tol=1e-4)

        for time_step in range(1, 50):
            system.time_step = time_step
            system.update()
            system.recover()

        system.update()
        residual_demand_traffic_distribution_model.components = system.components
        residual_demand_traffic_distribution_model.update_r2d_dict()
        residual_demand_traffic_distribution_model.distribute_traffic()
        assert len(residual_demand_traffic_distribution_model.travel_times) == 2
        for travel_time_used, target_travel_time in zip(residual_demand_traffic_distribution_model.travel_times[1]['travel_time_used'], TARGET_TRAVEL_TIMES):
            assert math.isclose(travel_time_used, target_travel_time, rel_tol=1e-4)

        for time_step in range(51, 103):
            system.time_step = time_step
            system.update()
            system.recover()  

        system.update()
        residual_demand_traffic_distribution_model.components = system.components
        residual_demand_traffic_distribution_model.update_r2d_dict()
        residual_demand_traffic_distribution_model.distribute_traffic()
        assert len(residual_demand_traffic_distribution_model.travel_times) == 3
        for travel_time_used, target_travel_time in zip(residual_demand_traffic_distribution_model.travel_times[2]['travel_time_used'], UNDAMAGED_TRAVEL_TIMES):
            assert travel_time_used == target_travel_time

    def test_distribute_traffic_od_changed(self, residual_demand_traffic_distribution_model, system):
        TARGET_TRAVEL_TIMES = [2660.83, 0, 1874.03, 0]
        system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityResidualDemand_Main_BuildingDamaged.json')
        residual_demand_traffic_distribution_model.components = system.components
        residual_demand_traffic_distribution_model.update_r2d_dict()
        residual_demand_traffic_distribution_model.distribute_traffic()
        for travel_time_used, target_travel_time in zip(residual_demand_traffic_distribution_model.travel_times[0]['travel_time_used'], UNDAMAGED_TRAVEL_TIMES):
            assert travel_time_used == target_travel_time

        system.time_step = 0
        system.set_initial_damage()
        system.update()
        residual_demand_traffic_distribution_model.components = system.components
        residual_demand_traffic_distribution_model.update_r2d_dict()
        residual_demand_traffic_distribution_model.distribute_traffic()
        for travel_time_used, target_travel_time in zip(residual_demand_traffic_distribution_model.travel_times[1]['travel_time_used'], TARGET_TRAVEL_TIMES):
            assert math.isclose(travel_time_used, target_travel_time, rel_tol=1e-4)

        for time_step in range(1, 15):
            system.time_step = time_step
            system.update()
            system.recover()

        system.update()
        residual_demand_traffic_distribution_model.components = system.components
        residual_demand_traffic_distribution_model.update_r2d_dict()
        residual_demand_traffic_distribution_model.distribute_traffic()
        for travel_time_used, target_travel_time in zip(residual_demand_traffic_distribution_model.travel_times[2]['travel_time_used'], TARGET_TRAVEL_TIMES):
            assert math.isclose(travel_time_used, target_travel_time, rel_tol=1e-4)

        for time_step in range(15, 33):
            system.time_step = time_step
            system.update()
            system.recover()  

        system.update()
        residual_demand_traffic_distribution_model.components = system.components
        residual_demand_traffic_distribution_model.update_r2d_dict()
        residual_demand_traffic_distribution_model.distribute_traffic()
        for travel_time_used, target_travel_time in zip(residual_demand_traffic_distribution_model.travel_times[-1]['travel_time_used'], UNDAMAGED_TRAVEL_TIMES):
            assert travel_time_used == target_travel_time

    def test_sparse_distribution_time_stepping(self, residual_demand_traffic_distribution_model, system):
        RESOURCE_PARAMETERS_RESIDUAL_DEMAND_SPARSE = copy.deepcopy(RESOURCE_PARAMETERS_RESIDUAL_DEMAND)
        RESOURCE_PARAMETERS_RESIDUAL_DEMAND_SPARSE['DistributionTimeStepping'] = [{"start": 0, "end": 5, "step": 1}, {"start": 5, "end": 100, "step": 3}]
        residual_demand_traffic_distribution_model = ResidualDemandTrafficDistributionModel(RESOURCE_NAME_RESIDUAL_DEMAND, RESOURCE_PARAMETERS_RESIDUAL_DEMAND_SPARSE, system.components)
        for time_step in range(0, 20):
            residual_demand_traffic_distribution_model.distribute(time_step)
        assert len(residual_demand_traffic_distribution_model.travel_times) == 20
        for time_step in range(0, 5):
            assert (residual_demand_traffic_distribution_model.travel_times[time_step]['travel_time_used'] == UNDAMAGED_TRAVEL_TIMES).all()
        for time_step in range(5, 20):
            if (time_step-5) % 3 == 0:
                assert (residual_demand_traffic_distribution_model.travel_times[time_step]['travel_time_used'] == UNDAMAGED_TRAVEL_TIMES).all()
            else:
                assert residual_demand_traffic_distribution_model.travel_times[time_step] == []

    def test_get_total_supply(self, residual_demand_traffic_distribution_model, system):
        residual_demand_traffic_distribution_model.distribute(0)
        assert residual_demand_traffic_distribution_model.get_total_supply('All') == 4

        system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityResidualDemand_Main_AllRoadsDamaged.json')
        system.time_step = 0
        system.set_initial_damage()
        system.update()
        residual_demand_traffic_distribution_model.components = system.components
        residual_demand_traffic_distribution_model.update_r2d_dict()
        residual_demand_traffic_distribution_model.distribute(1)
        assert residual_demand_traffic_distribution_model.get_total_supply('All') == 0
        
        system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityResidualDemand_Main_Road2Damaged.json')
        system.time_step = 0
        system.set_initial_damage()
        system.update()
        residual_demand_traffic_distribution_model.TRIP_CUTOFF_THRESHOLD = 1.49
        residual_demand_traffic_distribution_model.components = system.components
        residual_demand_traffic_distribution_model.update_r2d_dict()
        residual_demand_traffic_distribution_model.distribute(1)
        assert residual_demand_traffic_distribution_model.get_total_supply('All') == 2

    def test_get_total_demand(self, residual_demand_traffic_distribution_model, system):
        residual_demand_traffic_distribution_model.distribute(0)
        assert residual_demand_traffic_distribution_model.get_total_demand('All') == 4

        system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityResidualDemand_Main_AllRoadsDamaged.json')
        system.time_step = 0
        system.set_initial_damage()
        system.update()
        residual_demand_traffic_distribution_model.components = system.components
        residual_demand_traffic_distribution_model.update_r2d_dict()
        residual_demand_traffic_distribution_model.distribute(1)
        assert residual_demand_traffic_distribution_model.get_total_demand('All') == 4
        
        system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityResidualDemand_Main_Road2Damaged.json')
        system.time_step = 0
        system.set_initial_damage()
        system.update()
        residual_demand_traffic_distribution_model.TRIP_CUTOFF_THRESHOLD = 1.49
        residual_demand_traffic_distribution_model.components = system.components
        residual_demand_traffic_distribution_model.update_r2d_dict()
        residual_demand_traffic_distribution_model.distribute(1)
        assert residual_demand_traffic_distribution_model.get_total_demand('All') == 4




        
       



        

        


        

    # def test_component_is_a_building(self, rewet_distribution_model):
    #     assert rewet_distribution_model.component_is_a_building(rewet_distribution_model.components[12]) == True
    #     assert rewet_distribution_model.component_is_a_building(rewet_distribution_model.components[0]) == False

    # def test_component_has_demand_for_water(self, rewet_distribution_model):
    #     assert rewet_distribution_model.component_has_demand_for_water(rewet_distribution_model.components[12]) == True
    #     assert rewet_distribution_model.component_has_demand_for_water(rewet_distribution_model.components[0]) == False

    # def test_distribute_water_no_damage(self, rewet_distribution_model):
    #     met_demand_per_building = rewet_distribution_model.distribute_water(0)
    #     assert met_demand_per_building == {"1": 1.0}

    #     met_demand_per_building = rewet_distribution_model.distribute_water(10)
    #     assert met_demand_per_building == {"1": 1.0}

    #     met_demand_per_building = rewet_distribution_model.distribute_water(30)
    #     assert met_demand_per_building == {"1": 1.0}

    # def test_distribute_water_pipe_1_damaged(self, rewet_distribution_model, system):
    #     system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_Pipe1Damaged.json')
    #     system.time_step = 0
    #     system.set_initial_damage()
    #     system.update()
    #     rewet_distribution_model.components = system.components
    #     rewet_distribution_model.update_r2d_dict()
    #     met_demand_per_building = rewet_distribution_model.distribute_water(system.time_step)
    #     assert met_demand_per_building == {"1": 1.0}

    # def test_distribute_water_pipe_2_damaged(self, rewet_distribution_model, system):
    #     system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_Pipe2Damaged.json')
    #     system.time_step = 0
    #     system.set_initial_damage()
    #     system.update()
    #     rewet_distribution_model.components = system.components
    #     rewet_distribution_model.update_r2d_dict()
    #     met_demand_per_building = rewet_distribution_model.distribute_water(system.time_step)
    #     assert met_demand_per_building == {"1": 1.0}

    # # These three tests are too strict for the current implementation. In the future figure out why they throw an error.
    # # def test_distribute_water_pipe_3_damaged(self, rewet_distribution_model, system):
    # #     system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_Pipe3Damaged.json')
    # #     system.time_step = 0
    # #     system.set_initial_damage()
    # #     system.update()
    # #     rewet_distribution_model.components = system.components
    # #     rewet_distribution_model.update_r2d_dict()
    # #     met_demand_per_building = rewet_distribution_model.distribute_water(system.time_step)
    # #     assert met_demand_per_building == {"1": 1.0}

    # # def test_distribute_water_pipe_4_damaged(self, rewet_distribution_model, system):
    # #     system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_Pipe4Damaged.json')
    # #     system.time_step = 0
    # #     system.set_initial_damage()
    # #     system.update()
    # #     rewet_distribution_model.components = system.components
    # #     rewet_distribution_model.update_r2d_dict()
    # #     met_demand_per_building = rewet_distribution_model.distribute_water(system.time_step)
    # #     assert met_demand_per_building == {"1": 1.0}

    # # def test_distribute_water_pipe_34_damaged(self, rewet_distribution_model, system):
    # #     system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_Pipes34Damaged.json')
    # #     system.time_step = 0
    # #     system.set_initial_damage()
    # #     system.update()
    # #     rewet_distribution_model.components = system.components
    # #     rewet_distribution_model.update_r2d_dict()
    # #     met_demand_per_building = rewet_distribution_model.distribute_water(system.time_step)
    # #     assert met_demand_per_building == {"1": 1.0}        

    # def test_distribute_water_pipe_12_damaged(self, rewet_distribution_model, system):
    #     system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_Pipes12Damaged.json')
    #     system.time_step = 0
    #     system.set_initial_damage()
    #     system.update()
    #     rewet_distribution_model.components = system.components
    #     rewet_distribution_model.update_r2d_dict()
    #     met_demand_per_building = rewet_distribution_model.distribute_water(system.time_step)
    #     assert met_demand_per_building == {"1": 1.0} 

    # def test_distribute_water_with_all_pipes_damage(self, rewet_distribution_model, system):
    #     system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_AllPipesDamaged.json')
    #     system.time_step = 0
    #     system.set_initial_damage()
    #     system.update()
    #     rewet_distribution_model.components = system.components
    #     rewet_distribution_model.update_r2d_dict()
    #     met_demand_per_building = rewet_distribution_model.distribute_water(system.time_step)
    #     assert met_demand_per_building == {"1": 0.0}

    # def test_distribute_water_in_recovered_system(self, rewet_distribution_model, system):
    #     system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_AllPipesDamaged.json')
    #     system.time_step = 0
    #     system.set_initial_damage()
    #     system.update()
    #     rewet_distribution_model.components = system.components
    #     rewet_distribution_model.update_r2d_dict()
    #     met_demand_per_building = rewet_distribution_model.distribute_water(system.time_step)
    #     assert met_demand_per_building == {"1": 0.0}

    #     for time_step in range(1, 22):
    #         system.time_step = time_step
    #         system.update()
    #         system.recover()

    #     system.update()
    #     rewet_distribution_model.components = system.components
    #     rewet_distribution_model.update_r2d_dict()
    #     met_demand_per_building = rewet_distribution_model.distribute_water(system.time_step)
    #     assert met_demand_per_building == {"1": 1.0}

    # def test_distribute_no_damage(self, rewet_distribution_model):
    #     rewet_distribution_model.distribute(0)
    #     assert rewet_distribution_model.components[12].supply['Supply']['Shelter'].current_amount == 10

    # def test_distribute_all_damage(self, rewet_distribution_model, system):
    #     system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_AllPipesDamaged.json')
    #     system.time_step = 0
    #     system.set_initial_damage()
    #     system.update()
    #     rewet_distribution_model.components = system.components
    #     rewet_distribution_model.distribute(1)
    #     assert rewet_distribution_model.components[12].supply['Supply']['Shelter'].current_amount == 0

    # def test_get_total_supply(self, rewet_distribution_model):
    #     rewet_distribution_model.distribute(0)
    #     assert rewet_distribution_model.get_total_supply() == 0.5

    #     system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_different_water_demand.json')
    #     rewet_distribution_model = REWETDistributionModel(RESOURCE_NAME_REWET, RESOURCE_PARAMETERS_REWET, system.components)
    #     rewet_distribution_model.distribute(1)
    #     assert rewet_distribution_model.get_total_supply() == 1.5

    #     # assign damage and test the demand
    #     system.time_step = 2
    #     system.set_initial_damage()
    #     system.update()
    #     rewet_distribution_model.distribute(2)
    #     assert rewet_distribution_model.get_total_supply() == 0.0

    #     # recover system and then check demand
    #     system.start_resilience_assessment()
    #     rewet_distribution_model.distribute(32)
    #     assert math.isclose(rewet_distribution_model.get_total_supply(), 1.5)

    # def test_get_water_demand(self, system, rewet_distribution_model):
    #     system.time_step = 0
    #     system.update()
    #     rewet_distribution_model.components = system.components
    #     assert rewet_distribution_model.get_total_demand() == 0.5

    #     # check with different population in the building and therefore, different demand
    #     system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_different_water_demand.json')
    #     rewet_distribution_model = REWETDistributionModel(RESOURCE_NAME_REWET, RESOURCE_PARAMETERS_REWET, system.components)
    #     assert rewet_distribution_model.get_total_demand() == 1.5

    #     # assign damage and test the demand
    #     system.time_step = 1
    #     system.set_initial_damage()
    #     system.update()
    #     assert rewet_distribution_model.get_total_demand() == 0.0

    #     system.time_step = 2
    #     system.recover()
    #     system.update()
    #     assert math.isclose(rewet_distribution_model.get_total_demand(), 1.5 * 1/30)

    #     # recover system and then check demand
    #     system.start_resilience_assessment()
    #     assert math.isclose(rewet_distribution_model.get_total_demand(), 1.5)

    # def test_get_water_consumption(self, rewet_distribution_model):
    #     rewet_distribution_model.distribute(0)
    #     assert rewet_distribution_model.get_total_consumption() == 0.5

    #     system = self.create_damaged_system('./tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main_different_water_demand.json')
    #     rewet_distribution_model = REWETDistributionModel(RESOURCE_NAME_REWET, RESOURCE_PARAMETERS_REWET, system.components)
    #     rewet_distribution_model.distribute(1)
    #     assert rewet_distribution_model.get_total_consumption() == 1.5

    #     # assign damage and test the demand
    #     system.time_step = 2
    #     system.set_initial_damage()
    #     system.update()
    #     rewet_distribution_model.distribute(2)
    #     assert rewet_distribution_model.get_total_consumption() == 0.0

    #     # recover system and then check demand
    #     system.start_resilience_assessment()
    #     rewet_distribution_model.distribute(32)
    #     assert math.isclose(rewet_distribution_model.get_total_consumption(), 1.5)





