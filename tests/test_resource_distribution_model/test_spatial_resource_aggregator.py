import pytest
from pyrecodes.utilities import read_json_file
from pyrecodes.resource_distribution_model.spatial_resource_aggregator import SpatialResourceAggregator
from pyrecodes import main

FOLDER_NAME = './tests/test_inputs'
MAIN_FILE = 'test_inputs_ThreeLocalitiesCommunity_Main.json'


class TestSpatialResourceAggregator:

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(f'{FOLDER_NAME}/{MAIN_FILE}')
        return main.create_system(FOLDER_NAME, input_dict)

    @pytest.fixture
    def spatial_resource_aggregator(self):
        return SpatialResourceAggregator()
    
    def test_aggregate_per_locality(self, spatial_resource_aggregator, system):
        resource_per_locality = spatial_resource_aggregator.aggregate_per_locality(system.components, 'Communication', supply_or_demand='supply', supply_or_demand_type='Supply')
        assert resource_per_locality == {1: 1.0, 2: 0.0, 3: 2.0}
        resource_per_locality = spatial_resource_aggregator.aggregate_per_locality(system.components, 'Communication', locality_ids=[1, 2], supply_or_demand='supply', supply_or_demand_type='Supply')
        assert resource_per_locality == {1: 1.0, 2: 0.0}

        resource_per_locality = spatial_resource_aggregator.aggregate_per_locality(system.components, 'ElectricPower')
        assert resource_per_locality == {1: 1.0, 2: 1.0, 3: 2.0}

        resource_per_locality = spatial_resource_aggregator.aggregate_per_locality(system.components, 'Shelter')
        assert resource_per_locality == {1: 0.0, 2: 0.0, 3: 0.0}

    def test_aggregate_total(self, spatial_resource_aggregator, system):
        total_resource = spatial_resource_aggregator.aggregate_total(system.components, 'Communication')
        assert total_resource == 3.0

    def test_aggregate_per_locality_empty_components(self, spatial_resource_aggregator):
        result = spatial_resource_aggregator.aggregate_per_locality([], 'Communication')
        assert result == {}

    def test_aggregate_per_locality_nonexistent_resource(self, spatial_resource_aggregator, system):
        result = spatial_resource_aggregator.aggregate_per_locality(system.components, 'NonExistentResource')
        assert all(v == 0.0 for v in result.values())

    def test_aggregate_total_supply(self, spatial_resource_aggregator, system):
        from pyrecodes.component.component import SupplyOrDemand
        from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
        total = spatial_resource_aggregator.aggregate_total(
            system.components, 'Communication',
            supply_or_demand=SupplyOrDemand.SUPPLY.value,
            supply_or_demand_type=StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value
        )
        assert total == 3.0

    def test_aggregate_total_empty_components(self, spatial_resource_aggregator):
        total = spatial_resource_aggregator.aggregate_total([], 'Communication')
        assert total == 0


