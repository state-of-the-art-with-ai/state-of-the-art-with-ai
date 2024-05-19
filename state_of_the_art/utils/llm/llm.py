import os
import sys
from typing import Optional

from state_of_the_art.config import config
from state_of_the_art.utils.llm.gpt_openai import call_chatgpt, calculate_cost
from state_of_the_art.utils.llm.mistral import Mistral

class LLM:
    """Wrapper for llm call"""
    def __init__(self, model_type='openai'):
        self.model_type = 'mistral' if os.environ.get('USE_MISTRAL') else model_type

        if self.model_type == 'openai':
            self.call_llm = call_chatgpt
        if self.model_type == 'mistral':
            self.call_llm = Mistral().call_llm
        print(f"Using model {self.model_type}")


    def call(
        self,
        prompt: str,
        prompt_input: str,
        expected_ouput_len=4000,
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

        if self.model_type == 'openai':
            self._cost_check(
                prompt, prompt_input, expected_ouput_len
            )

        return self.call_llm(prompt, prompt_input)

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
