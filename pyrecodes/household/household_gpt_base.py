import asyncio
import ast
import re
import requests
import string
import openai
from pyrecodes.utilities import read_json_file

TEXT_WORDS_BATCH_SIZE = 500
GPT_MODEL = 'gpt-4o-mini-2024-07-18' # or gpt-5-mini-2025-08-07
LLAMA_MODEL = 'llama3'
ASYNC_MODE = False

class HouseholdGPTBase:
    """Shared GPT machinery for all household agent types.

    Not a Household itself — subclasses that participate in the regional simulation
    must also inherit from Household. Survey-only agents need only this base.
    """

    PROMPTS_FILE = None  # each subclass must define this
    MAX_PAST_EXPERIENCE_FOR_SUMMARY = 5
    
    def __init__(self) -> None:
        self.decisions = []
        self.moved_at_time_step = False
        self.prompts = read_json_file(self.PROMPTS_FILE)
        self._async_loop = asyncio.new_event_loop() if ASYNC_MODE else None

    def __getstate__(self) -> dict:
        # asyncio event loops cannot be pickled/deepcopied; exclude and recreate on restore
        state = self.__dict__.copy()
        state['_async_loop'] = None
        return state

    def __setstate__(self, state: dict) -> None:
        self.__dict__.update(state)
        if ASYNC_MODE:
            self._async_loop = asyncio.new_event_loop()

    def create_llm(self, api_key_filename: str, temperature: float, llm_model: str) -> None:
        self.llm = LLM(api_key_filename, temperature=temperature, llm_model=llm_model)

    def inform_gpt(self, inform_gpt_method: str) -> None:
        if inform_gpt_method is None or inform_gpt_method == 'None':
            pass
        elif inform_gpt_method == 'ReadLiterature':
            self.read_literature()
        elif inform_gpt_method == 'ReadRuleset':
            self.read_ruleset()
        else:
            raise ValueError(f'Invalid method to inform GPT: {inform_gpt_method!r}.')

    def read_literature(self, file_name: str = './pyrecodes/household/literature_summaries.json') -> None:
        summaries_json = read_json_file(file_name)
        summaries = ""
        for summary in summaries_json['Literature']:
            summaries += f"\n - {summary['paper']}\n  Findings: {summary['findings']}\n\n"
        content = self.prompts['ReadLiterature']['content'].replace('SUMMARIES', summaries)
        self.prompt_llm({'role': self.prompts['ReadLiterature']['role'], 'content': content}, print_answer=False)

    def read_ruleset(self) -> None:
        self.prompt_llm(self.prompts['ReadRuleset'], print_answer=False)

    @staticmethod
    def split_text_into_batches(text: str, max_words: int = TEXT_WORDS_BATCH_SIZE):
        words = text.split()
        for i in range(0, len(words), max_words):
            yield " ".join(words[i:i + max_words])

    def prompt_llm(self, prompt: dict, print_answer: bool = False, add_to_past_experience: bool = False) -> str:
        if ASYNC_MODE:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                return self._async_loop.run_until_complete(self.async_prompt_llm(prompt, print_answer=print_answer, add_to_past_experience=add_to_past_experience))
            future = asyncio.ensure_future(self.async_prompt_llm(prompt, print_answer=print_answer, add_to_past_experience=add_to_past_experience))
            return loop.run_until_complete(future)
        return self.llm.prompt(prompt, print_answer=print_answer, add_to_past_experience=add_to_past_experience)

    async def async_prompt_llm(self, prompt: dict, print_answer: bool = False, add_to_past_experience: bool = False) -> str:
        return await self.llm.async_prompt(prompt, print_answer=print_answer, add_to_past_experience=add_to_past_experience)

    def get_decision(self, answer: str):
        decision_output = answer.strip().split()[-1].strip(string.punctuation)
        for decision in self.OPTIONS:
            template = decision.value
            if template.endswith('_ID'):
                if decision_output.startswith(template[:-3]):
                    return decision_output
            elif decision_output == template:
                return decision_output
        return None

    def format_household_options_string(self, household_options: list) -> str:
        joined = ", ".join(household_options)
        return joined + ". " if joined else ""

    def string_to_dict(self, string: str) -> dict:
        matches = re.findall(r'\{.*?\}', string)
        return ast.literal_eval(matches[0])


