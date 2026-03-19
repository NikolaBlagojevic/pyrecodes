import pytest
from pyrecodes import main
from pyrecodes.component.r2d_building_with_households import R2DBuildingWithHouseholds
from pyrecodes.household.household_gpt import HouseholdGPT
from test_component_inputs import BUILDING_WITH_HOUSEHOLDS_COMPONENT_LIBRARY_PARAMETERS, BUILDING_WITH_HOUSEHOLDS_PARAMETERS

BUILT_ENVIRONMENT_FILENAME = "test_inputs_SmallAlamedaWithHouseholds_Main.json"
FOLDER_NAME = "./tests/test_inputs/"

class TestR2DBuildingWithHouseholds:

    @pytest.fixture
    def r2d_building_with_households(self):
        return R2DBuildingWithHouseholds()

    @pytest.fixture()
    def built_environment(self):
        input_dict = main.read_json_file(f'{FOLDER_NAME}/{BUILT_ENVIRONMENT_FILENAME}')
        return main.create_system(FOLDER_NAME, input_dict)

    @pytest.fixture
    def r2d_building_with_households_with_households(self):
        r2d_building_with_households_with_households = R2DBuildingWithHouseholds()
        r2d_building_with_households_with_households.construct('R2DBuildingWithHouseholds', BUILDING_WITH_HOUSEHOLDS_COMPONENT_LIBRARY_PARAMETERS)
        r2d_building_with_households_with_households.create_households(BUILDING_WITH_HOUSEHOLDS_PARAMETERS['Households'])
        r2d_building_with_households_with_households.general_information = BUILDING_WITH_HOUSEHOLDS_PARAMETERS
        return r2d_building_with_households_with_households
    
    def test_init(self, r2d_building_with_households):
        assert r2d_building_with_households.households == []
        assert r2d_building_with_households.occupied_or_vacant == []

    def test_construct(self, r2d_building_with_households):
        r2d_building_with_households.construct('R2DBuildingWithHouseholds', BUILDING_WITH_HOUSEHOLDS_COMPONENT_LIBRARY_PARAMETERS)
        assert isinstance(r2d_building_with_households.household_object, HouseholdGPT)

    def test_create_households(self, r2d_building_with_households):
        r2d_building_with_households.construct('R2DBuildingWithHouseholds', BUILDING_WITH_HOUSEHOLDS_COMPONENT_LIBRARY_PARAMETERS)
        r2d_building_with_households.create_households(BUILDING_WITH_HOUSEHOLDS_PARAMETERS['Households'])
        assert len(r2d_building_with_households.households) == 2

    def test_map_buildings_to_households(self, r2d_building_with_households):
        # Tested in test_household_gpt.py
        assert True

    def test_update_occupancy_status(self, r2d_building_with_households_with_households):
        r2d_building_with_households_with_households.update_occupancy_status()
        assert r2d_building_with_households_with_households.occupied_or_vacant == ['Occupied']

        r2d_building_with_households_with_households.households = []
        r2d_building_with_households_with_households.update_occupancy_status()
        assert r2d_building_with_households_with_households.occupied_or_vacant == ['Occupied', 'Vacant']

        r2d_building_with_households_with_households.create_households(BUILDING_WITH_HOUSEHOLDS_PARAMETERS['Households'])
        r2d_building_with_households_with_households.update_occupancy_status()
        assert r2d_building_with_households_with_households.occupied_or_vacant == ['Occupied', 'Vacant', 'Occupied']

    def test_update_operation_demand(self, r2d_building_with_households_with_households):
        assert r2d_building_with_households_with_households.demand['OperationDemand']['PotableWater'].current_amount == 0

        r2d_building_with_households_with_households.update_operation_demand()
        expected_demand = 3*150 + 4*150
        assert r2d_building_with_households_with_households.demand['OperationDemand']['PotableWater'].current_amount == expected_demand

        r2d_building_with_households_with_households.households = []
        r2d_building_with_households_with_households.update_operation_demand()
        assert r2d_building_with_households_with_households.demand['OperationDemand']['PotableWater'].current_amount == 0

        r2d_building_with_households_with_households.functionality_level = 0.0
        r2d_building_with_households_with_households.update_operation_demand()
        assert r2d_building_with_households_with_households.demand['OperationDemand']['PotableWater'].current_amount == 0

    def test_update_supply_based_on_unmet_demand(self, r2d_building_with_households_with_households):
        r2d_building_with_households_with_households.met_demand_tracker = [{}]
        r2d_building_with_households_with_households.update_supply_based_on_unmet_demand(0.5, 'PotableWater', 0)
        print(r2d_building_with_households_with_households.households[0].time_step_narrative_creator.narrative)
        assert ''.join(r2d_building_with_households_with_households.households[0].time_step_narrative_creator.narrative.split()) == ''.join('  - At your current location, your needs for PotableWater are partially satisfied. '.split())
        assert ''.join(r2d_building_with_households_with_households.households[1].time_step_narrative_creator.narrative.split()) == ''.join('  - At your current location, your needs for PotableWater are partially satisfied. '.split())
        
    def test_update_households_based_on_unmet_demand(self, r2d_building_with_households_with_households):
        # Tested in test_update_supply_based_on_unmet_demand
        assert True

    def test_update_demand_from_households(self, r2d_building_with_households_with_households):
        assert r2d_building_with_households_with_households.demand['OperationDemand']['PotableWater'].current_amount == 0
        r2d_building_with_households_with_households.update_demand_from_households()
        expected_demand = 3*150 + 4*150
        assert r2d_building_with_households_with_households.demand['OperationDemand']['PotableWater'].current_amount == expected_demand

        r2d_building_with_households_with_households.households = []
        r2d_building_with_households_with_households.demand['OperationDemand']['PotableWater'].current_amount = 0
        r2d_building_with_households_with_households.update_demand_from_households()
        assert r2d_building_with_households_with_households.demand['OperationDemand']['PotableWater'].current_amount == 0

    @pytest.mark.skip(reason="Not implemented yet.")
    def test_update_supply_from_households(self, r2d_building_with_households_with_households):
        pass

    def test_component_represents_out_of_town(self, r2d_building_with_households_with_households):
        assert not r2d_building_with_households_with_households.component_represents_out_of_town()
        r2d_building_with_households_with_households.general_information['OccupancyClass'] = 'OutOfTown'
        assert r2d_building_with_households_with_households.component_represents_out_of_town()

    def test_component_represents_friends_house(self, r2d_building_with_households_with_households):
        household = r2d_building_with_households_with_households.households[0]
        assert not r2d_building_with_households_with_households.component_represents_friends_house(household)
        household.friends = [35]
        assert not r2d_building_with_households_with_households.component_represents_friends_house(household)
        household.friends = [30]
        assert r2d_building_with_households_with_households.component_represents_friends_house(household)

    def test_component_represents_home(self, r2d_building_with_households_with_households):
        household = r2d_building_with_households_with_households.households[0]
        assert r2d_building_with_households_with_households.component_represents_home(household)
        household.home_id = '31'
        assert not r2d_building_with_households_with_households.component_represents_home(household)

    def test_update_households(self, r2d_building_with_households_with_households, built_environment):
        built_environment.components.append(r2d_building_with_households_with_households)
        r2d_building_with_households_with_households.map_buildings_to_households(built_environment)
        assert r2d_building_with_households_with_households.households[0].staying_at == []
        assert r2d_building_with_households_with_households.households[1].staying_at == []
        assert r2d_building_with_households_with_households.households[0].moved_at_time_step == False
        assert r2d_building_with_households_with_households.households[1].moved_at_time_step == False
        assert r2d_building_with_households_with_households.households[0].time_step_narrative_creator.narrative == ''
        assert r2d_building_with_households_with_households.households[1].time_step_narrative_creator.narrative == ''

        r2d_building_with_households_with_households.update_households(0, [30])
        assert r2d_building_with_households_with_households.households[0].staying_at == ['Home']
        assert r2d_building_with_households_with_households.households[1].staying_at == ['Home']
        assert r2d_building_with_households_with_households.households[0].moved_at_time_step == False
        assert r2d_building_with_households_with_households.households[1].moved_at_time_step == False

        another_building = built_environment.components[3]
        another_building.households = [r2d_building_with_households_with_households.households[0]]
        another_building.update_households(1, [30])
        assert another_building.households[0].staying_at == ['Home', 'Friend']
        assert another_building.households[0].moved_at_time_step == False

    def test_households_decide(self, r2d_building_with_households_with_households, built_environment):
        built_environment.components.append(r2d_building_with_households_with_households)
        r2d_building_with_households_with_households.map_buildings_to_households(built_environment)
        assert r2d_building_with_households_with_households.households[0].decisions == []
        assert r2d_building_with_households_with_households.households[1].decisions == []

        r2d_building_with_households_with_households.update_households(0, [30])
        r2d_building_with_households_with_households.households_decide()
        assert r2d_building_with_households_with_households.households[0].decisions == ['StayAtHome']
        assert r2d_building_with_households_with_households.households[1].decisions == ['StayAtHome']

        r2d_building_with_households_with_households.households_decide()
        assert r2d_building_with_households_with_households.households[0].decisions == ['StayAtHome', 'StayAtHome']
        assert r2d_building_with_households_with_households.households[1].decisions == ['StayAtHome', 'StayAtHome']

    def test_households_move(self, r2d_building_with_households_with_households, built_environment):
        for component in built_environment.components[1:]:
            component.households = []
        built_environment.components.append(r2d_building_with_households_with_households)
        r2d_building_with_households_with_households.map_buildings_to_households(built_environment)
        r2d_building_with_households_with_households.households[0].decisions = ['StayAtHome']
        r2d_building_with_households_with_households.households[1].decisions = ['StayAtHome']
        r2d_building_with_households_with_households.update_households(0, [30])
        r2d_building_with_households_with_households.households_move()

        households_in_components = [0, 0, 0, 0, 2]
        for households_in_component, component in zip(households_in_components, built_environment.components[1:]):
            assert len(component.households) == households_in_component

        r2d_building_with_households_with_households.households[0].decisions = ['StayAtHome', 'LeaveTown']
        r2d_building_with_households_with_households.households[1].decisions = ['StayAtHome', 'LeaveTown']
        r2d_building_with_households_with_households.update_households(1, [30])
        r2d_building_with_households_with_households.households_move()

        households_in_components = [2, 0, 0, 0, 0]
        for households_in_component, component in zip(households_in_components, built_environment.components[1:]):
            assert len(component.households) == households_in_component

        built_environment.components[1].update_households(2, [30])
        built_environment.components[1].households[0].decisions = ['StayAtHome', 'LeaveTown', 'MoveToFriend_1']
        built_environment.components[1].households[1].decisions = ['StayAtHome', 'LeaveTown', 'MoveToFriend_1']
        built_environment.components[1].households_move()

        households_in_components = [0, 0, 1, 1, 0]
        for households_in_component, component in zip(households_in_components, built_environment.components[1:]):
            assert len(component.households) == households_in_component      
    

