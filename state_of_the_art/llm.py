import os
import sys
from state_of_the_art.config import config

open_ai_cost = {
    'gpt-4-turbo-preview': {
        'input_cost_per_million': 10,
        'output_cost_per_million': 30,
    },
}



def calculate_cost(*, chars_input=None, chars_output=None, tokens_input=None, tokens_output=None):
    if chars_input is not None:
        tokens_input = chars_input / 4
    if chars_output is not None:
        tokens_output = chars_output / 4

    model = 'gpt-4-turbo-preview'
    input_cost_per_million = open_ai_cost[model]['input_cost_per_million']
    output_cost_per_million = open_ai_cost[model]['output_cost_per_million']

    input_cost = (tokens_input / 1000000) * input_cost_per_million
    output_cost = (tokens_output / 1000000) * output_cost_per_million

    return input_cost + output_cost


def call_chatgpt(prompt_str: str, input_str: str) -> str:
        from langchain_community.chat_models import ChatOpenAI
        from langchain import PromptTemplate, LLMChain

        prompt_template = PromptTemplate(template=prompt_str, input_variables=["text"])
        llm = ChatOpenAI(temperature=0.0, model=config.sort_papers_gpt_model, openai_api_key=config.open_ai_key)
        chain =LLMChain(llm=llm, prompt=prompt_template)
        # two weeks ago

        return chain.run(input_str)


class LLM:
    """Wrapper for llm call """

    def __init__(self, mock=False):

        self.mock = mock

        if 'LLM_MOCK' in os.environ:
            print("LLM mock enabled via enviroment variable")
            self.mock = True


    def call(self, prompt, input, expected_ouput_len=4000, ask_cost_confirmation=True):
        if self.mock:
            return f"""Mocked llm return
INPUT: {input}
PROMPT: {prompt[0:200]}...
            """

        self._cost_check(prompt, input, expected_ouput_len, ask_cost_confirmation)


        return call_chatgpt(prompt, input)

    def _cost_check(self, prompt, input, expected_ouput_len=4000, ask_cost_confirmation=True):
        if ask_cost_confirmation:
            expected_cost = calculate_cost(chars_input=len(input) + len(prompt), chars_output=expected_ouput_len)
            if expected_cost < 0.5:
                print("Cost is low {}, continuing without asking for confirmation".format(expected_cost))
                return

            user_input = input(f"Do you want ton continue to call the AI at a cost of $ {expected_cost}? Type c to continue \n")

            if user_input != 'c':
                print("Aborting")
                sys.exit(1)