class LLM:
    """Wraps OpenAI GPT or Ollama Llama, maintaining chat history and prompt management."""

    def __init__(self, api_key_filename: str, temperature: float = 1.0, llm_model: str = 'GPT') -> None:
        self.chat_history = []
        self.relevant_prompts = []
        self.past_experience = []
        self.temperature = temperature
        self.set_llm_model(llm_model, api_key_filename)

    def set_llm_model(self, llm_model: str, api_key_filename: str) -> None:
        if llm_model == 'GPT':
            self.api_key = read_json_file(api_key_filename)['API_KEY']
            openai.api_key = self.api_key
            self.LLM_MODEL = GPT_MODEL
            self.llm_backend = 'openai'
            self.llm = openai.AsyncOpenAI(api_key=self.api_key) if ASYNC_MODE else openai.OpenAI(api_key=self.api_key)
        elif llm_model == 'LLAMA':
            self.LLM_MODEL = LLAMA_MODEL
            self.llm_backend = 'ollama'
        else:
            raise ValueError("llm_model must be 'GPT' or 'LLAMA'")

    def prompt(self, prompt: dict, print_answer: bool = False, add_to_past_experience: bool = False) -> str:
        if ASYNC_MODE:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                return asyncio.run(self.async_prompt(prompt, print_answer, add_to_past_experience))
            future = asyncio.ensure_future(self.async_prompt(prompt, print_answer, add_to_past_experience))
            return loop.run_until_complete(future)
        self.add_to_chat_history(prompt)
        answer = self.query_llm(self.relevant_prompts + [prompt])
        if print_answer:
            print('--' * 20)
            print(answer)
            print('--' * 20)
        self.add_to_relevant_prompts(prompt)
        self.add_to_chat_history({'content': answer, 'role': 'assistant'})
        if add_to_past_experience:
            self.add_to_past_experience(answer)
        return answer

    async def async_prompt(self, prompt: dict, print_answer: bool = False, add_to_past_experience: bool = False) -> str:
        self.add_to_chat_history(prompt)
        answer = await self.async_query_llm(self.relevant_prompts + [prompt])
        if print_answer:
            print('--' * 20)
            print(answer)
            print('--' * 20)
        self.add_to_relevant_prompts(prompt)
        self.add_to_chat_history({'content': answer, 'role': 'assistant'})
        if add_to_past_experience:
            self.add_to_past_experience(answer)
        return answer

    def query_llm(self, current_prompt: list) -> str:
        if self.llm_backend == 'openai':
            chat_completion = self.llm.chat.completions.create(
                model=self.LLM_MODEL,
                messages=current_prompt,
                temperature=self.temperature,
            )
            return chat_completion.choices[0].message.content
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": self.LLM_MODEL, "prompt": self.convert_chat_to_prompt(current_prompt), "stream": False, "temperature": self.temperature},
        )
        response.raise_for_status()
        return response.json()["response"]

    async def async_query_llm(self, current_prompt: list) -> str:
        if self.llm_backend == 'openai':
            chat_completion = await self.llm.chat.completions.create(
                model=self.LLM_MODEL,
                messages=current_prompt,
                temperature=self.temperature,
            )
            return chat_completion.choices[0].message.content
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:11434/api/generate",
                json={"model": self.LLM_MODEL, "prompt": self.convert_chat_to_prompt(current_prompt), "stream": False, "temperature": self.temperature},
            ) as resp:
                resp.raise_for_status()
                return (await resp.json())["response"]

    def convert_chat_to_prompt(self, messages: list) -> str:
        role_prefix = {"user": "User", "assistant": "Assistant", "system": "System", "developer": "Developer"}
        prompt = "".join(f"{role_prefix.get(msg['role'], msg['role'])}: {msg['content']}\n" for msg in messages)
        return prompt + "Assistant:"

    def add_to_chat_history(self, prompt: dict) -> None:
        self.chat_history.append(prompt)

    def add_to_relevant_prompts(self, prompt: dict) -> None:
        if prompt['role'] == 'developer':
            self.relevant_prompts.append(prompt)

    def add_to_past_experience(self, answer: str) -> None:
        decision_number = len(self.past_experience) + 1
        self.past_experience.append({'role': 'assistant', 'content': f'\n - Decision {decision_number}: \n ' + answer})

    def summarize_past_experience(self, description_prompt: dict) -> str:
        if not self.past_experience:
            return ""
        recent = self.past_experience[-self.MAX_PAST_EXPERIENCE_FOR_SUMMARY:]
        past_experience_string = description_prompt['content'] + '\n'.join(item['content'] for item in recent)
        answer = self.prompt({'role': 'user', 'content': past_experience_string}, print_answer=False, add_to_past_experience=False)
        return '\n' + answer
