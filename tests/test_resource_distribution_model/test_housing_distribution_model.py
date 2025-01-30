import pytest
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.resource_distribution_model.housing_distribution_model import HousingDistributionModel

MAIN_FILE = './tests/test_inputs/test_inputs_Alameda_Main.json'
RESOURCE_NAME = 'Shelter'
RESOURCE_PARAMETERS = {}

class TestHousingDistributionModel:

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(MAIN_FILE)
        return main.create_system(input_dict)

    @pytest.fixture
    def housing_distribution_model(self, system):
        return HousingDistributionModel(RESOURCE_NAME, RESOURCE_PARAMETERS, system.components)
    
    def test_init(self, housing_distribution_model, system):
        assert housing_distribution_model.resource_name == RESOURCE_NAME
        assert housing_distribution_model.distribution_time_steps == []
        assert len(housing_distribution_model.components) == len(system.components)

    def test_distribute(self, housing_distribution_model, system):
        housing_distribution_model.distribute(time_step=1)
        assert housing_distribution_model.get_total_supply(scope='All') == 28.0
        assert housing_distribution_model.get_total_demand(scope='All') == 28.0
        assert housing_distribution_model.get_total_consumption(scope='All') == 28.0

        system.components[3].set_initial_damage_level(0.5)
        system.components[3].update(time_step=1)
        housing_distribution_model.distribute(time_step=1)
        assert housing_distribution_model.get_total_supply(scope='All') == 25.0
        assert housing_distribution_model.get_total_demand(scope='All') == 28.0
        assert housing_distribution_model.get_total_consumption(scope='All') == 25.0

    def test_distribute_housing_within_component(self, housing_distribution_model, system):
        component = system.components[1]
        housing_distribution_model.distribute_housing_within_component(component)
        assert component.get_current_resource_amount('supply', 'Supply', RESOURCE_NAME) == 10.0

        component.set_initial_damage_level(0.5)
        component.update(time_step=1)
        housing_distribution_model.distribute_housing_within_component(component)
        assert component.get_current_resource_amount('supply', 'Supply', RESOURCE_NAME) == 0.0

    def test_get_total_supply(self, housing_distribution_model, system):
        assert housing_distribution_model.get_total_supply(scope='All') == 28.0

        system.components[1].set_initial_damage_level(0.5)
        system.components[1].update(time_step=1)
        assert housing_distribution_model.get_total_supply(scope='All') == 18.0

    def test_get_total_demand(self, housing_distribution_model, system):
        assert housing_distribution_model.get_total_demand(scope='All') == 28.0

        system.components[1].set_initial_damage_level(0.5)
        system.components[1].update(time_step=1)
        assert housing_distribution_model.get_total_demand(scope='All') == 28.0

    def test_get_total_consumption(self, housing_distribution_model, system):
        assert housing_distribution_model.get_total_consumption(scope='All') == 28.0

        system.components[1].set_initial_damage_level(0.5)
        system.components[1].update(time_step=1)
        assert housing_distribution_model.get_total_consumption(scope='All') == 18.0

        