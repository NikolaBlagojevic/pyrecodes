from enum import Enum

from pyrecodes.household.household_gpt_base import HouseholdGPTBase

SOCIOECONOMIC_MAPPING = {
    'STATE': 'State',
    'MSA': 'MSA',
    'TENURE': 'Tenure',
    'INCOME': 'Income',
    'OCCUPANTS': 'Occupants',
    'NUM_CHILDREN_5': 'Kids5years',
    'NUM_CHILDREN_11': 'Kids5-11years',
    'NUM_CHILDREN_17': 'Kids12-17years',
    'EMPLOYED': 'EmploymentStatus'
}


class HouseholdOptions(Enum):
    DISPLACED_UNDER_WEEK = 'LeaveHomeForLessThanAWeek'
    DISPLACED_OVER_WEEK = 'LeaveHomeForMoreThanAWeek'


class HouseholdSurveyGPT(HouseholdGPTBase):
    """GPT-powered household agent for validating decisions against the Household Pulse Survey."""

    PROMPTS_FILE = './pyrecodes/household/household_survey_gpt_prompts.json'
    PUBLICATION_FOLDER = "./literature_for_households"
    OPTIONS = HouseholdOptions

    def __init__(self) -> None:
        super().__init__()
        self.home_id = None
        self.time_step_narrative_creator = SurveyNarrativeCreator(self.prompts)

    def set_parameters(self, parameters: dict, api_key_filename: str = "./openai_api_key.json", temperature: float = 1.0, llm_model: str = 'GPT') -> None:
        self.create_llm(api_key_filename, temperature, llm_model)
        self.inform_gpt_method = parameters.get('InformGPTMethod', None)
        self.set_context(parameters['DisasterType'])
        self.set_socioeconomic_parameters(parameters)

    def set_context(self, disaster_type: str) -> None:
        content = self.prompts['Initial']['content'].replace('DISASTER', disaster_type)
        self.prompt_llm({'role': self.prompts['Initial']['role'], 'content': content}, print_answer=False)

    def set_socioeconomic_parameters(self, parameters: dict) -> None:
        self.send_socioeconomic_parameters_to_llm(parameters['SocioEconomicParameters'])

    def send_socioeconomic_parameters_to_llm(self, socioeconomic_parameters: dict) -> None:
        content = self.prompts['SetSocioeconomicParameters']['content']
        for word_to_replace, key_in_parameters in SOCIOECONOMIC_MAPPING.items():
            value = socioeconomic_parameters[key_in_parameters]
            content = content.replace(word_to_replace, str(value) if value is not None else '')
        self.prompt_llm({'role': self.prompts['SetSocioeconomicParameters']['role'], 'content': content}, print_answer=False)

    def decide(self) -> None:
        self.time_step_narrative_creator.update_household_options(self.get_household_options())
        time_step_narrative = self.time_step_narrative_creator.get_narrative()
        self.inform_gpt(self.inform_gpt_method)
        answer = self.prompt_llm({'role': 'user', 'content': time_step_narrative}, print_answer=False, add_to_past_experience=True)
        while True:
            decision = self.get_decision(answer)
            if decision is not None:
                break
            print(f"\n Decision not recognized. Trying again. \n Full answer: \n {answer}")
            answer = self.prompt_llm({'role': 'user', 'content': time_step_narrative}, print_answer=False, add_to_past_experience=True)
        self.decisions.append(decision)

    def get_household_options(self) -> str:
        return self.format_household_options_string([option.value for option in self.OPTIONS])

    def create_time_step_narrative(self, building_damage: str, resource_met_indicators: dict, disaster_type: str) -> None:
        self.time_step_narrative_creator.create(building_damage, resource_met_indicators, disaster_type)


class SurveyNarrativeCreator:
    """Builds the prompt for survey-validation household agents."""

    def __init__(self, prompts: dict) -> None:
        self.prompts = prompts
        self.narrative = ""

    def create(self, building_damage: str, resource_met_indicators: dict, disaster_type: str) -> None:
        self.narrative = self.prompts['StartTimeStepNarrative']['content']
        self.set_building_damage(building_damage, disaster_type)
        self.set_resource_met_indicators(resource_met_indicators, disaster_type)

    def set_building_damage(self, building_damage: str, disaster_type: str) -> None:
        prompt = self.prompts['InformOnBuildingDamage']['content'].replace('BUILDING_DAMAGE_DESCRIPTION', building_damage).replace('DISASTER_TYPE', disaster_type)
        self.add_to_narrative(prompt)

    def set_resource_met_indicators(self, resource_met_indicators: dict, disaster_type: str) -> None:
        for met_demand_indicator in resource_met_indicators.values():
            prompt = self.prompts['InformOnUnmetDemand']['content'].replace('MET_DEMAND_INDICATOR', met_demand_indicator).replace('DISASTER_TYPE', disaster_type)
            self.add_to_narrative(prompt)

    def add_to_narrative(self, prompt: str) -> None:
        self.narrative += prompt + ' '

    def update_household_options(self, household_options: str) -> None:
        self.add_to_narrative(self.prompts['MakeDecision']['content'].replace('HOUSEHOLD_OPTIONS', household_options))

    def get_narrative(self) -> str:
        return self.narrative
