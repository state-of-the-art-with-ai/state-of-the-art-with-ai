
from state_of_the_art.utils.clipboard import get_clipboard_content
from state_of_the_art.utils.llm.llm import LLM


def generate_headline_from_clipboard():

    prompt = """You are a headline creator for a newlstter about ai for Jean Carlo machado.
You will be given the content of the episode and you generate the highlights based on the paper title keywords that will drive most clicks.
The maximum amount of chars is 196. If you need to pick specific papers, pick the most interesting ones while keeping the output diverse

Here are some examples of successful past headlines:
1. Exploring the 4 stages of inference, cross-lingual sentiment analysis, the dynamics of auto bidding systems, cross-channel bidding, sequence recommendations modelling, a participatory approach to AI
2. Long-Term Planning, Causal Inference, Lifelong Learning, Misinformation Modeling, Neural Networks, Data Science Success, and Python for Deep Learning
3. Exploring Ethics, Mechanisms, and Innovations in AI Network Design and General Intelligence
4. Collaborative Ensemble Strategies, Complete Non-overlapping Category Extraction, NN Evaluation without Actuals, Hallucination risk detection, Causal Reasoning in LLMs, and Bias Correction in MMM




Now follows the content:
{text}

Now follows your given headline: """
    content = get_clipboard_content()

    return LLM().call(prompt=prompt, prompt_input=content)