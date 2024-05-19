from state_of_the_art.config import config


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


def calculate_cost(
    *, chars_input=None, chars_output=None, tokens_input=None, tokens_output=None
):
    if chars_input is not None:
        tokens_input = chars_input / 4
    if chars_output is not None:
        tokens_output = chars_output / 4

    model = config.GPT_MODEL
    input_cost_per_million = open_ai_cost[model]["input_cost_per_million"]
    output_cost_per_million = open_ai_cost[model]["output_cost_per_million"]

    input_cost = (tokens_input / 1000000) * input_cost_per_million
    output_cost = (tokens_output / 1000000) * output_cost_per_million
    print(f"Input cost {input_cost} for {tokens_input} tokens ({chars_input} chars)")
    print(
        f"Output cost {output_cost} for {tokens_output} tokens ({chars_output} chars)"
    )

    return input_cost + output_cost


open_ai_cost = {
    "gpt-4-turbo-preview": {
        "input_cost_per_million": 10,
        "output_cost_per_million": 30,
    },
    "gpt-4o": {
        "input_cost_per_million": 5,
        "output_cost_per_million": 15,
    },
}
