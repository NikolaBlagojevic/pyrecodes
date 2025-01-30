import pytest
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.resource_distribution_model.residual_demand_traffic_distribution_model_constructor import ResidualDemandTrafficDistributionModelConstructor
from pyrecodes.resource_distribution_model.residual_demand_traffic_distribution_model import ResidualDemandTrafficDistributionModel
from tests.test_resource_distribution_model.test_resource_distribution_model_inputs import MAIN_FILE_RESIDUAL_DEMAND, RESOURCE_NAME_RESIDUAL_DEMAND, RESOURCE_PARAMETERS_RESIDUAL_DEMAND, INITIAL_R2D_DICT_RESIDUAL_DEMAND
from residual_demand_API.transportation import pyrecodes_residual_demand

class TestResidualDemandTrafficDistributionModelConstructor:

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
    
    def test_construct(self, residual_demand_traffic_distribution_model_constructor, residual_demand_traffic_distribution_model):
        residual_demand_traffic_distribution_model_constructor.construct(RESOURCE_NAME_RESIDUAL_DEMAND, RESOURCE_PARAMETERS_RESIDUAL_DEMAND, residual_demand_traffic_distribution_model.components, residual_demand_traffic_distribution_model)
        assert isinstance(residual_demand_traffic_distribution_model.flow_simulator, pyrecodes_residual_demand)
        assert residual_demand_traffic_distribution_model.TRIP_CUTOFF_THRESHOLD == RESOURCE_PARAMETERS_RESIDUAL_DEMAND['TripCutoffThreshold']
        assert residual_demand_traffic_distribution_model_constructor.r2d_dict == INITIAL_R2D_DICT_RESIDUAL_DEMAND
