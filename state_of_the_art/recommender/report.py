from typing import Optional

from datetime import datetime
from state_of_the_art.paper.format_papers import PapersFormatter
from state_of_the_art.paper.papers_data import PapersInDataWharehouse
from state_of_the_art.paper.url_extractor import PapersUrlsExtractor
from state_of_the_art.recommender.ranker.rank_data import RankGeneratedData
from state_of_the_art.register_papers.arxiv_miner import PaperMiner
from state_of_the_art.recommender.ranker.ranker import PaperRanker
from state_of_the_art.recommender.report_parameters import RecommenderParameters
from state_of_the_art.recommender.reports_data import ReportsData
import sys
from state_of_the_art.config import config

from state_of_the_art.recommender.topic_based.topic_search import TopicSearch
from state_of_the_art.utils import pdf
from state_of_the_art.utils.mail import Mail
import state_of_the_art.utils.pdf


class RecommenderReport():
    """
    Class responsible to the entire generation pipeline
    """

    def generate(self, *, number_lookback_days=None, from_date=None, to_date=None, skip_register=False, dry_run=False,
                 batch=1, batch_size=None, max_papers_per_query=None, papers_to_rank=None, query: Optional[str] = None,
                 topic_dive: Optional[str] = None, description_from_clipboard=False):
        """
        The main entrypoint of the application does the entire cycle from registering papers to ranking them
        """

        parameters = RecommenderParameters(lookback_days=number_lookback_days, from_date=from_date, to_date=to_date,
                                           skip_register=skip_register, dry_run=dry_run, batch=batch,
                                           batch_size=batch_size, papers_to_rank=papers_to_rank, query=query,
                                           topic_dive=topic_dive, description_from_clipboard=description_from_clipboard)

        if not skip_register:
            PaperMiner().register_new(dry_run=dry_run, max_papers_per_query=max_papers_per_query)
        else:
            print("Skipping registering papers")

        result = self._rank(parameters)
        self._format_results(result, parameters)

        return result

    def _rank(self, parameters: RecommenderParameters) -> str:

        if parameters.topic_dive:
            return TopicSearch().search_by_topic(parameters.topic_dive)

        if parameters.query:
            return TopicSearch().extract_query_and_search(parameters.query)

        if parameters.description_from_clipboard:
            import subprocess
            output = subprocess.getoutput('clipboard get_content')
            print("Clipboard content: ", output)
            return TopicSearch().extract_query_and_search(output)

        if not sys.stdin.isatty():
            print("Reading from stdin")
            stdindata = sys.stdin.readlines()
            stdindata = "\n".join(stdindata)
            return TopicSearch().extract_query_and_search(stdindata)

        self._input_articles = PapersInDataWharehouse().get_latest_articles(lookback_days=parameters.lookback_days,
                                                                from_date=parameters.from_date,
                                                                batch=parameters.batch,
                                                                batch_size=parameters.batch_size)
        print(f"Found {len(self._input_articles)} articles")

        if len(self._input_articles) == 0:
            return "No articles found"

        result = PaperRanker().rank(articles=self._input_articles, parameters=parameters)

        return result

    def _format_results(self, result, parameters):
        formatted_result = PapersFormatter().from_str(result)
        profile_name = config.get_current_audience().name.upper()

        now = datetime.now().isoformat()
        header = f"Results generated at {now} for profile: \"{profile_name}\" for period ({parameters.from_date}, {parameters.to_date}) analysed {len(self._input_articles)} papers: \n\n"
        result = header + result
        formatted_result = header + formatted_result
        papers_str = PapersInDataWharehouse().papers_to_urls_str(PapersInDataWharehouse().df_to_papers(self._input_articles))

        ranking_data = RankGeneratedData(from_date=parameters.from_date, to_date=parameters.to_date, prompt='',
                                         summary=formatted_result, llm_result=result, papers_analysed=papers_str)
        config.get_datawarehouse().write_event('state_of_the_art_summary', ranking_data.to_dict())

        print("Sending email")
        pdf.create_pdf(formatted_result, f'/tmp/sota_summary.pdf')

        Mail().send(formatted_result, f'Sota summary batch {parameters.batch} at {now} for profile {profile_name}')

    def _load_papers_from_str(self, papers_str: str):
        urls = PapersUrlsExtractor().extract_urls(papers_str)

        return PapersInDataWharehouse().load_from_urls(urls, fail_on_missing_ids=False)

    def latest(self):
        return ReportsData().get_latest_summary()
