import pytest
from pyrecodes import main
from pyrecodes.utilities import read_json_file
from pyrecodes.resource_distribution_model.utility_distribution_model_constructor import UtilityDistributionModelConstructor
from pyrecodes.distribution_priority.component_type_priority import ComponentTypePriority
from pyrecodes.resource_distribution_model.single_resource_system_matrix_creator import SingleResourceSystemMatrixCreator

MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

DUMMY_PRIORITY = {"ClassName": "ComponentTypePriority",
                  "FileName": "component_type_priority",
                    "Parameters": [
                        [
                            "BaseTransceiverStation_1",
                            "OperationDemand"
                        ],
                        [
                            "ElectricPowerPlant",
                            "OperationDemand"
                        ],
                        [
                            "CoolingWaterFacility",
                            "OperationDemand"
                        ],
                        [
                            "BuildingStockUnit",
                            "OperationDemand"
                        ]
                    ]}

class TestUtilityDistributionModelConstructor:    
    
    @pytest.fixture
    def system(self):
        input_dict = read_json_file(MAIN_FILE)
        return main.create_system(input_dict)

    @pytest.fixture
    def distribution_model_constructor(self):
        return UtilityDistributionModelConstructor()
    
    @pytest.fixture
    def distribution_model(self, system):
        distribution_model = {resource_name: resource_parameters['DistributionModel'] for
                               resource_name, resource_parameters in system.resources.items() if resource_name == 'ElectricPower'}
        return distribution_model  
       
    def test_set_components(self, distribution_model, distribution_model_constructor, system):
        component_subset = system.components[:10]
        distribution_model_constructor.set_components(component_subset, distribution_model['ElectricPower'])
        assert distribution_model['ElectricPower'].components == component_subset

    def test_set_resource_name(self, distribution_model, distribution_model_constructor):
        distribution_model_constructor.set_resource_name('DummyResource', distribution_model['ElectricPower'])
        assert distribution_model['ElectricPower'].resource_name == 'DummyResource'

    def test_set_priority_model(self, distribution_model, distribution_model_constructor, system):
        distribution_model_constructor.set_priority_model('ElectricPower', DUMMY_PRIORITY, system.components, distribution_model['ElectricPower'])
        assert isinstance(distribution_model['ElectricPower'].priority, ComponentTypePriority)
    
    def test_set_system_matrix(self, distribution_model, distribution_model_constructor, system):
        distribution_model_constructor.set_system_matrix(system.components, 'ElectricPower', distribution_model['ElectricPower'])
        assert isinstance(distribution_model['ElectricPower'].system_matrix, SingleResourceSystemMatrixCreator)
