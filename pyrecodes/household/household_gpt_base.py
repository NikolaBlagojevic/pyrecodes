import ast
import asyncio
import copy
import re
import string
import textwrap
import openai
from pyrecodes.utilities import read_json_file

TEXT_WORDS_BATCH_SIZE = 500
GPT_MODEL = 'gpt-4o-mini-2024-07-18' # or gpt-5-mini-2025-08-07 - more expensive, be careful


class HouseholdGPTBase:
    """Shared GPT machinery for all household agent types.

    Not a Household itself — subclasses that participate in the regional simulation
    must also inherit from Household. Survey-only agents need only this base.
    """

    PROMPTS_FILE = None  # each subclass must define this

    def __init__(self) -> None:
        self.decisions = []
        self.moved_at_time_step = False
        self.prompts = read_json_file(self.PROMPTS_FILE)

    def create_llm(self, api_key_filename: str, temperature: float, llm_model: str, summarize_experience: bool = True) -> None:
        self.llm = LLM(api_key_filename, temperature=temperature, llm_model=llm_model, summarize_experience=summarize_experience)

    def inform_gpt(self, inform_gpt_method: str) -> None:
        if inform_gpt_method is None or inform_gpt_method == 'None':
            pass
        elif inform_gpt_method == 'ReadLiterature':
            self.read_literature()
        elif inform_gpt_method == 'ReadRuleset':
            self.read_ruleset()
        else:
            raise ValueError(f'Invalid method to inform GPT: {inform_gpt_method!r}.')

    async def async_inform_gpt(self, inform_gpt_method: str) -> None:
        if inform_gpt_method is None or inform_gpt_method == 'None':
            pass
        elif inform_gpt_method == 'ReadLiterature':
            await self.async_read_literature()
        elif inform_gpt_method == 'ReadRuleset':
            await self.async_read_ruleset()
        else:
            raise ValueError(f'Invalid method to inform GPT: {inform_gpt_method!r}.')

    def read_literature(self, file_name: str = './pyrecodes/household/literature_summaries.json') -> None:
        summaries_json = read_json_file(file_name)
        summaries = ""
        for summary in summaries_json['Literature']:
            summaries += f"\n - {summary['paper']}\n  Findings: {summary['findings']}\n\n"
        content = self.prompts['ReadLiterature']['content'].replace('SUMMARIES', summaries)
        self.prompt_llm({'role': self.prompts['ReadLiterature']['role'], 'content': content}, print_answer=False)

    async def async_read_literature(self, file_name: str = './pyrecodes/household/literature_summaries.json') -> None:
        summaries_json = read_json_file(file_name)
        summaries = ""
        for summary in summaries_json['Literature']:
            summaries += f"\n - {summary['paper']}\n  Findings: {summary['findings']}\n\n"
        content = self.prompts['ReadLiterature']['content'].replace('SUMMARIES', summaries)
        await self.async_prompt_llm({'role': self.prompts['ReadLiterature']['role'], 'content': content}, print_answer=False)

    def read_ruleset(self) -> None:
        self.prompt_llm(self.prompts['ReadRuleset'], print_answer=False)

    async def async_read_ruleset(self) -> None:
        await self.async_prompt_llm(self.prompts['ReadRuleset'], print_answer=False)

    @staticmethod
    def split_text_into_batches(text: str, max_words: int = TEXT_WORDS_BATCH_SIZE):
        words = text.split()
        for i in range(0, len(words), max_words):
            yield " ".join(words[i:i + max_words])

    def prompt_llm(self, prompt: dict, print_answer: bool = False, add_to_past_experience: bool = False) -> str:
        return self.llm.prompt(prompt, print_answer=print_answer, add_to_past_experience=add_to_past_experience)

    async def async_prompt_llm(self, prompt: dict, print_answer: bool = False, add_to_past_experience: bool = False) -> str:
        return await self.llm.prompt_async(prompt, print_answer=print_answer, add_to_past_experience=add_to_past_experience)

    def get_decision(self, answer: str):
        words = answer.strip().split()
        if not words:
            return None
        decision_output = words[-1].strip(string.punctuation)
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

    def print_chat_history(self, text_width: int = 80) -> None:
        for msg in self.llm.chat_history:
            role = msg['role'].upper()
            print(f"{'─'*text_width}")
            print(f"  {role}")
            print(f"{'─'*text_width}")
            for line in msg['content'].splitlines():
                print(textwrap.fill(line, width=text_width) if line.strip() else '')
            print()


