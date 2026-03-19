import pytest
from pyrecodes.household.household_gpt import TimeStepNarrativeCreator
from pyrecodes.household.household_gpt_base import LLM
from pyrecodes.component.r2d_building_with_households import R2DBuildingWithHouseholds
from pyrecodes import main

BUILT_ENVIRONMENT_FILENAME = "test_inputs_SmallAlamedaWithHouseholds_Main.json"
BUILT_ENVIRONMENT_FOLDERNAME = "./tests/test_inputs" # not sure if we need this, but if we do, we can use it to read the built environment in the test file instead of hardcoding the filename there

class TestTimeStepNarrativeCreator:

    @pytest.fixture
    def prompts(self):
        return main.read_json_file('./pyrecodes/household/household_gpt_prompts.json')
    
    @pytest.fixture
    def narrative_creator(self, prompts):
        return TimeStepNarrativeCreator(prompts)

    @pytest.fixture
    def llm(self):
        return LLM(api_key_filename="./openai_api_key.json", temperature=0.0)
    
    @pytest.fixture()
    def built_environment(self):
        input_dict = main.read_json_file(f'{BUILT_ENVIRONMENT_FOLDERNAME}/{BUILT_ENVIRONMENT_FILENAME}')
        system = main.create_system(BUILT_ENVIRONMENT_FOLDERNAME, input_dict)
        system.time_step = 0
        return system
    
    def test_add_to_narrative(self, narrative_creator):
        narrative_creator.add_to_narrative("Test message")
        assert narrative_creator.narrative == "Test message "
        narrative_creator.add_to_narrative("Another message")
        assert narrative_creator.narrative == "Test message Another message "

    def test_format_recovery_info(self, narrative_creator, built_environment):
        component_recovery_model = built_environment.components[4].recovery_model
        prompt = narrative_creator.format_recovery_info(component_recovery_model, "Household Location Building")
        assert prompt == '\n - The Household Location Building has no damage.'

        component_recovery_model.recovery_activities['Repair'].set_level(0.0)
        prompt = narrative_creator.format_recovery_info(component_recovery_model, "Household Location Building")
        assert prompt ==  '\n - The Household Location Building is completely damaged.'

    def test_provide_information_on_building_recovery(self, narrative_creator, built_environment):
        component_recovery_model = built_environment.components[4].recovery_model

        narrative_creator.provide_information_on_building_recovery(component_recovery_model, "Household Location Building")
        assert narrative_creator.narrative == '\n - The Household Location Building has no damage. '
        
        component_recovery_model.recovery_activities['Repair'].set_level(0.0)
        narrative_creator.narrative = ""
        narrative_creator.provide_information_on_building_recovery(component_recovery_model, "Household Location Building")
        assert narrative_creator.narrative == '\n - The Household Location Building is completely damaged. '

    def test_get_building_damage_indicator(self, narrative_creator):
        assert narrative_creator.get_building_damage_indicator(1) == "not"
        assert narrative_creator.get_building_damage_indicator(0.1) == "partially"
        assert narrative_creator.get_building_damage_indicator(0.5) == "partially"
        assert narrative_creator.get_building_damage_indicator(0.8) == "partially"
        assert narrative_creator.get_building_damage_indicator(0) == "completely"
