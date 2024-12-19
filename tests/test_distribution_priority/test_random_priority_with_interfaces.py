import pytest
import copy
from pyrecodes.utilities import read_json_file
from pyrecodes import main
from pyrecodes.system.system import System
from pyrecodes.distribution_priority.random_priority_with_prioritized_interfaces import RandomPriorityWithPrioritizedInterfaces
from pyrecodes.distribution_priority.distribution_priority import DistributionPriority
from pyrecodes.component.infrastructure_interface import InfrastructureInterface

MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

class TestRandomPriorityWithPrioritizedInterfaces():

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(MAIN_FILE)
        system = main.create_system(input_dict)
        interface_component = InfrastructureInterface()
        system.components.append(interface_component)
        return system
    
    @pytest.fixture
    def distribution_priority(self, system: System):
        return RandomPriorityWithPrioritizedInterfaces(resource_name='ElectricPower', 
                                    parameters={'Seed': 0, 'DemandType': ['OperationDemand']},
                                    components=system.components)
    
    def test_set_distribution_priority(self, distribution_priority: DistributionPriority):
        assert distribution_priority.get_component_priorities()[0][0] == 0
        assert distribution_priority.get_component_priorities()[0][1] == 11
        assert len(distribution_priority.get_component_priorities()[0][2:]) == len(distribution_priority.components) - 2

        current_priority = copy.deepcopy(distribution_priority.get_component_priorities()[0])

        distribution_priority.set_distribution_priority(parameters={'Seed': 1, 'DemandType': ['OperationDemand']})
        assert current_priority[0] == distribution_priority.get_component_priorities()[0][0]
        assert current_priority[1] == distribution_priority.get_component_priorities()[0][1]
        assert current_priority[2:] != distribution_priority.get_component_priorities()[0][2:]
       
        distribution_priority.set_distribution_priority(parameters={'Seed': 0, 'DemandType': ['OperationDemand']})
        assert current_priority == distribution_priority.get_component_priorities()[0]

    def test_get_infrastructure_interface_id(self, distribution_priority):
        interface_ids, remaining_component_ids = distribution_priority.get_infrastructure_interface_id(list(range(len(distribution_priority.components))))
        assert interface_ids == [11]
        assert len(remaining_component_ids) == len(distribution_priority.components) - 1
        assert 11 not in remaining_component_ids
