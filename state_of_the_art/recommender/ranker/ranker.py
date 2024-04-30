import datetime
import os
from typing import List

from state_of_the_art.config import config
from state_of_the_art.paper.format_papers import PapersFormatter
from state_of_the_art.paper.paper import Paper
from state_of_the_art.paper.papers_data import PapersInDataWharehouse
from state_of_the_art.utils.llm import LLM
from state_of_the_art.recommender.ranker.rank_data import RankGeneratedData
from state_of_the_art.recommender.report_parameters import RecommenderParameters
from state_of_the_art.utils.mail import Mail

class PaperRanker:

    def __init__(self):
        self._enable_abstract_in_ranking = False
    def rank(self, *, articles: List[Paper], parameters: RecommenderParameters, dry_run=False):
        """
        Ranks existing papers by relevance
        """
        prompt = self.get_prompt()

        if dry_run:
            print(prompt)

        articles_str = self._format_input_articles(articles)

        if 'PRINT_PAPERS_INPUT' in os.environ:
            print(articles_str)
            return "Dry run result"

        if dry_run:
            return "Dry run result"

        result = LLM().call(prompt, articles_str, expected_ouput_len=4000)
        formatted_result = PapersFormatter().from_str(result)
        profile_name = config.get_current_audience().name.upper()

        now = datetime.datetime.now().isoformat()
        header = f"Results generated at {now} for profile: \"{profile_name}\" for period ({parameters.from_date}, {parameters.to_date}) analysed {len(articles)} papers: \n\n"
        result = header + result
        formatted_result = header + formatted_result
        papers_str = PapersInDataWharehouse().papers_to_urls_str(PapersInDataWharehouse().df_to_papers(articles))

        ranking_data = RankGeneratedData(from_date=parameters.from_date, to_date=parameters.to_date, prompt=prompt, summary=formatted_result, llm_result=result, papers_analysed=papers_str)
        config.get_datawarehouse().write_event('state_of_the_art_summary', ranking_data.to_dict())

        print("Sending email")
        Mail().send(formatted_result, f'Sota summary batch {parameters.batch} at {now} for profile {profile_name}')

        return formatted_result

    def _format_input_articles(self, papers)->str:
        papers_str = " "
        counter = 1
        for i in papers.iterrows():
            abstract_row =   f'Abstract: {i[1]['abstract'][0:config.MAX_ABSTRACT_SIZE_RANK]}' if self._enable_abstract_in_ranking else ''
            papers_str += f"""
{counter}. Title: {i[1]['title']}
Arxiv URL: {i[1]['url']}
Published: {i[1]['published']}
{abstract_row}
"""
            counter += 1
        return papers_str
    def get_prompt(self):
        return f"""You are an world class expert in Data Science and computer science.
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

Ranked output of articles: ##start """


if __name__ == "__main__":
    import fire
    fire.Fire()
