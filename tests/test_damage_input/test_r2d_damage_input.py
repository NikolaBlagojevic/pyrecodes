import pytest
from pyrecodes.utilities import read_json_file
from pyrecodes.damage_input.r2d_damage_input import R2DDamageInput
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.component.infrastructure_interface import InfrastructureInterface
from pyrecodes.component.r2d_component import R2DPipe
from pyrecodes.component_recovery_model.no_recovery_activity_model import NoRecoveryActivityModel
from pyrecodes.component_recovery_model.component_level_recovery_activities_model import ComponentLevelRecoveryActivitiesModel
from pyrecodes import main

class TestR2DDamageInput:

    MAIN_FILE = './tests/test_inputs/test_inputs_ThreeLocalitiesCommunityREWET_Main.json'
    DAMAGE_INPUT_PARAMETERS = {"DamageFile": "./tests/test_inputs/test_inputs_ThreeLocalitiesCommunity_0.json",
                            "DistributionModelDamage": [
                                "PotableWater"
                            ],
                            }

    @pytest.fixture
    def system(self):
        input_dict = read_json_file(self.MAIN_FILE)
        return main.create_system(input_dict)

    @pytest.fixture
    def damage_input(self, system):
        return R2DDamageInput(system.system_creator.get_damage_input_parameters(), system)

    def test_set_initial_component_damage_level_no_interfaces(self, system, damage_input):
        damage_input.set_initial_component_damage_level()
        system.time_step = 1
        system.update()
        target_damage_levels = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0]
        for i, component in enumerate(system.components):
            assert component.get_damage_level() == target_damage_levels[i]

    def test_set_damage_in_the_distribution_model(self, damage_input):
        damage_input.set_damage_in_the_distribution_model()
        target_damage_information = [{'Location': [], 'Type': []}, {'Location': [], 'Type': []}, {'Location': [], 'Type': []}, {'Location': [0.25], 'Type': ['break']}]
        i = 0
        for component in damage_input.system.components:
            if isinstance(component, R2DPipe):
                assert component.damage_information == target_damage_information[i]
                i += 1

    def test_configure_damage_file(self, damage_input):
        pass

    def test_component_is_damaged(self, damage_input):
        component = StandardiReCoDeSComponent()
        component.recovery_model = NoRecoveryActivityModel({'Parameters': {}, 'DamageFunctionalityRelation': {}})
        assert damage_input.component_is_damaged(component) == False
        component.recovery_model = ComponentLevelRecoveryActivitiesModel({'Parameters': {}, 'DamageFunctionalityRelation': {}})
        assert damage_input.component_is_damaged(component) == False

        component = R2DPipe()
        assert damage_input.component_is_damaged(component) == True
    
    def test_component_is_interface(self, damage_input):
        component = StandardiReCoDeSComponent()
        assert damage_input.component_is_interface(component) == False
        component = InfrastructureInterface()
        assert damage_input.component_is_interface(component) == True
