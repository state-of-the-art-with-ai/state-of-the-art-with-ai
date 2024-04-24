import datetime
import os
from typing import List

from state_of_the_art.config import config
from state_of_the_art.paper.format_papers import PapersFormatter
from state_of_the_art.paper.paper import Paper
from state_of_the_art.paper.papers_data import PapersInDataWharehouse
from state_of_the_art.paper.text_extractor import PapersUrlsExtractor
from state_of_the_art.llm import LLM
from state_of_the_art.ranker.rank_generated_data import RankGeneratedData
from state_of_the_art.report.report_parameters import RecommenderParameters
from state_of_the_art.utils.mail import Mail

class PaperRanker:
    MAX_ARTICLES_TO_RETURN = 25

    def __init__(self):
        self._enable_abstract_in_ranking = False
    def rank(self, *, articles: List[Paper], parameters: RecommenderParameters, dry_run=False):
        """
        Ranks existing papers by relevance
        """
        prompt = self.get_prompt()

        if dry_run:
            print(prompt)

        articles_str = self.get_articles_str(articles)

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
        print("Writing event")
        config.get_datawarehouse().write_event('state_of_the_art_summary', ranking_data.to_dict())

        print("Sending email")
        Mail().send(formatted_result, f'Sota summary batch {parameters.batch} at {now} for profile {profile_name}')

        return formatted_result

    def get_articles_str(self, papers)->str:
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

        The articles for you to work with will be provided below in the following format (Title, Abstract, URL)
        the order they are provided is not optimized, figure out the best order to present them to your audience.
        Do not be biased by the given order of the papers, it does not mean more recent is more relevant.
        Sort the papers from most relevant to less, return not more than a single page of results
        Try also to include meta-analysis and reviews of the field.

        Example of expected output format: ##start

        (0.9) Title: "A new approach to ml pipeline testing" 
        Arxiv URL: the article url
        Relevance: Relevant because it presents a new approach to testing pipelines and could change how production systems are built.

        (0.7) Title: "a new mixed of experts llm breaking bechmarks"
        Relevance: "Relevant because it presents a new large language model that could be used to improve quality and speed of delivery of recommendation system"
        Arxiv URL: the article url
        ## end of example

        Articles to rank
        ##start
        {{text}}
        ##end of articles

        Ranked output of articles: ##start """


if __name__ == "__main__":
    import fire
    fire.Fire()
