import pytest
import math
from pyrecodes.utilities import read_json_file
from pyrecodes.damage_input import ListDamageInput
from pyrecodes import main

MAIN_FILE = 'test_inputs_ThreeLocalitiesCommunity_Main.json'    
FOLDER_NAME = './tests/test_inputs'

class TestListDamageInput():

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(f'{FOLDER_NAME}/{MAIN_FILE}')
        return main.create_system(FOLDER_NAME, input_dict)

    @pytest.fixture
    def damage_input(self, system):
        return ListDamageInput(system.system_creator.get_damage_input_parameters(), system)

    def test_damage_levels(self, damage_input):
        assert damage_input.damage_levels == [0.0, 0.4, 0.0, 0.0, 0.4, 0.0, 0.0, 0.4, 0.4, 0.0, 0.0]

    def test_set_initial_damage(self, system):
        system.set_initial_damage()
        target_damage_levels = [0.0, 0.4, 0.0, 0.0, 0.4, 0.0, 0.0, 0.4, 0.4, 0.0, 0.0]
        for target_damage_level, component in zip(target_damage_levels, system.components):
            assert component.get_damage_level() == target_damage_level
    
    def test_set_initial_damage_fewer_levels(self, system):
        system.damage_input.damage_levels = [0.1, 0.4, 0.3, 0.5, 0.4]
        system.set_initial_damage()
        target_damage_levels = [0.1, 0.4, 0.3, 0.5, 0.4, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        for target_damage_level, component in zip(target_damage_levels, system.components):
            assert math.isclose(component.get_damage_level(), target_damage_level)

    def test_init(self, damage_input, system):
        assert damage_input.system == system
        assert damage_input.damage_levels == [0.0, 0.4, 0.0, 0.0, 0.4, 0.0, 0.0, 0.4, 0.4, 0.0, 0.0]

    def test_set_initial_damage_more_levels_than_components(self, system):
        extra_levels = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.5, 0.3, 0.2]
        system.damage_input.damage_levels = extra_levels
        system.set_initial_damage()
        target_damage_levels = extra_levels[:len(system.components)]
        for target, component in zip(target_damage_levels, system.components):
            assert math.isclose(component.get_damage_level(), target)