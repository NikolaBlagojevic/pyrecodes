import pytest
from pyrecodes.utilities import read_json_file
from pyrecodes import main
from pyrecodes.distribution_priority.component_type_priority import ComponentTypePriority
from pyrecodes.distribution_priority.distribution_priority import DistributionPriority

MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

class TestComponentTypePriority:

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(MAIN_FILE)
        return main.create_system(input_dict)
    
    @pytest.fixture
    def distribution_priority(self, system):
        return ComponentTypePriority(resource_name='Resource 1', 
                                    parameters=[['ElectricPowerPlant', 'OperationDemand'], 
                                                ['CoolingWaterFacility', 'OperationDemand'], 
                                                ['BuildingStockUnit', 'OperationDemand']],
                                    components=system.components)
    
    def test_categorize_components_based_on_type(self, distribution_priority: DistributionPriority):
        categorized_components_dict = distribution_priority.categorize_components_based_on_type()
        assert categorized_components_dict['ElectricPowerPlant'] == [0]
        assert categorized_components_dict['BaseTransceiverStation_1'] == [1]        
        assert categorized_components_dict['SuperLink'] == [2, 3, 5, 6, 9, 10]
        assert categorized_components_dict['CoolingWaterFacility'] == [4]
        assert categorized_components_dict['BaseTransceiverStation_2'] == [7]
        assert categorized_components_dict['BuildingStockUnit'] == [8]
    
    def test_set_distribution_priority(self, distribution_priority: DistributionPriority):
        assert distribution_priority.get_component_priorities() == ([0, 4, 8], ['OperationDemand', 'OperationDemand', 'OperationDemand'])
