import pytest
import math
from pyrecodes import DamageInput
from pyrecodes import Component
from pyrecodes import main

class TestListDamageInput():

    MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_Main.json'    

    @pytest.fixture
    def system(self):
        input_dict = main.read_file(self.MAIN_FILE)
        return main.create_system(input_dict)

    @pytest.fixture
    def damage_input(self, system):
        return DamageInput.ListDamageInput(system.system_creator.get_damage_input_parameters())

    def test_get_initial_damage(self, damage_input):
        damage_input.get_initial_damage()
        assert damage_input.damage_levels == [0.0, 0.4, 0.0, 0.0, 0.4, 0.0, 0.0, 0.4, 0.4, 0.0, 0.0]

    def test_set_initial_damage(self, system):
        system.set_initial_damage()
        target_damage_levels = [0.0, 0.4, 0.0, 0.0, 0.4, 0.0, 0.0, 0.4, 0.4, 0.0, 0.0]
        for target_damage_level, component in zip(target_damage_levels, system.components):
            assert component.get_damage_level() == target_damage_level
    
    def test_set_initial_damage_fewer_levels(self, system):
        system.damage_input.parameters = [0.1, 0.4, 0.3, 0.5, 0.4]
        system.set_initial_damage()
        target_damage_levels = [0.1, 0.4, 0.3, 0.5, 0.4, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        for target_damage_level, component in zip(target_damage_levels, system.components):
            assert math.isclose(component.get_damage_level(), target_damage_level)

class TestR2DDamageInput:

    MAIN_FILE = './tests/test_inputs/test_inputs_NorthEast_SF_Housing_Interface_Infrastructure_Main.json'

    @pytest.fixture
    def system(self):
        input_dict = main.read_file(self.MAIN_FILE)
        return main.create_system(input_dict)

    @pytest.fixture
    def damage_input(self, system):
        return DamageInput.R2DDamageInput(system.system_creator.get_damage_input_parameters())

    def test_set_initial_damage_buildings(self, system):
        system.set_initial_damage()
        target_damage_states = [1, 0, 3, 1, 0, 3, 1, 0, 0]
        target_damage_levels = [1, 0, 1, 1, 0, 1, 1, 0, 0]
        for i, component in enumerate(system.components[1:10]):
            assert int(component.name[2]) == target_damage_states[i]
            assert component.get_damage_level() == target_damage_levels[i]
    
    def test_set_initial_damage_interfaces(self, system):
        system.set_initial_damage()
        interface_ids = [433, 434, 435, 553, 554, 555, 606, 607, 608, 749, 750, 751]
        for interface_id in interface_ids:
            assert system.components[interface_id].get_damage_level() == 1.0
    
    def test_component_is_damaged(self, damage_input):
        component = Component.StandardiReCoDeSComponent()
        component.name = 'DS0_ResidentialBuilding'
        assert damage_input.component_is_damaged(component) == False
        component.name = 'DS1_ResidentialBuilding'
        assert damage_input.component_is_damaged(component) == True
    
    def test_component_is_interface(self, damage_input):
        component = Component.StandardiReCoDeSComponent()
        assert damage_input.component_is_interface(component) == False
        component = Component.InfrastructureInterface()
        assert damage_input.component_is_interface(component) == True

class TestFileDamageInput:

    DAMAGE_FILE = './tests/test_inputs/dummy_damage_input_file.txt'

    @pytest.fixture
    def damage_input(self):
        return DamageInput.FileDamageInput(self.DAMAGE_FILE)
    
    def test_get_initial_damage(self, damage_input):
        damage_input.get_initial_damage()
        assert damage_input.damage_levels == [0.0, 0.1, 0.2, 0.3, 0.4]

    


