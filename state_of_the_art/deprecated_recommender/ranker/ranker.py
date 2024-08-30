import os
from typing import List

from state_of_the_art.config import config
from state_of_the_art.paper.arxiv_paper import ArxivPaper
from state_of_the_art.utils.llm.llm import LLM


class PaperRanker:
    def __init__(self):
        self._enable_abstract_in_ranking = False

    def rank(self, *, articles: List[ArxivPaper], dry_run=False):
        """
        Ranks existing papers by relevance
        """
        if not articles:
            raise Exception(
                "Arrived at paper ranker with no articles to rank. Did you mine new papers?"
            )

        prompt = self.get_prompt()

        if dry_run:
            print(prompt)

        articles_str = self._format_input_articles(articles)

        if "PRINT_PAPERS_INPUT" in os.environ:
            print(articles_str)
            return "Dry run result"

        if dry_run:
            return "Dry run result"

        result = LLM().call(
            prompt,
            articles_str,
            expected_ouput_len=4000,
            mock_content="A paper: http://arxiv.org/abs/2206.12048v1",
        )
        return result

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
Published: {i.published_date_str()}
{abstract_row}
"""
            counter += 1
        return papers_str

    def get_prompt(self) -> str:
        prompts = {
            "default": f"""You are an world class expert in Data Science and computer science.
Your task is spotting key insights of what is going on in academia an in the industry via arxiv articles provided to you.
Highlight only topics that are exciting or import for your target audience

##start of target audience 
{config.get_current_audience().get_preferences()}
##end of target audience

Try also to include meta-analysis and reviews of the field.

Articles to rank
The articles for you to work with will be provided below in the following format (Title, Abstract, URL)
##start
{{text}}
##end of articles

Example of expected output format: ##start

(0.9) Title: "the title" 
Arxiv URL: the article url
Relevance: Relevant because it presents a new approach to .. 

(0.7) Title: "the title 2"
Relevance: "Relevant because it presents a new ... "
Arxiv URL: the article url
## end of example

the order they are provided is not optimized, figure out the best order to present them to your audience.
Do not be biased by the given order of the papers, it does not mean more recent is more relevant.
Sort the papers from most relevant to less, return  {config.get_max_articles_to_return_rank()} ranked papers

Ranked output of articles: ##start """,
            "curiosity": f"""You are an world class expert in Data Science and computer science.            
Your task is ranking unsuaual, curious and interesting papers of what is going on in academia an in the industry via arxiv articles provided to you.            
Highlight only topics that are exciting to your target audience. Bring diverse topics and ideas, from diffent places and fields.
            
##start of target audience             
{config.get_current_audience().get_preferences(include_keywords_to_exclude=False)}            
##end of target audience            
            
Articles to rank            
The articles for you to work with will be provided below in the following format (Title, Abstract, URL)            
##start            
{{text}}            
##end of articles            
            
Example of expected output format: ##start

(0.9) Title: "the title" 
Arxiv URL: the article url
Why its curious?: Because it presents a new approach to .. 

(0.7) Title: "the title 2"
Relevance: "Relevant because it presents a new ... "
Arxiv URL: the article url
Why its curious?: Because it show that folks in china are ...
## end of example

The order they are provided is not optimized, figure out the best order to present them to your audience.            
Do not be biased by the given order of the papers, it does not mean more recent is more curious.            
There can be thousands of papers so do not only recommend the top ones, the best could also be in the middle.
Sort the papers from most curious to less, return  {config.get_max_articles_to_return_rank()} ranked papers            
            
Ranked output of articles: ##start """,
        }

        rank_prompt = os.environ.get("SOTA_RANK_PROMPT", "default")
        print(f"Using rank prompt: {rank_prompt}")

        return prompts[rank_prompt]


if __name__ == "__main__":
    import fire

    fire.Fire()
