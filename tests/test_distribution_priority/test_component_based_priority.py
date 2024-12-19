import pytest
from pyrecodes.utilities import read_json_file
from pyrecodes import main
from pyrecodes.system.system import System
from pyrecodes.distribution_priority.component_based_priority import ComponentBasedPriority

MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'

class TestComponentBasedDistributionPriority():

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(MAIN_FILE)
        return main.create_system(input_dict)
    
    @pytest.fixture
    def distribution_priority(self, system: System):
        return ComponentBasedPriority(resource_name='Resource 1', 
                                    parameters=[
                                                ["ElectricPowerPlant", ["Locality 1"], "OperationDemand"],
                                                ["BaseTransceiverStation_1", ["Locality 1"], "OperationDemand"],
                                                ["CoolingWaterFacility", ["Locality 2"], "OperationDemand"],
                                                ["BaseTransceiverStation_2", ["Locality 3"], "OperationDemand"],
                                                ["BuildingStockUnit", ["Locality 3"], "OperationDemand"]
                                                            ],
                                    components=system.components)


    def test_component_not_already_in_priority_list(self, distribution_priority):
        component = distribution_priority.components[0]
        assert not(distribution_priority.component_not_already_in_priority_list(None))
        assert distribution_priority.component_not_already_in_priority_list(component)        

    def test_find_component_position(self, distribution_priority):
        target_components = [['BaseTransceiverStation_1', ['Locality 1']], ['ElectricPowerPlant', ['Locality 1']],
                             ['BuildingStockUnit', ['Locality 3']], ['SuperLink', ['Locality 1', 'Locality 2']]]
        target_positions = [1, 0, 8, 2]
        for target_component, target_position in zip(target_components, target_positions):
            component_position, temp_components = distribution_priority.find_component_position(target_component[0],
                                                                                                target_component[1],
                                                                                                distribution_priority.components)
            assert component_position == target_position

    def test_find_component_position_error(self, system: System):
        distribution_priority = system.resources['ElectricPower']['DistributionModel'].priority
        with pytest.raises(ValueError):
            distribution_priority.find_component_position('ElectricPowerPlant', ['Locality 3'], system.components)

    def test_set_distribution_priority(self, system: System):
        target_priorities = [[0, 1, 4, 7, 8], [4, 0, 1, 7, 8], [1, 7, 0, 4, 8]]
        for target_priority, resource_parameters in zip(target_priorities, list(system.resources.values())[1:]):
            component_positions, demand_types = resource_parameters[
                'DistributionModel'].priority.get_component_priorities()
            assert target_priority == component_positions
            assert all([demand_type == 'OperationDemand' for demand_type in demand_types])
