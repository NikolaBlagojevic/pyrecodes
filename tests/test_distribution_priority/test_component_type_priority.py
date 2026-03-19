import pytest
from pyrecodes.distribution_priority.component_type_priority import ComponentTypePriority
from pyrecodes.distribution_priority.distribution_priority import DistributionPriority
from tests.conftest import make_system

class TestComponentTypePriority:

    @pytest.fixture
    def system(self, three_localities_system_template):
        return make_system(three_localities_system_template)
    
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

    def test_set_distribution_priority_empty_parameters(self, system):
        dp = ComponentTypePriority('Resource 1', [], system.components)
        assert dp.get_component_priorities() == ([], [])

    def test_set_distribution_priority_recovery_demand(self, distribution_priority: DistributionPriority):
        distribution_priority.set_distribution_priority(
            [['ElectricPowerPlant', 'RecoveryDemand']]
        )
        ids, demand_types = distribution_priority.get_component_priorities()
        assert ids == [0]
        assert demand_types == ['RecoveryDemand']
