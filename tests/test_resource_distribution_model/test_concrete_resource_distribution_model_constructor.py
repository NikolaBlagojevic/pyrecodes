import pytest
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.resource_distribution_model.concrete_resource_distribution_model_constructor import ConcreteResourceDistributionModelConstructor

MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

class TestConcreteResourceDistributionModelConstructor:    

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(MAIN_FILE)
        return main.create_system(input_dict)

    @pytest.fixture
    def distribution_model_constructor(self):
        return ConcreteResourceDistributionModelConstructor()
    
    @pytest.fixture
    def distribution_model(self, system):
        distribution_model = {resource_name: resource_parameters['DistributionModel'] for
                               resource_name, resource_parameters in system.resources.items() if resource_name == 'SuperTransferService'}
        return distribution_model
    
    def test_set_components(self, distribution_model, distribution_model_constructor, system):
        component_subset = system.components[:10]
        distribution_model_constructor.set_components(component_subset, distribution_model['SuperTransferService'])
        assert distribution_model['SuperTransferService'].components == component_subset
    
    def test_set_resource_name(self, distribution_model, distribution_model_constructor):
        distribution_model_constructor.set_resource_name('DummyResource', distribution_model['SuperTransferService'])
        assert distribution_model['SuperTransferService'].resource_name == 'DummyResource'

    def test_set_time_stepping_rules(self, distribution_model, distribution_model_constructor):
        distribution_model_constructor.set_time_stepping_rules([{'start': 0, 'end': 10, 'step': 1}], distribution_model['SuperTransferService'])
        assert distribution_model['SuperTransferService'].distribution_time_steps == list(range(0, 10, 1))