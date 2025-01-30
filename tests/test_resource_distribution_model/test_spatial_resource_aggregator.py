import pytest
from pyrecodes.utilities import read_json_file
from pyrecodes.resource_distribution_model.spatial_resource_aggregator import SpatialResourceAggregator
from pyrecodes import main

MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'


class TestSpatialResourceAggregator:

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(MAIN_FILE)
        return main.create_system(input_dict)

    @pytest.fixture
    def spatial_resource_aggregator(self):
        return SpatialResourceAggregator()
    
    def test_aggregate_per_locality(self, spatial_resource_aggregator, system):
        resource_per_locality = spatial_resource_aggregator.aggregate_per_locality(system.components, 'Communication', 'supply', 'Supply')
        assert resource_per_locality == {1: 1.0, 2: 0.0, 3: 2.0}

        resource_per_locality = spatial_resource_aggregator.aggregate_per_locality(system.components, 'ElectricPower')
        assert resource_per_locality == {1: 1.0, 2: 1.0, 3: 2.0}

        resource_per_locality = spatial_resource_aggregator.aggregate_per_locality(system.components, 'Shelter')
        assert resource_per_locality == {1: 0.0, 2: 0.0, 3: 0.0}

    def test_aggregate_total(self, spatial_resource_aggregator, system):
        total_resource = spatial_resource_aggregator.aggregate_total(system.components, 'Communication')
        assert total_resource == 3.0


    
