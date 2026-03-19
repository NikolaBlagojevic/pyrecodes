import math

from enum import Enum

from pyrecodes.household.household import Household
from pyrecodes.household.household_gpt_base import HouseholdGPTBase, LLM
from pyrecodes.component.component import Component
from pyrecodes.component.r2d_building_with_households import R2DBuildingWithHouseholds
from pyrecodes.component_recovery_model.recovery_model import RecoveryModel

RESOURCE_DEMAND_CALCULATION_METHOD = 'Constant'

SOCIOECONOMIC_MAPPING = {
    'TENURE': 'Tenure',
    'INCOME': 'Income',
    'OCCUPANTS': 'Occupants',
    'NUM_CHILDREN': 'Children',
    'NUM_ELDERLY': 'Elderly',
    'NUM_EMPLOYED': 'EmploymentStatus',
    'IMMIGRATION_STATUS': 'ImmigrationStatus'
}

LOCATION_STRING_MAPPING = {
    'Friend': 'with friend FRIEND_ID. ',
    'OutOfTown': 'out of town. ',
    'Home': 'at home. '
}


class HouseholdOptions(Enum):
    LEAVE_TOWN = 'LeaveTown'
    MOVE_TO_FRIEND = 'MoveToFriend_ID'
    RETURN_HOME = 'ReturnHome'
    STAY_AT_HOME = 'StayAtHome'
    STAY_WITH_FRIEND = 'StayWithFriend_ID'
    STAY_OUT_OF_TOWN = 'StayOutOfTown'


