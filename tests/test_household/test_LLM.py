import pytest
from pyrecodes.household.household_gpt import LLM

class TestLLM:

    @pytest.fixture
    def llm(self):
        return LLM(api_key_filename="./openai_api_key.json", temperature=0.0)

    def remove_blank_lines_and_spaces(self, string):
        return ''.join(string.split())
    
    def test_init(self, llm):
        pass

    def test_prompt(self, llm):
        pass

    def test_add_to_chat_history(self, llm):
        pass

    def test_add_to_relevant_prompts(self, llm):
        pass

    def test_add_to_past_experience(self, llm):
        llm.add_to_past_experience("I decided to stay at home.")
        assert len(llm.past_experience) == 1

    def test_get_past_experience_string_empty(self, llm):
        assert llm.get_past_experience_string() == ""

    def test_get_past_experience_string(self, llm):
        llm.past_experience = [
            "I stayed at home in week 1 because my building had no damage. In week 2, I left town because water was not available.",
        ]
        result = llm.get_past_experience_string()
        assert "Your past experience:" in result
        assert "I stayed at home in week 1" in result

    def test_update_past_experience_with_summarization(self, llm):
        dummy_prompt = {
            "role": "user",
            "content": "Compress past experience and latest decision. \n\n PAST_EXPERIENCE \n\n LATEST_ANSWER"
        }
        llm.update_past_experience(dummy_prompt, "I stayed home because building was fine.")
        assert len(llm.past_experience) == 1
        assert isinstance(llm.past_experience[0], str)

    def test_update_past_experience_without_summarization(self):
        llm = LLM(api_key_filename="./openai_api_key.json", temperature=0.0, summarize_experience=False)
        dummy_prompt = {
            "role": "user",
            "content": "Compress past experience and latest decision. \n\n PAST_EXPERIENCE \n\n LATEST_ANSWER"
        }
        llm.update_past_experience(dummy_prompt, "I stayed home because building was fine.")
        llm.update_past_experience(dummy_prompt, "I left town because water was unavailable.")
        assert len(llm.past_experience) == 2
        assert llm.past_experience[0] == "I stayed home because building was fine."
        assert llm.past_experience[1] == "I left town because water was unavailable."

    def test_get_past_experience_string_without_summarization(self):
        llm = LLM(api_key_filename="./openai_api_key.json", temperature=0.0, summarize_experience=False)
        llm.past_experience = ["Stayed home.", "Left town."]
        result = llm.get_past_experience_string()
        assert "Decision 1: Stayed home." in result
        assert "Decision 2: Left town." in result

