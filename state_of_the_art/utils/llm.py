import os
import sys
from typing import Optional

from state_of_the_art.config import config

open_ai_cost = {
    "gpt-4-turbo-preview": {
        "input_cost_per_million": 10,
        "output_cost_per_million": 30,
    },
}


def calculate_cost(
    *, chars_input=None, chars_output=None, tokens_input=None, tokens_output=None
):
    if chars_input is not None:
        tokens_input = chars_input / 4
    if chars_output is not None:
        tokens_output = chars_output / 4

    model = "gpt-4-turbo-preview"
    input_cost_per_million = open_ai_cost[model]["input_cost_per_million"]
    output_cost_per_million = open_ai_cost[model]["output_cost_per_million"]

    input_cost = (tokens_input / 1000000) * input_cost_per_million
    output_cost = (tokens_output / 1000000) * output_cost_per_million
    print(f"Input cost {input_cost} for {tokens_input} tokens ({chars_input} chars)")
    print(
        f"Output cost {output_cost} for {tokens_output} tokens ({chars_output} chars)"
    )

    return input_cost + output_cost


def call_chatgpt(prompt_str: str, input_str: str) -> str:
    from langchain_community.chat_models import ChatOpenAI
    from langchain import PromptTemplate, LLMChain

    prompt_template = PromptTemplate(template=prompt_str, input_variables=["text"])
    llm = ChatOpenAI(
        temperature=0.0, model=config.GPT_MODEL, openai_api_key=config.OPEN_API_KEY
    )
    chain = LLMChain(llm=llm, prompt=prompt_template)
    # two weeks ago

    return chain.run(input_str)


class LLM:
    """Wrapper for llm call"""

    def call(
        self,
        prompt: str,
        prompt_input: str,
        expected_ouput_len=4000,
        ask_cost_confirmation=True,
        mock_content: Optional[str] = None,
    ) -> str:
        if not prompt:
            raise Exception("Prompt is empty")
        if not prompt_input:
            raise Exception("Prompt input is empty")

        if "LLM_MOCK" in os.environ or "SOTA_TEST" in os.environ:
            if mock_content:
                return mock_content
            else:
                return f"""Mocked llm return
    Prompt: {prompt[0:50]}
    Input: {prompt_input[0:50]}
                """

        if "PRINT_PROMPT" in os.environ:
            print("Prompt: ")
            print(prompt)

            print("Input now: ")
            print(prompt_input)

        self._cost_check(
            prompt, prompt_input, expected_ouput_len, ask_cost_confirmation
        )

        return call_chatgpt(prompt, prompt_input)

    def _cost_check(
        self,
        prompt: str,
        prompt_input: str,
        expected_ouput_len=4000,
        ask_cost_confirmation=True,
    ):
        if ask_cost_confirmation:
            expected_cost = calculate_cost(
                chars_input=len(prompt_input) + len(prompt),
                chars_output=expected_ouput_len,
            )
            if expected_cost < config.MINIMAL_CONFIRMATION_COST:
                print(
                    "Cost is low {}, continuing without asking for confirmation".format(
                        expected_cost
                    )
                )
                return

            user_input = input(
                f"Do you want ton continue to call the AI at a cost of $ {expected_cost}? Type c to continue \n"
            )

            if user_input != "c":
                print("Aborting")
                sys.exit(1)
