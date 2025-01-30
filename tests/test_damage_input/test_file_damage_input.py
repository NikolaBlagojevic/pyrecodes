import pytest
import math
from pyrecodes.utilities import read_json_file
from pyrecodes import main
from pyrecodes.damage_input.file_damage_input import FileDamageInput

class TestFileDamageInput:

    MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'
    DAMAGE_FILE = './tests/test_inputs/test_damage_input_file.txt'

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(self.MAIN_FILE)
        system = main.create_system(input_dict)
        damage_input = FileDamageInput(self.DAMAGE_FILE, system)
        system.damage_input = damage_input
        return system

    @pytest.fixture
    def damage_input(self, system):
        return FileDamageInput(self.DAMAGE_FILE, system)
    
    def test_read_initial_damage_file(self, damage_input):
        damage_input.read_initial_damage_file(self.DAMAGE_FILE)
        assert damage_input.damage_levels == [0.0, 0.1, 0.2, 0.3, 0.4]

    def test_set_initial_damage(self, system):
        system.set_initial_damage()
        target_damage_levels = [0.0, 0.1, 0.2, 0.3, 0.4]
        for target_damage_level, component in zip(target_damage_levels, system.components):
            assert math.isclose(component.get_damage_level(), target_damage_level)