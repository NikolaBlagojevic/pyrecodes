import pytest
from pyrecodes.utilities import read_json_file
from pyrecodes import main
from pyrecodes.distribution_priority.supplier_only_priority import SupplierOnlyPriority
from pyrecodes.distribution_priority.distribution_priority import DistributionPriority

MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

class TestSupplierOnlyPriority:

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(MAIN_FILE)
        return main.create_system(input_dict)
    
    @pytest.fixture
    def distribution_priority(self, system):
        return SupplierOnlyPriority(resource_name='Resource 1', 
                                    parameters=[['ElectricPowerPlant', 'OperationDemand'], 
                                                ['CoolingWaterFacility', 'OperationDemand'], 
                                                ['BuildingStockUnit', 'OperationDemand']],
                                    components=system.components)
    
    def test_set_distribution_priority(self, system):
        distribution_priority = SupplierOnlyPriority(resource_name='ElectricPower', 
                                    parameters=[],
                                    components=system.components)
        assert distribution_priority.get_component_priorities() == ([0], ['OperationDemand'])

        distribution_priority = SupplierOnlyPriority(resource_name='DummyResource', 
                                    parameters=[],
                                    components=system.components)
        assert distribution_priority.get_component_priorities() == ([], [])

        distribution_priority = SupplierOnlyPriority(resource_name='Communication', 
                                    parameters=[],
                                    components=system.components)
        assert distribution_priority.get_component_priorities() == ([1, 7], ['OperationDemand', 'OperationDemand'])

