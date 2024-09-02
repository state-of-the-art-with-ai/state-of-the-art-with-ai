import os
import json
from typing import List

from state_of_the_art.config import config
from state_of_the_art.insight_extractor.insight_extractor import SupportedModels
from state_of_the_art.paper.arxiv_paper import ArxivPaper
from openai import OpenAI


class StructuredPaperRanker:
    def __init__(self):
        self.model_to_use = None
        self._enable_abstract_in_ranking = False
        self.profile = config.get_current_audience()

    def rank(self, *, articles: List[ArxivPaper], dry_run=False):
        if os.environ.get("SOTA_TEST"):
            return "Mocked result", {}

        client = OpenAI(api_key=config.OPEN_API_KEY)
        used_model = (
            self.model_to_use
            if self.model_to_use
            else SupportedModels.gpt_4o_mini.value
        )
        print("Using model: ", used_model)
        result = client.chat.completions.create(
            model=used_model,
            messages=[
                {"role": "user", "content": self._format_input_articles(articles)}
            ],
            # temperature=1.5,
            functions=[
                {
                    "name": "get_insights_from_paper",
                    "description": f"""This selects the best papers from a list of papers to rank.
It optimized for the following audience: {self.profile.get_preferences()[0:300]}

The order they are provided is not optimized, figure out the best order to present them to your audience.
Do not be biased by the given order of the papers, it does not mean more recent is more relevant.
Sort the papers from most relevant to less. You cannot return all papers so pick only the best first.

""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ranked_articles": {
                                "type": "array",
                                "max_items": config.get_max_articles_to_return_rank(),
                                "min_items": config.get_max_articles_to_return_rank(),
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "paper_title": {"type": "string"},
                                        "url": {"type": "string"},
                                        "published_date": {"type": "string"},
                                        "why_relevant": {"type": "string"},
                                        "insitution": {"type": "string"},
                                    },
                                },
                            }
                        },
                    },
                }
            ],
            function_call="auto",
        )

        if not hasattr(result.choices[0].message, "function_call"):
            raise Exception(
                f"""Function call extraction operation failed returned {result.choices[0].message.content} instead """
            )

        structured_results = result.choices[0].message.function_call.arguments
        structured_results = json.loads(str(structured_results))
        print(json.dumps(structured_results, indent=3))
        return str(structured_results), structured_results

    def _format_input_articles(self, papers: List[ArxivPaper]) -> str:
        papers_str = " "
        counter = 1
        for i in papers:
            abstract_row = (
                f"Abstract: {i.abstract[0:config.MAX_ABSTRACT_SIZE_RANK]}"
                if self._enable_abstract_in_ranking
                else ""
            )
            papers_str += f"""
{counter}. Title: {i.title}
Arxiv URL: {i.abstract_url}
Published Date: {i.published_date_str()}
{abstract_row}
"""
            counter += 1
        print("input: ", papers_str)
        return papers_str