class HouseholdGPT(Household, HouseholdGPTBase):
    """GPT-powered household agent for regional sociotechnical recovery simulations."""

    PROMPTS_FILE = './pyrecodes/household/household_gpt_prompts.json'
    OPTIONS = HouseholdOptions

    def __init__(self) -> None:
        HouseholdGPTBase.__init__(self)
        self.friends = []
        self.home_id = None
        self.staying_at = []
        self.time_step_narrative_creator = TimeStepNarrativeCreator(self.prompts)

    def set_parameters(self, parameters: dict, api_key_filename: str = "./openai_api_key.json", temperature: float = 1.0, llm_model: str = 'GPT') -> None:
        self.set_household_id(parameters['HouseholdID'])
        self.create_llm(api_key_filename, temperature, llm_model)
        self.inform_gpt(parameters.get('InformGPTMethod', None))
        self.set_context()
        self.set_socioeconomic_parameters(parameters)
        self.set_resource_demand_parameters(parameters)

    def set_household_id(self, household_id: int) -> None:
        self.id = household_id

    def set_context(self) -> None:
        self.prompt_llm(self.prompts['Initial'], print_answer=False)

    def set_socioeconomic_parameters(self, parameters: dict) -> None:
        self.set_friends_ids(parameters['SocioEconomicParameters']['Friends'])
        self.set_home_id(parameters['SocioEconomicParameters']['Home'])
        self.send_socioeconomic_parameters_to_llm(parameters['SocioEconomicParameters'])

    def set_friends_ids(self, friends: list) -> None:
        self.friends = friends

    def set_home_id(self, home_id: int) -> None:
        self.home_id = home_id

    def set_resource_demand_parameters(self, parameters: dict) -> None:
        self.send_resource_demand_parameters_to_llm(parameters['ResourceDemand'])
        if RESOURCE_DEMAND_CALCULATION_METHOD == 'Constant':
            answer = self.prompt_llm(self.prompts['GetDemand'], print_answer=False)
            self.resource_demand = self.string_to_dict(answer)

    def send_socioeconomic_parameters_to_llm(self, socioeconomic_parameters: dict) -> None:
        content = self.prompts['SetSocioeconomicParameters']['content']
        content = content.replace('NUM_FRIENDS', str(len(socioeconomic_parameters['Friends'])))
        for word_to_replace, key_in_parameters in SOCIOECONOMIC_MAPPING.items():
            content = content.replace(word_to_replace, str(socioeconomic_parameters[key_in_parameters]))
        self.prompt_llm({'role': self.prompts['SetSocioeconomicParameters']['role'], 'content': content})

    def send_resource_demand_parameters_to_llm(self, parameters: dict) -> None:
        content = self.prompts['SetResourceDemandParameters']['content'].replace('PARAMETERS', str(parameters))
        self.prompt_llm({'role': self.prompts['SetResourceDemandParameters']['role'], 'content': content}, print_answer=False)

    def map_buildings_to_households(self, built_environment) -> None:
        self.buildings_map = {'Home': [], 'Friend': [], 'OutOfTown': []}
        for component in built_environment.components:
            if isinstance(component, R2DBuildingWithHouseholds):
                if component.component_represents_home(self):
                    self.buildings_map['Home'] = [component]
                elif component.component_represents_friends_house(self):
                    self.buildings_map['Friend'].append(component)
                elif component.component_represents_out_of_town():
                    self.buildings_map['OutOfTown'] = [component]

    def decide(self, component_where_household_is_staying: Component) -> None:
        household_options = self.get_household_options(component_where_household_is_staying)
        self.time_step_narrative_creator.summarize_past_experience(self.llm)
        self.time_step_narrative_creator.update_household_options(household_options)
        time_step_narrative = self.time_step_narrative_creator.get_narrative()
        answer = self.prompt_llm({'role': 'user', 'content': time_step_narrative}, print_answer=False, add_to_past_experience=True)
        while True:
            decision = self.get_decision(answer)
            if decision is not None:
                break
            print(f"\n Decision not recognized. Trying again. \n Full answer: \n {answer}")
            answer = self.prompt_llm({'role': 'user', 'content': time_step_narrative}, print_answer=False, add_to_past_experience=True)
        self.decisions.append(decision)

    def add_move_to_friend_options(self, component_where_household_is_staying=None) -> list:
        return [
            self.OPTIONS.MOVE_TO_FRIEND.value.replace('ID', str(self.find_friend_id(friends_house)))
            for friends_house in self.buildings_map.get('Friend', [])
            if friends_house != component_where_household_is_staying
        ]

    def get_household_options(self, component_where_household_is_staying: Component) -> str:
        current_location = self.staying_at[-1]
        if current_location == 'Friend':
            friend_id = self.find_friend_id(component_where_household_is_staying)
            household_options = [self.OPTIONS.LEAVE_TOWN.value, self.OPTIONS.RETURN_HOME.value, self.OPTIONS.STAY_WITH_FRIEND.value.replace('ID', str(friend_id))]
        elif current_location == 'OutOfTown':
            household_options = [self.OPTIONS.RETURN_HOME.value, self.OPTIONS.STAY_OUT_OF_TOWN.value]
        elif current_location == 'Home':
            household_options = [self.OPTIONS.STAY_AT_HOME.value, self.OPTIONS.LEAVE_TOWN.value]
        else:
            return ""
        household_options += self.add_move_to_friend_options(component_where_household_is_staying)
        return self.format_household_options_string(household_options)

    def find_friend_id(self, component: Component) -> int:
        return self.buildings_map['Friend'].index(component) + 1

    def move(self, component_where_household_is_staying: Component) -> None:
        if self.moved_at_time_step:
            return
        self.moved_at_time_step = True
        decision = self.decisions[-1]
        if self.OPTIONS.LEAVE_TOWN.value in decision:
            self.leave_town(component_where_household_is_staying)
        elif self.OPTIONS.MOVE_TO_FRIEND.value[:-2] in decision:
            self.move_to_friend(component_where_household_is_staying)
        elif self.OPTIONS.RETURN_HOME.value in decision:
            self.return_home(component_where_household_is_staying)

    def leave_town(self, component_where_household_is_staying: Component) -> None:
        self.remove_household_from_component(component_where_household_is_staying)
        self.buildings_map['OutOfTown'][0].households.append(self)

    def move_to_friend(self, component_where_household_is_staying: Component) -> None:
        friend_id = int(self.decisions[-1][-1])
        friends_house = self.buildings_map['Friend'][friend_id - 1]
        self.remove_household_from_component(component_where_household_is_staying)
        friends_house.households.append(self)

    def return_home(self, component_where_household_is_staying: Component) -> None:
        self.remove_household_from_component(component_where_household_is_staying)
        self.buildings_map['Home'][0].households.append(self)

    def remove_household_from_component(self, component: Component) -> None:
        component.households.remove(self)

    def update(self, time_step: int, component: Component, households_in_town: list) -> None:
        location, location_string = self.update_where_household_is_staying(component)
        self.staying_at.append(location[0])
        self.moved_at_time_step = False
        self.create_time_step_narrative(time_step, location_string, households_in_town)

    def create_time_step_narrative(self, time_step: int, location_string: str, households_in_town: list) -> None:
        self.time_step_narrative_creator.create(time_step, location_string, households_in_town, self.buildings_map, self.find_friend_id)

    def update_where_household_is_staying(self, component: Component):
        location = [key for key, value in self.buildings_map.items() if component in value]
        if not location:
            raise ValueError(f"Household {self.id} is not staying in any of the buildings it is mapped to.")
        if location[0] == 'Friend':
            return location, LOCATION_STRING_MAPPING[location[0]].replace('FRIEND_ID', str(self.find_friend_id(component)))
        return location, LOCATION_STRING_MAPPING[location[0]]

    def update_based_on_unmet_demand(self, percent_of_met_demand: float, resource_name: str) -> None:
        self.time_step_narrative_creator.update_resource_demand_fulfilment_status(percent_of_met_demand, resource_name)

    def get_demand(self) -> dict:
        if RESOURCE_DEMAND_CALCULATION_METHOD == 'Constant':
            return self.resource_demand
        answer = self.prompt_llm(self.prompts['GetDemand'], print_answer=False)
        return self.string_to_dict(answer)

    def get_supply(self):
        pass

    def get_relocation_factors(self) -> dict:
        summary = self.llm.summarize_past_experience(self.prompts['SummarizePastExperience'])
        content = self.prompts['GetRelocationFactors']['content'].replace('PAST_EXPERIENCE', summary)
        answer = self.prompt_llm({'role': 'user', 'content': content}, print_answer=False)
        return self.string_to_dict(answer.lower())


