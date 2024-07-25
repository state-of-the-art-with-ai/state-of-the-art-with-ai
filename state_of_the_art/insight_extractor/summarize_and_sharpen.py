from state_of_the_art.utils.llm.llm import LLM


class Sharpen:
    def perform(self, base_text=None, question=None) -> str:
        if not base_text:
            import sys

            data = sys.stdin.readlines()
            base_text = "".join(data)

        question_prompt = ""
        if question:
            question_prompt = (
                f"""Additionally answer the following question: {question} """
            )

        prompt = f"""You are an expert summarizer you get some input and summarize it to its essence removing any uncesseary language.
You prefer bullet points than long text explanations. The text imput is always being referred to a paper being reviwed. 
If words among the base text are redundant rework the senteces and reduce them when possible to convey the whole information in shorter form
Also remove any  special characters mmeant to change the formatting via markdown.
We want ot highlight only the essential topics of the paper. If there are too details we should skip them. Also prefer information that might be actionalble.
9k

Some examples of great summaries are:

1. LLMs show a large variance in their ability to replicate human judgments across different datasets. All models under evaluation achieve better alignment with human judgments when evaluating human language than when assessing machine-generated text.
2. Small Multilingual Language Models (SMLMs) like XLM-R and mT5 outperform larger English-centric LLMs in zero-shot cross-lingual sentiment analysis. This means they can better handle sentiment analysis tasks in multiple languages without additional training data in those languages.
3.  Autobidding systems can exhibit complex behaviors like bi-stability, periodic orbits, and quasi-periodicity.
4. NOAH is a practical example how one can can optimise marketing actions across different channels and products, leading to significant business improvements

Now follow the input to be summarized:
Input: <textStart>{{text}}</textEnd>

{question_prompt}

Now your answer follows:
<summaryStart>"""
        result = LLM().call(prompt, base_text)
        print("Result:")

        return result

    def perform_from_clipboard(self, question=None):
        from python_search.apps.clipboard import Clipboard

        content = Clipboard().get_content()
        return self.perform(content, question=question)
