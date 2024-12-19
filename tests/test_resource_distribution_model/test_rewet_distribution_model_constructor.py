import pytest
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.resource_distribution_model.rewet_distribution_model_constructor import REWETDistributionModelConstructor
from pyrecodes.resource_distribution_model.rewet_distribution_model import REWETDistributionModel
from rewet_API.rewet_pyrecodes_api import REWETPyReCoDes
from test_resource_distribution_model_inputs import MAIN_FILE_REWET, RESOURCE_NAME_REWET, RESOURCE_PARAMETERS_REWET, INITIAL_R2D_DICT_REWET

class TestREWETDistributionModelConstructor:

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
    
    def test_construct(self, rewet_distribution_model_constructor, rewet_distribution_model):
        rewet_distribution_model_constructor.construct(RESOURCE_NAME_REWET, RESOURCE_PARAMETERS_REWET, rewet_distribution_model.components, rewet_distribution_model)
        assert isinstance(rewet_distribution_model.flow_simulator, REWETPyReCoDes)
        assert rewet_distribution_model.r2d_dict == INITIAL_R2D_DICT_REWET

    def test_create_r2d_dict(self, rewet_distribution_model_constructor, system):
        r2d_dict = rewet_distribution_model_constructor.create_r2d_dict(system.components)
        assert r2d_dict == INITIAL_R2D_DICT_REWET