class LLM:
    """Wraps OpenAI GPT, maintaining chat history and prompt management."""

    def __init__(self, api_key_filename: str, temperature: float = 1.0, llm_model: str = 'GPT', summarize_experience: bool = True) -> None:
        self.chat_history = []
        self.relevant_prompts = []
        self.past_experience = []
        self.temperature = temperature
        self.summarize_experience = summarize_experience
        self.set_llm_model(llm_model, api_key_filename)
        self._lock = None

    def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    def set_llm_model(self, llm_model: str, api_key_filename: str) -> None:
        if llm_model != 'GPT':
            raise ValueError(f"Unsupported llm_model {llm_model!r}. Only 'GPT' is supported.")
        self.api_key = read_json_file(api_key_filename)['API_KEY']
        self.LLM_MODEL = GPT_MODEL
        self.llm_backend = 'openai'
        self.llm = openai.OpenAI(api_key=self.api_key)

    def prompt(self, prompt: dict, print_answer: bool = False, add_to_past_experience: bool = False) -> str:
        self.add_to_chat_history(prompt)
        messages = copy.deepcopy(self.relevant_prompts + [prompt])
        messages = self._sanitize_messages(messages)
        answer = self.query_llm(messages)
        if print_answer:
            print('--' * 20)
            print(answer)
            print('--' * 20)
        self.add_to_relevant_prompts(prompt)
        self.add_to_chat_history({'content': answer, 'role': 'assistant'})
        if add_to_past_experience:
            self.add_to_past_experience(answer)
        return answer

    async def prompt_async(self, prompt: dict, print_answer: bool = False, add_to_past_experience: bool = False) -> str:
        async with self._get_lock():
            self.add_to_chat_history(prompt)
            messages = copy.deepcopy(self.relevant_prompts + [prompt])
        messages = self._sanitize_messages(messages)
        answer = await self._query_llm_async(messages)
        if print_answer:
            print('--' * 20)
            print(answer)
            print('--' * 20)
        async with self._get_lock():
            self.add_to_relevant_prompts(prompt)
            self.add_to_chat_history({'content': answer, 'role': 'assistant'})
            if add_to_past_experience:
                self.add_to_past_experience(answer)
        return answer

            
    @staticmethod
    def _remove_surrogates(text: str) -> str:
        """Remove lone Unicode surrogates that make json.dumps produce invalid JSON."""
        return text.encode('utf-8', errors='ignore').decode('utf-8')

    def _sanitize_messages(self, messages):
        valid_roles = {'system', 'user', 'assistant', 'developer'}
        sanitized = []
        for msg in messages:
            role = msg.get('role', 'user')
            if role not in valid_roles:
                role = 'system'
            content = msg.get('content', '') or ''
            if not isinstance(content, str):
                content = str(content)
            content = self._remove_surrogates(content)
            sanitized.append({'role': role, 'content': content})
        return sanitized

    def query_llm(self, messages: list) -> str:
        for attempt in range(3):
            try:
                chat_completion = self.llm.chat.completions.create(
                    model=self.LLM_MODEL,
                    messages=messages,
                    temperature=self.temperature,
                )
                return chat_completion.choices[0].message.content
            except (openai.BadRequestError, openai.APIConnectionError, openai.APITimeoutError) as e:
                if attempt == 2:
                    raise
                print(f"[RETRY {attempt + 1}] {type(e).__name__}, retrying...")

    async def _query_llm_async(self, messages: list) -> str:
        return await asyncio.to_thread(self.query_llm, messages)

    def add_to_chat_history(self, prompt: dict) -> None:
        self.chat_history.append(prompt)

    def add_to_relevant_prompts(self, prompt: dict) -> None:
        if prompt['role'] in ('developer', 'system'):
            self.relevant_prompts.append(prompt)

    def add_to_past_experience(self, answer: str) -> None:
        self.past_experience.append({'role': 'assistant', 'content': f'\n - Latest Decision: \n ' + answer})

    def update_past_experience(self, description_prompt: dict, latest_answer: str) -> None:
        if self.summarize_experience:
            self._summarize_latest_experience(description_prompt, latest_answer)
        else:
            self._append_latest_experience(latest_answer)

    async def update_past_experience_async(self, description_prompt: dict, latest_answer: str) -> None:
        if self.summarize_experience:
            await self._summarize_latest_experience_async(description_prompt, latest_answer)
        else:
            self._append_latest_experience(latest_answer)

    def _summarize_latest_experience(self, description_prompt: dict, latest_answer: str) -> None:
        past_experience_string = self.past_experience[0] if self.past_experience else "None yet."
        content = description_prompt['content'].replace('PAST_EXPERIENCE', past_experience_string).replace('LATEST_ANSWER', latest_answer)
        summary = self.prompt({'role': 'user', 'content': content}, print_answer=False)
        if summary is None:
            print("Warning: LLM returned no summary of latest experience.")
            return
        self.past_experience = [summary.strip()]

    async def _summarize_latest_experience_async(self, description_prompt: dict, latest_answer: str) -> None:
        past_experience_string = self.past_experience[0] if self.past_experience else "None yet."
        content = description_prompt['content'].replace('PAST_EXPERIENCE', past_experience_string).replace('LATEST_ANSWER', latest_answer)
        summary = await self.prompt_async({'role': 'user', 'content': content}, print_answer=False)
        if summary is None:
            print("Warning: LLM returned no summary of latest experience.")
            return
        self.past_experience = [summary.strip()]

    def _append_latest_experience(self, latest_answer: str) -> None:
        self.past_experience.append(latest_answer.strip())

    def get_past_experience_string(self) -> str:
        if not self.past_experience:
            return ""
        if self.summarize_experience:
            return "\nYour past experience:\n" + self.past_experience[0]
        return "\nYour past experience:\n" + "\n".join(
            f" - Decision {i+1}: {exp}" for i, exp in enumerate(self.past_experience)
        )
