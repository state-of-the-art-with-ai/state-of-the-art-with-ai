import datetime
from typing import Optional

from state_of_the_art.config import config
from state_of_the_art.paper.presenter import PaperHumanPresenter
from state_of_the_art.papers import PapersData, PapersFormatter, PapersExtractor
from state_of_the_art.llm import LLM
from state_of_the_art.ranker.rank_generated_data import RankGeneratedData
from state_of_the_art.utils.mail import Mail


class PaperRanker:
    MAX_ARTICLES_TO_RETURN = 25

    def rank(self, *, from_date: Optional[str]=None, to_date: Optional[str]=None, lookback_days=None, dry_run=False, article_slices=None, batch=1):
        """
        Ranks existing papers by relevance
        """
        if not to_date and not lookback_days:
            lookback_days = config.DEFAULT_LOOK_BACK_DAYS

        max_papers = config.sort_papers_max_to_compute
        if not article_slices:
            article_slices = (max_papers * (batch - 1), max_papers * batch)


        print("Article slices ", article_slices)
        print("Look back days ", lookback_days)

        prompt = f"""You are an world class expert in Data Science and computer science.
Your task is spotting key insights of what is going on in academia an in the industry via arxiv articles provided to you..
Highlight only topics that are exciting or import for yoru target audience
    
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

        if dry_run:
            print(prompt)

        # two weeks ago
        from_date = from_date if from_date else (datetime.date.today() - datetime.timedelta(days=lookback_days)).isoformat()
        to_date = to_date if to_date else datetime.date.today().isoformat()

        articles = PapersData().load_between_dates(from_date, to_date)
        amount_of_articles = len(articles)
        print("Found  ", amount_of_articles, f" articles with date filters but filtering down to {max_papers} ")

        if amount_of_articles < max_papers:
            article_slices = (0, amount_of_articles)
        print("Slicing articles ", article_slices)

        articles = articles[article_slices[0]:article_slices[1]]
        articles_str = self.get_articles_str(articles)

        if dry_run:
            return "Dry run result"

        result = LLM().call(prompt, articles_str, expected_ouput_len=4000)

        now = datetime.datetime.now().isoformat()
        header = f"Results generated at {now} for period ({from_date}, {to_date}) analysed {amount_of_articles} papers: \n\n"
        result = header + result

        urls = PapersExtractor().extract_urls(result)
        formatted_result = ""
        counter = 1
        for url in urls:
            presenter = PaperHumanPresenter(url)
            formatted_result+= f"{counter}. {presenter.present()} \n\n"
            counter = counter + 1

        formatted_result = header + formatted_result

        papers_str = PapersFormatter().papers_urls(PapersData().df_to_papers(articles))

        ranking_data = RankGeneratedData(from_date=from_date, to_date=to_date, prompt=prompt, summary=formatted_result, llm_result=result, papers_analysed=papers_str)
        print("Writing event")
        config.get_datawharehouse().write_event('state_of_the_art_summary', ranking_data.to_dict())

        print("Sending email")
        Mail().send(formatted_result, f'Sota summary batch {batch} at {now}')

        return formatted_result

    def get_articles_str(self, papers)->str:
        papers_str = " "
        for i in papers.iterrows():
            papers_str += f"""
    Title: {i[1]['title']}
    Abstract: {i[1]['abstract'][0:config.MAX_ABSTRACT_SIZE_RANK]}
    Arxiv URL: {i[1]['url']}
            """
        return papers_str


if __name__ == "__main__":
    import fire
    fire.Fire()
