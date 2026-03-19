from pyrecodes.household.household_gpt import HouseholdGPT
from pyrecodes.household.household_gpt_base import LLM
from pyrecodes.component.r2d_building_with_households import R2DBuildingWithHouseholds
from pyrecodes import main
import pytest
import json
from openai import OpenAI

HOUSEHOLD_PARAMETERS = {
    "HouseholdID": "4286_1540",
    "CensusBlock": "Block 2012",
    "CensusTract": "Census Tract 4286",
    "SocioEconomicParameters": {
        "Tenure": "Renter",
        "Income": "High",
        "Occupants": 5,
        "Elderly": 0,
        "Children": 0,
        "EmploymentStatus": 5,
        "ImmigrationStatus": "US born",
        "Home": "3153",
        "Friends": [
            13605,
            10209
        ]
    },
    "ResourceDemand": {
        "PotableWater": 150
    },
    "InformGPTMethod": "None"
}

HOUSEHOLD_GPT_PROMPTS_FILENAME = "./pyrecodes/household/household_gpt_prompts.json"
BUILT_ENVIRONMENT_FILENAME = "test_inputs_SmallAlamedaWithHouseholds_Main.json"
BUILT_ENVIRONMENT_FOLDERNAME = "./tests/test_inputs" 
class TestHouseholdGPT:

    @pytest.fixture
    def household_gpt(self):
        return HouseholdGPT()

    @pytest.fixture()
    def built_environment(self):
        input_dict = main.read_json_file(f'{BUILT_ENVIRONMENT_FOLDERNAME}/{BUILT_ENVIRONMENT_FILENAME}')
        system = main.create_system(BUILT_ENVIRONMENT_FOLDERNAME, input_dict)
        system.time_step = 0
        return system

    def load_household_prompts(self):
        with open(HOUSEHOLD_GPT_PROMPTS_FILENAME, 'r') as file:
            self.prompts = json.load(file)

    def test_init(self, household_gpt):
        assert household_gpt.friends == []
        assert household_gpt.home_id == None # is home_id necessary? we map home component in household.buildings_map
        assert household_gpt.decisions == []
        assert household_gpt.staying_at == []
        assert household_gpt.moved_at_time_step == False
        assert isinstance(household_gpt.prompts, dict)

    def test_set_parameters(self, household_gpt):
        household_gpt.set_parameters(HOUSEHOLD_PARAMETERS)
        assert household_gpt.id == HOUSEHOLD_PARAMETERS["HouseholdID"]
        assert isinstance(household_gpt.llm, LLM)
        assert household_gpt.friends == HOUSEHOLD_PARAMETERS["SocioEconomicParameters"]["Friends"]
        assert household_gpt.home_id == HOUSEHOLD_PARAMETERS["SocioEconomicParameters"]["Home"]
        # Note that we do not check setting the context, the SocioEconomicParameters and ResourceDemand attributes here, as they are tested later

    def test_set_household_id(self, household_gpt):
        household_gpt.set_household_id(HOUSEHOLD_PARAMETERS["HouseholdID"])
        assert household_gpt.id == HOUSEHOLD_PARAMETERS["HouseholdID"]
        household_gpt.set_household_id(5)
        assert household_gpt.id == 5

    def test_create_llm(self, household_gpt):
        # set temperature to zero to have the llm be deterministic
        household_gpt.llm = None  # Reset llm to ensure it is created fresh
        household_gpt.create_llm(api_key_filename="./openai_api_key.json", temperature=0.0, llm_model='GPT')
        assert isinstance(household_gpt.llm, LLM)
        assert household_gpt.llm.chat_history == []
        assert household_gpt.llm.relevant_prompts == []
        assert household_gpt.llm.past_experience == []
        assert isinstance(household_gpt.llm.llm, OpenAI)

    def test_inform_gpt(self, household_gpt):
        # Not sure how to test this method.
        pass

    def test_set_context(self, household_gpt):
        self.load_household_prompts()
        household_gpt.create_llm(api_key_filename="./openai_api_key.json", temperature=0.0, llm_model='GPT')
        assert household_gpt.llm.chat_history == []
        household_gpt.set_context()
        assert household_gpt.llm.chat_history[0] == self.prompts['Initial']
        assert len(household_gpt.llm.chat_history) == 2

    def test_set_socioeconomic_parameters(self, household_gpt):
        household_gpt.create_llm(api_key_filename="./openai_api_key.json", temperature=0.0, llm_model='GPT')
        household_gpt.set_socioeconomic_parameters(HOUSEHOLD_PARAMETERS)
        assert household_gpt.friends == HOUSEHOLD_PARAMETERS["SocioEconomicParameters"]["Friends"]
        assert household_gpt.home_id == HOUSEHOLD_PARAMETERS["SocioEconomicParameters"]["Home"]
        assert household_gpt.llm.chat_history[0] == {
        "role": "developer",
        "content": "Socioeconomic characteristics of your household: \n - You are Renter of the building you live in.\n - Your household income level is High. \n - There are 5 people in your household. Out of those 0 are children and 0 are elderly. \n - 5 of household members are employed. \n - Your immigration status is US born. \n - You have 2 friends in this town.  \n Important: \n - Do not respond to this prompt."
    }

    def test_set_resource_demand_parameters(self, household_gpt):
        household_gpt.create_llm(api_key_filename="./openai_api_key.json", temperature=0.0, llm_model='GPT')
        household_gpt.set_resource_demand_parameters(HOUSEHOLD_PARAMETERS)
        assert household_gpt.llm.chat_history[0] == {
            "role": "developer",
            "content": " # Resource needs of the household \n - These are the average per person resource needs for your household: {'PotableWater': 150}. Take them into account when assessing the needs of the entire household. You might require more or less of each resource at different times after a disaster due to different needs. \n Important: \n - Do not respond to this prompt."
        }

    def test_map_buildings_to_households(self, household_gpt, built_environment):
        household_gpt.set_parameters(HOUSEHOLD_PARAMETERS)
        household_gpt.map_buildings_to_households(built_environment)
        assert isinstance(household_gpt.buildings_map, dict)
        assert household_gpt.buildings_map['Home'][0].general_information['AIM_id'] == HOUSEHOLD_PARAMETERS["SocioEconomicParameters"]["Home"]
        assert isinstance(household_gpt.buildings_map['Home'][0], R2DBuildingWithHouseholds)
        assert len(household_gpt.buildings_map['Friend']) == len(HOUSEHOLD_PARAMETERS["SocioEconomicParameters"]["Friends"])
        for friends_home, friends_id in zip(household_gpt.buildings_map['Friend'], HOUSEHOLD_PARAMETERS["SocioEconomicParameters"]["Friends"]):
            assert int(friends_home.general_information['AIM_id']) == friends_id
            assert isinstance(friends_home, R2DBuildingWithHouseholds)
        assert household_gpt.buildings_map['OutOfTown'][0].name == "NeighboringTown"

    def test_read_literature(self, household_gpt):
        household_gpt.create_llm(api_key_filename="./openai_api_key.json", temperature=0.0, llm_model='GPT')
        household_gpt.read_literature(file_name="./tests/test_inputs/test_literature_summaries.json")
        self.load_household_prompts()
        # remove last part of the prompt that is added to the chat history, as it is not relevant for the test
        assert self.prompts['ReadLiterature']['content'][:20] in household_gpt.llm.chat_history[0]['content']
        assert household_gpt.llm.chat_history[0]['content'].startswith("# Literature on household decision-making \n")
        assert len(household_gpt.llm.chat_history[0]['content']) >= len(self.prompts['ReadLiterature']['content'])
        # not sure how the test the rest of the method, it depends on the literature

    def test_read_ruleset(self, household_gpt):
        self.load_household_prompts()
        household_gpt.create_llm(api_key_filename="./openai_api_key.json", temperature=0.0, llm_model='GPT')
        household_gpt.read_ruleset()
        assert self.prompts['ReadRuleset']['content'] == household_gpt.llm.chat_history[0]['content']

    def test_split_text_into_batches(self, household_gpt):
        text = "A " * 500
        split_text = household_gpt.split_text_into_batches(text, max_words=100)
        for batch in list(split_text):
            assert len(batch.split()) == 100

    def test_prompt_llm(self, household_gpt):
        household_gpt.create_llm(api_key_filename="./openai_api_key.json", temperature=0.0, llm_model='GPT')
        test_prompt = {"role": "user", "content": "just say 'Test.'"}
        response = household_gpt.prompt_llm(test_prompt)
        assert isinstance(response, str)
        assert "Test." in response

    def test_decide(self, household_gpt, built_environment):
        household_gpt.create_llm(api_key_filename="./openai_api_key.json", temperature=0.0, llm_model='GPT')
        household_gpt.set_parameters(HOUSEHOLD_PARAMETERS, temperature=0.0)
        household_gpt.map_buildings_to_households(built_environment)
        for friend_house in household_gpt.buildings_map['Friend']:
            for household in friend_house.households:
                household.staying_at = ['Home']

        household_gpt.update(10, household_gpt.buildings_map['Home'][0], [10, 10])
        household_gpt.decide(household_gpt.buildings_map['Home'][0])
        assert household_gpt.decisions[-1] == household_gpt.OPTIONS.STAY_AT_HOME.value

        household_gpt.llm.past_experience = []
        household_gpt.update(10, household_gpt.buildings_map['OutOfTown'][0], [10, 10])
        household_gpt.decide(household_gpt.buildings_map['OutOfTown'][0])
        assert household_gpt.decisions[-1] == household_gpt.OPTIONS.RETURN_HOME.value

    def test_add_move_to_friend_options(self, household_gpt, built_environment):
        household_gpt.set_parameters(HOUSEHOLD_PARAMETERS)
        household_gpt.map_buildings_to_households(built_environment)

        move_to_friends_options = household_gpt.add_move_to_friend_options(household_gpt.buildings_map['Home'][0])
        assert isinstance(move_to_friends_options, list)
        assert len(move_to_friends_options) == len(HOUSEHOLD_PARAMETERS["SocioEconomicParameters"]["Friends"])
        assert move_to_friends_options == [household_gpt.OPTIONS.MOVE_TO_FRIEND.value.replace('ID', '1'),
                                          household_gpt.OPTIONS.MOVE_TO_FRIEND.value.replace('ID', '2')]

        move_to_friends_options = household_gpt.add_move_to_friend_options(household_gpt.buildings_map['Friend'][0])
        assert len(move_to_friends_options) == len(HOUSEHOLD_PARAMETERS["SocioEconomicParameters"]["Friends"]) - 1
        assert move_to_friends_options == [household_gpt.OPTIONS.MOVE_TO_FRIEND.value.replace('ID', '2')]

        move_to_friends_options = household_gpt.add_move_to_friend_options(household_gpt.buildings_map['Friend'][1])
        assert len(move_to_friends_options) == len(HOUSEHOLD_PARAMETERS["SocioEconomicParameters"]["Friends"]) - 1
        assert move_to_friends_options == [household_gpt.OPTIONS.MOVE_TO_FRIEND.value.replace('ID', '1')]

    def test_get_household_options(self, household_gpt, built_environment):
        household_gpt.set_parameters(HOUSEHOLD_PARAMETERS)
        household_gpt.map_buildings_to_households(built_environment)

        household_gpt.staying_at = ['Friend']
        options = household_gpt.get_household_options(household_gpt.buildings_map['Friend'][0])
        assert options == f"{household_gpt.OPTIONS.LEAVE_TOWN.value}, {household_gpt.OPTIONS.RETURN_HOME.value}, {household_gpt.OPTIONS.STAY_WITH_FRIEND.value.replace('ID', '1')}, {household_gpt.OPTIONS.MOVE_TO_FRIEND.value.replace('ID', '2')}. "

        options = household_gpt.get_household_options(household_gpt.buildings_map['Friend'][1])
        assert options == f"{household_gpt.OPTIONS.LEAVE_TOWN.value}, {household_gpt.OPTIONS.RETURN_HOME.value}, {household_gpt.OPTIONS.STAY_WITH_FRIEND.value.replace('ID', '2')}, {household_gpt.OPTIONS.MOVE_TO_FRIEND.value.replace('ID', '1')}. "

        household_gpt.staying_at = ['OutOfTown']
        options = household_gpt.get_household_options(household_gpt.buildings_map['OutOfTown'][0])
        assert options == f"{household_gpt.OPTIONS.RETURN_HOME.value}, {household_gpt.OPTIONS.STAY_OUT_OF_TOWN.value}, {household_gpt.OPTIONS.MOVE_TO_FRIEND.value.replace('ID', '1')}, {household_gpt.OPTIONS.MOVE_TO_FRIEND.value.replace('ID', '2')}. "

        household_gpt.staying_at = ['Home']
        options = household_gpt.get_household_options(household_gpt.buildings_map['Home'][0])
        assert options == f"{household_gpt.OPTIONS.STAY_AT_HOME.value}, {household_gpt.OPTIONS.LEAVE_TOWN.value}, {household_gpt.OPTIONS.MOVE_TO_FRIEND.value.replace('ID', '1')}, {household_gpt.OPTIONS.MOVE_TO_FRIEND.value.replace('ID', '2')}. "

        household_gpt.staying_at = ['Dummy']
        options = household_gpt.get_household_options(household_gpt.buildings_map['Home'][0])
        assert options == ''

    def test_find_friend_id(self, household_gpt, built_environment):
        household_gpt.set_parameters(HOUSEHOLD_PARAMETERS)
        household_gpt.map_buildings_to_households(built_environment)

        friend_id = household_gpt.find_friend_id(household_gpt.buildings_map['Friend'][0])
        assert friend_id == 1

        friend_id = household_gpt.find_friend_id(household_gpt.buildings_map['Friend'][1])
        assert friend_id == 2

    def test_format_household_options_string(self, household_gpt):
        options = ['Option 1', 'Option 2', 'Option 3']
        formatted_options = household_gpt.format_household_options_string(options)
        assert formatted_options == "Option 1, Option 2, Option 3. "

        options = []
        formatted_options = household_gpt.format_household_options_string(options)
        assert formatted_options == ""

    def test_move(self, household_gpt, built_environment):
        household_gpt.set_parameters(HOUSEHOLD_PARAMETERS)
        household_gpt.map_buildings_to_households(built_environment)

        household_gpt.buildings_map['Home'][0].households = [household_gpt]
        household_gpt.decisions = [household_gpt.OPTIONS.LEAVE_TOWN.value]
        household_gpt.move(household_gpt.buildings_map['Home'][0])
        assert household_gpt not in household_gpt.buildings_map['Home'][0].households
        assert household_gpt in household_gpt.buildings_map['OutOfTown'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][1].households

        household_gpt.decisions = [household_gpt.OPTIONS.LEAVE_TOWN.value]
        household_gpt.moved_at_time_step = False
        household_gpt.move(household_gpt.buildings_map['OutOfTown'][0])
        assert household_gpt not in household_gpt.buildings_map['Home'][0].households
        assert household_gpt in household_gpt.buildings_map['OutOfTown'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][1].households

        household_gpt.decisions = [household_gpt.OPTIONS.LEAVE_TOWN.value]
        household_gpt.moved_at_time_step = False
        household_gpt.move(household_gpt.buildings_map['OutOfTown'][0])
        assert household_gpt not in household_gpt.buildings_map['Home'][0].households
        assert household_gpt in household_gpt.buildings_map['OutOfTown'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][1].households

        household_gpt.decisions = [household_gpt.OPTIONS.MOVE_TO_FRIEND.value.replace('ID', '1')]
        household_gpt.moved_at_time_step = False
        household_gpt.move(household_gpt.buildings_map['OutOfTown'][0])
        assert household_gpt not in household_gpt.buildings_map['Home'][0].households
        assert household_gpt not in household_gpt.buildings_map['OutOfTown'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][1].households
        assert household_gpt in household_gpt.buildings_map['Friend'][0].households

        household_gpt.decisions = [household_gpt.OPTIONS.MOVE_TO_FRIEND.value.replace('ID', '2')]
        household_gpt.moved_at_time_step = False
        household_gpt.move(household_gpt.buildings_map['Friend'][0])
        assert household_gpt not in household_gpt.buildings_map['Home'][0].households
        assert household_gpt not in household_gpt.buildings_map['OutOfTown'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][0].households
        assert household_gpt in household_gpt.buildings_map['Friend'][1].households

        household_gpt.decisions = [household_gpt.OPTIONS.RETURN_HOME.value]
        household_gpt.moved_at_time_step = False
        household_gpt.move(household_gpt.buildings_map['Friend'][1])
        assert household_gpt in household_gpt.buildings_map['Home'][0].households
        assert household_gpt not in household_gpt.buildings_map['OutOfTown'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][1].households

        household_gpt.decisions = [household_gpt.OPTIONS.LEAVE_TOWN.value]
        household_gpt.moved_at_time_step = True
        household_gpt.move(household_gpt.buildings_map['Home'][0])
        assert household_gpt in household_gpt.buildings_map['Home'][0].households
        assert household_gpt not in household_gpt.buildings_map['OutOfTown'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][1].households

        household_gpt.decisions = ['MoveToFriend_1']
        household_gpt.moved_at_time_step = False
        household_gpt.move(household_gpt.buildings_map['Home'][0])
        assert household_gpt not in household_gpt.buildings_map['Home'][0].households
        assert household_gpt not in household_gpt.buildings_map['OutOfTown'][0].households
        assert household_gpt in household_gpt.buildings_map['Friend'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][1].households

    def test_remove_household_from_component(self, household_gpt, built_environment):
        household_gpt.set_parameters(HOUSEHOLD_PARAMETERS)
        household_gpt.map_buildings_to_households(built_environment)
        household_gpt.buildings_map['Home'][0].households = [household_gpt]

        household_gpt.remove_household_from_component(household_gpt.buildings_map['Home'][0])
        assert household_gpt not in household_gpt.buildings_map['Home'][0].households
        assert household_gpt not in household_gpt.buildings_map['OutOfTown'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][1].households

        household_gpt.buildings_map['OutOfTown'][0].households = [household_gpt]
        household_gpt.remove_household_from_component(household_gpt.buildings_map['OutOfTown'][0])
        assert household_gpt not in household_gpt.buildings_map['Home'][0].households
        assert household_gpt not in household_gpt.buildings_map['OutOfTown'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][1].households

    def test_leave_town(self, household_gpt, built_environment):
        household_gpt.set_parameters(HOUSEHOLD_PARAMETERS)
        household_gpt.map_buildings_to_households(built_environment)
        household_gpt.buildings_map['Home'][0].households = [household_gpt]

        household_gpt.leave_town(household_gpt.buildings_map['Home'][0])
        assert household_gpt not in household_gpt.buildings_map['Home'][0].households
        assert household_gpt in household_gpt.buildings_map['OutOfTown'][0].households

        household_gpt.leave_town(household_gpt.buildings_map['OutOfTown'][0])
        assert household_gpt not in household_gpt.buildings_map['Home'][0].households
        assert household_gpt in household_gpt.buildings_map['OutOfTown'][0].households

    def test_move_to_friend(self, household_gpt, built_environment):
        household_gpt.set_parameters(HOUSEHOLD_PARAMETERS)
        household_gpt.map_buildings_to_households(built_environment)
        household_gpt.buildings_map['Home'][0].households = [household_gpt]
        household_gpt.decisions = [household_gpt.OPTIONS.MOVE_TO_FRIEND.value.replace('ID', '1')]

        household_gpt.move_to_friend(household_gpt.buildings_map['Home'][0])
        assert household_gpt not in household_gpt.buildings_map['Home'][0].households
        assert household_gpt in household_gpt.buildings_map['Friend'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][1].households

        household_gpt.decisions = [household_gpt.OPTIONS.MOVE_TO_FRIEND.value.replace('ID', '2')]
        household_gpt.move_to_friend(household_gpt.buildings_map['Friend'][0])
        assert household_gpt not in household_gpt.buildings_map['Home'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][0].households
        assert household_gpt in household_gpt.buildings_map['Friend'][1].households

    def test_return_home(self, household_gpt, built_environment):
        household_gpt.set_parameters(HOUSEHOLD_PARAMETERS)
        household_gpt.map_buildings_to_households(built_environment)
        household_gpt.buildings_map['Friend'][0].households = [household_gpt]
        household_gpt.decisions = [household_gpt.OPTIONS.RETURN_HOME.value]

        household_gpt.return_home(household_gpt.buildings_map['Friend'][0])
        assert household_gpt in household_gpt.buildings_map['Home'][0].households
        assert household_gpt not in household_gpt.buildings_map['OutOfTown'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][0].households
        assert household_gpt not in household_gpt.buildings_map['Friend'][1].households

    def test_update(self, household_gpt, built_environment):
        household_gpt.create_llm(api_key_filename="./openai_api_key.json", temperature=0.0, llm_model='GPT')
        household_gpt.set_parameters(HOUSEHOLD_PARAMETERS)

        household_gpt.map_buildings_to_households(built_environment)
        for friend_house in household_gpt.buildings_map['Friend']:
            for household in friend_house.households:
                household.staying_at = ['Home']
        household_gpt.update(10, household_gpt.buildings_map['Home'][0], [10, 10])
        time_step_narrative = household_gpt.time_step_narrative_creator.get_narrative()
        assert time_step_narrative.replace(' ','') == "\n Your current situation: \n - It's now 10 days after the disaster. \n - You are currently staying at home.  \n - Your friend with ID 1 is in their home.  \n - Your friend with ID 2 is not in their home.  \n - All other households are in town. ".replace(' ','')

        household_gpt.update(15, household_gpt.buildings_map['Friend'][0], [10, 3])
        time_step_narrative = household_gpt.time_step_narrative_creator.get_narrative()
        assert time_step_narrative.replace(' ','') == "\n Your current situation: \n - It's now 15 days after the disaster. \n - You are currently staying with friend 1.  \n - Your friend with ID 1 is in their home.  \n - Your friend with ID 2 is not in their home.  \n - The building where you lived before the disaster has no damage. \n - Less than half of other households are in town. ".replace(' ','')

    def test_update_where_household_is_staying(self, household_gpt, built_environment):
        household_gpt.set_parameters(HOUSEHOLD_PARAMETERS)
        household_gpt.map_buildings_to_households(built_environment)
        location, location_string = household_gpt.update_where_household_is_staying(household_gpt.buildings_map['Home'][0])
        assert location == ['Home']
        assert location_string == 'at home. '

        location, location_string = household_gpt.update_where_household_is_staying(household_gpt.buildings_map['OutOfTown'][0])
        assert location == ['OutOfTown']
        assert location_string == 'out of town. '

        location, location_string = household_gpt.update_where_household_is_staying(household_gpt.buildings_map['Friend'][0])
        assert location == ['Friend']
        assert location_string == 'with friend 1. '

        location, location_string = household_gpt.update_where_household_is_staying(household_gpt.buildings_map['Friend'][1])
        assert location == ['Friend']
        assert location_string == 'with friend 2. '

        with pytest.raises(ValueError):
            location = household_gpt.update_where_household_is_staying(None)

    def test_create_time_step_narrative(self, household_gpt, built_environment):
        household_gpt.set_parameters(HOUSEHOLD_PARAMETERS)
        household_gpt.map_buildings_to_households(built_environment)
        for friend_house in household_gpt.buildings_map['Friend']:
            for household in friend_house.households:
                household.staying_at = ['Home']

        household_gpt.create_time_step_narrative(5, 'at home. ', [10, 10])
        time_step_narrative = household_gpt.time_step_narrative_creator.get_narrative()
        assert time_step_narrative == "\n Your current situation: \n - It's now 5 days after the disaster. \n - You are currently staying at home.  \n - Your friend with ID 1 is in their home.  \n - Your friend with ID 2 is not in their home.  \n - All other households are in town. "

        household_gpt.create_time_step_narrative(50, 'with a friend. ', [10, 0])
        time_step_narrative = household_gpt.time_step_narrative_creator.get_narrative()
        assert time_step_narrative == "\n Your current situation: \n - It's now 50 days after the disaster. \n - You are currently staying with a friend.  \n - Your friend with ID 1 is in their home.  \n - Your friend with ID 2 is not in their home.  \n - The building where you lived before the disaster has no damage. \n - There are no other households in town. "

    def test_get_decision(self, household_gpt):
        decision_string = "StayAtHome"
        decision = household_gpt.get_decision(decision_string)
        assert decision == 'StayAtHome'

        decision_string = "MoveToFriend_1"
        decision = household_gpt.get_decision(decision_string)
        assert decision == 'MoveToFriend_1'

        decision_string = "BlaBla Bla BlaBla MoveToFriend_1."
        decision = household_gpt.get_decision(decision_string)
        assert decision == 'MoveToFriend_1'

        decision_string = "BlaBla Bla BlaBla **MoveToFriend_10**."
        decision = household_gpt.get_decision(decision_string)
        assert decision == 'MoveToFriend_10'

        decision_string = "BlaBla Bla BlaBla StayAtHome."
        decision = household_gpt.get_decision(decision_string)
        assert decision == 'StayAtHome'

        decision_string = "BlaBla Bla BlaBla **LeaveTown**"
        decision = household_gpt.get_decision(decision_string)
        assert decision == 'LeaveTown'

        decision_string = "BlaBla Bla BlaBla **LeaveTownNow**"
        decision = household_gpt.get_decision(decision_string)
        assert decision == None

    def test_update_based_on_unmet_demand(self, household_gpt):
        household_gpt.update_based_on_unmet_demand(1.0, 'Resource1')
        time_step_narrative = household_gpt.time_step_narrative_creator.get_narrative()
        assert time_step_narrative == "\n - At your current location, your needs for Resource1 are completely satisfied. "

        household_gpt.time_step_narrative_creator.narrative = ""
        household_gpt.update_based_on_unmet_demand(0.0, 'Resource1')
        time_step_narrative = household_gpt.time_step_narrative_creator.get_narrative()
        assert time_step_narrative == "\n - At your current location, your needs for Resource1 are not satisfied. "

        household_gpt.time_step_narrative_creator.narrative = ""
        household_gpt.update_based_on_unmet_demand(0.3, 'Resource1')
        time_step_narrative = household_gpt.time_step_narrative_creator.get_narrative()
        assert time_step_narrative == "\n - At your current location, your needs for Resource1 are partially satisfied. "

    def test_get_demand(self, household_gpt):
        household_gpt.create_llm(api_key_filename="./openai_api_key.json", temperature=0.0, llm_model='GPT')
        household_gpt.set_parameters(HOUSEHOLD_PARAMETERS)

        demand = household_gpt.get_demand()
        assert isinstance(demand, dict)
        assert demand['PotableWater'] == 150*5

        HOUSEHOLD_PARAMETERS['ResourceDemand']['ElectricPower'] = 10
        household_gpt.create_llm(api_key_filename="./openai_api_key.json", temperature=0.0, llm_model='GPT')
        household_gpt.set_parameters(HOUSEHOLD_PARAMETERS)
        demand = household_gpt.get_demand()
        assert isinstance(demand, dict)
        assert demand['PotableWater'] == 150*5
        assert demand['ElectricPower'] == 10*5

    def test_string_to_dict(self, household_gpt):
        test_string = "{'PotableWater': 150, 'ElectricPower': 10}"
        result = household_gpt.string_to_dict(test_string)
        assert isinstance(result, dict)
        assert result['PotableWater'] == 150
        assert result['ElectricPower'] == 10