class TimeStepNarrativeCreator:
    """Builds the per-time-step prompt for simulation household agents."""

    def __init__(self, prompts: dict) -> None:
        self.prompts = prompts
        self.narrative = ""

    def create(self, time_step: int, location_update: str, households_in_town: list, buildings_map: dict, find_friend_id) -> None:
        self.start_the_time_step_narrative()
        self.add_current_time_step_to_narrative(time_step)
        self.add_household_location_to_time_step_narrative(location_update)
        if time_step > 0:
            self.update_household_on_the_status_of_their_friend(buildings_map, find_friend_id)
        self.update_household_on_recovery_state_of_their_predisaster_home(location_update, buildings_map)
        self.update_household_on_other_households_in_town(households_in_town, location_update)

    def start_the_time_step_narrative(self) -> None:
        self.narrative = self.prompts['StartTimeStepNarrative']['content']

    def add_current_time_step_to_narrative(self, time_step: int) -> None:
        self.add_to_narrative(self.prompts['TimeStepUpdate']['content'].replace('TIME_STEP', str(time_step)))

    def add_household_location_to_time_step_narrative(self, location_update: str) -> None:
        self.add_to_narrative(self.prompts['HouseholdLocationUpdate']['content'].replace('HOUSEHOLD_LOCATION_STRING', location_update))

    def add_to_narrative(self, prompt: str) -> None:
        self.narrative += prompt + ' '

    def update_household_on_recovery_state_of_their_predisaster_home(self, location_string: str, buildings_map: dict) -> None:
        if location_string != LOCATION_STRING_MAPPING['Home']:
            self.provide_information_on_building_recovery(buildings_map['Home'][0].recovery_model, 'building where you lived before the disaster')

    def provide_information_on_building_recovery(self, recovery_model: RecoveryModel, household_location_string: str) -> None:
        recovery_info = self.format_recovery_info(recovery_model, household_location_string)
        self.add_to_narrative(self.prompts['InformOnBuildingRecovery']['content'].replace('BUILDING_RECOVERY_DESCRIPTION', recovery_info))

    def format_recovery_info(self, recovery_model: RecoveryModel, household_location_string: str) -> str:
        building_functionality_level = recovery_model.get_functionality_level()
        if building_functionality_level == 1:
            return self.prompts['BuildingHasNoDamage']['content'].replace('HOUSEHOLD_LOCATION_STRING', household_location_string)
        damage_indicator = self.get_building_damage_indicator(building_functionality_level)
        return self.prompts['BuildingHasDamage']['content'].replace('HOUSEHOLD_LOCATION_STRING', household_location_string).replace('DAMAGE_INDICATOR', damage_indicator)

    def get_building_damage_indicator(self, building_functionality_level: float) -> str:
        if math.isclose(building_functionality_level, 0):
            return "completely"
        elif math.isclose(building_functionality_level, 1):
            return "not"
        return "partially"

    def update_household_on_the_status_of_their_friend(self, buildings_map: dict, find_friend_id) -> None:
        for friends_house in buildings_map['Friend']:
            friend_at_home = any(h.staying_at[-1] == 'Home' for h in friends_house.households)
            friends_id = find_friend_id(friends_house)
            status = "in their home" if friend_at_home else "not in their home"
            self.add_to_narrative(f"\n - Your friend with ID {friends_id} is {status}. ")

    def update_current_building_recovery_info(self, recovery_model: RecoveryModel) -> None:
        self.provide_information_on_building_recovery(recovery_model, 'building you are currently in')

    def update_household_on_other_households_in_town(self, households_in_town: list, location_string: str) -> None:
        ratio = households_in_town[-1] / households_in_town[0]
        if ratio == 0:
            prompt = '\n - There are no other households in town.'
        elif ratio < 0.5:
            prompt = '\n - Less than half of other households are in town.'
        elif ratio < 1:
            prompt = '\n - More than half of other households are in town.'
        else:
            prompt = '\n - All other households are in town.'
        if location_string != LOCATION_STRING_MAPPING['OutOfTown']:
            self.add_to_narrative(prompt)

    def update_resource_demand_fulfilment_status(self, percent_of_met_demand: float, resource_name: str) -> None:
        if resource_name == 'TransportationService':
            met_demand_indicator = self.get_met_demand_indicator_for_traffic(percent_of_met_demand)
            prompt = self.prompts['UpdateTrafficSituation']['content'].replace('MET_DEMAND_INDICATOR', met_demand_indicator).replace('RESOURCE_NAME', resource_name)
        else:
            met_demand_indicator = self.get_met_demand_indicator(percent_of_met_demand)
            prompt = self.prompts['UpdateUnmetDemand']['content'].replace('MET_DEMAND_INDICATOR', met_demand_indicator).replace('RESOURCE_NAME', resource_name)
        self.add_to_narrative(prompt)

    def get_met_demand_indicator_for_traffic(self, percent_of_met_demand: float) -> str:
        if math.isclose(percent_of_met_demand, 1):
            return "the same"
        elif 1 < percent_of_met_demand < 2:
            return "slightly longer"
        return "significantly longer"

    def get_met_demand_indicator(self, percent_of_met_demand: float) -> str:
        if math.isclose(percent_of_met_demand, 1):
            return "completely satisfied"
        elif math.isclose(percent_of_met_demand, 0):
            return "not satisfied"
        return "partially satisfied"

    def update_household_options(self, household_options: str) -> None:
        self.add_to_narrative(self.prompts['MakeDecision']['content'].replace('HOUSEHOLD_OPTIONS', household_options))

    def summarize_past_experience(self, llm: LLM) -> None:
        self.add_to_narrative(llm.summarize_past_experience(self.prompts['SummarizePastExperience']))

    def get_narrative(self) -> str:
        return self.narrative
