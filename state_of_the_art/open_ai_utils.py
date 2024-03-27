

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

