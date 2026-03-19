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

    def add_to_past_experience(self, llm):
        pass

    def test_summarize_past_experience(self, llm):
        dummy_description_prompt = {
            "role": "user",
            "content": "Task: \n Summarize decisions below. Just write what comes after the 'Decision X'."
        }
        summary = llm.summarize_past_experience(dummy_description_prompt)
        assert summary == ''

        llm.past_experience = [
            {"role": "assistant", "content": "\n Decision 1: \n Test summary."},
        ]
        summary = llm.summarize_past_experience(dummy_description_prompt)
        assert self.remove_blank_lines_and_spaces(summary) == self.remove_blank_lines_and_spaces("\nDecision 1: Test summary.")

        llm.past_experience = [
            {"role": "assistant", "content": "\n Decision 1: \n Test summary."},
            {"role": "assistant", "content": "\n Decision 2: \n Another test summary."},
        ]
        summary = llm.summarize_past_experience(dummy_description_prompt)
        assert self.remove_blank_lines_and_spaces(summary) == self.remove_blank_lines_and_spaces("\nDecision 1: Test summary.  \nDecision 2: Another test summary.")
    

    
