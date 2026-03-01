import pytest
import math
from pyrecodes.utilities import read_json_file
from pyrecodes import main
from pyrecodes.damage_input.file_damage_input import FileDamageInput

FOLDER_NAME = './tests/test_inputs'
MAIN_FILE = 'test_inputs_ThreeLocalitiesCommunity_Main.json'
DAMAGE_FILE = 'test_damage_input_file.txt'

class TestFileDamageInput:

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(f'{FOLDER_NAME}/{MAIN_FILE}')
        system = main.create_system(FOLDER_NAME, input_dict)
        damage_input = FileDamageInput(f'{FOLDER_NAME}/{DAMAGE_FILE}', system)
        system.damage_input = damage_input
        return system

    @pytest.fixture
    def damage_input(self, system):
        return FileDamageInput(f'{FOLDER_NAME}/{DAMAGE_FILE}', system)
    
    def test_read_initial_damage_file(self, damage_input):
        damage_input.read_initial_damage_file(f'{FOLDER_NAME}/{DAMAGE_FILE}')
        assert damage_input.damage_levels == [0.0, 0.1, 0.2, 0.3, 0.4]

    def test_set_initial_damage(self, system):
        system.set_initial_damage()
        target_damage_levels = [0.0, 0.1, 0.2, 0.3, 0.4]
        for target_damage_level, component in zip(target_damage_levels, system.components):
            assert math.isclose(component.get_damage_level(), target_damage_level)

    def test_read_initial_damage_file_nonexistent_file(self, damage_input):
        with pytest.raises(FileNotFoundError):
            damage_input.read_initial_damage_file('nonexistent_file.txt')

    def test_set_initial_damage_more_levels_than_components(self, system):
        system.damage_input.damage_levels = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.5]
        system.set_initial_damage()
        target_damage_levels = [0.1, 0.2, 0.3, 0.4, 0.5]
        for target, component in zip(target_damage_levels, system.components):
            assert math.isclose(component.get_damage_level(), target)