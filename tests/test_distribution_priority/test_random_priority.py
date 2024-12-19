import pytest
import copy
from pyrecodes.utilities import read_json_file
from pyrecodes import main
from pyrecodes.system.system import System
from pyrecodes.distribution_priority.random_priority import RandomPriority
from pyrecodes.distribution_priority.distribution_priority import DistributionPriority

MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

class TestRandomDistributionPriority():

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(MAIN_FILE)
        return main.create_system(input_dict)
    
    @pytest.fixture
    def distribution_priority(self, system):
        return RandomPriority(resource_name='ElectricPower', 
                                    parameters={'Seed': 0, 'DemandType': ['OperationDemand']},
                                    components=system.components)
    
    def test_set_distribution_priority(self, distribution_priority: DistributionPriority):
        assert distribution_priority.get_component_priorities()[0][0] == 0
        assert len(distribution_priority.get_component_priorities()[0][1:]) == len(distribution_priority.components) - 1

        current_priority = copy.deepcopy(distribution_priority.get_component_priorities()[0])

        distribution_priority.set_distribution_priority(parameters={'Seed': 1, 'DemandType': ['OperationDemand']})
        assert current_priority[0] == distribution_priority.get_component_priorities()[0][0]
        assert current_priority[1:] != distribution_priority.get_component_priorities()[0][1:]
       
        distribution_priority.set_distribution_priority(parameters={'Seed': 0, 'DemandType': ['OperationDemand']})
        assert current_priority == distribution_priority.get_component_priorities()[0]

    def test_get_suppliers_id(self, distribution_priority: DistributionPriority):
        component_ids = list(range(len(distribution_priority.components)))
        assert distribution_priority.get_suppliers_id()[0] == [0]
        component_ids.remove(0)
        assert distribution_priority.get_suppliers_id()[1] == component_ids

        distribution_priority = RandomPriority(resource_name='CoolingWater', 
                                    parameters={'Seed': 0, 'DemandType': ['OperationDemand']},
                                    components=distribution_priority.components)
        component_ids = list(range(len(distribution_priority.components)))
        assert distribution_priority.get_suppliers_id()[0] == [4]
        component_ids.remove(4)
        assert distribution_priority.get_suppliers_id()[1] == component_ids

    def test_randomize_ids_one_component_two_demand_types(self, distribution_priority: DistributionPriority):
        component_ids = [0]
        demand_types = ['RecoveryDemand', 'OperationDemand']
        randomized_ids, randomized_demand_types = distribution_priority.randomize_ids(component_ids, demand_types)
        assert randomized_ids == [0, 0]
        assert 'RecoveryDemand' in randomized_demand_types and 'OperationDemand' in randomized_demand_types
    
    def test_randomize_ids_multiple_components_two_demand_types(self, distribution_priority: DistributionPriority):
        component_ids = [0, 1, 2]
        demand_types = ['RecoveryDemand', 'OperationDemand']
        randomized_ids, randomized_demand_types = distribution_priority.randomize_ids(component_ids, demand_types)
        assert [randomized_ids.count(id) for id in component_ids] == [2, 2, 2]
        assert randomized_demand_types.count('RecoveryDemand') == 3
        assert randomized_demand_types.count('OperationDemand') == 3