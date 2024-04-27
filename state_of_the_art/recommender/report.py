from typing import Optional

from state_of_the_art.paper.papers_data import PapersInDataWharehouse
from state_of_the_art.paper.url_extractor import PapersUrlsExtractor
from state_of_the_art.register_papers.arxiv_miner import PaperMiner
from state_of_the_art.recommender.ranker.ranker import PaperRanker
from state_of_the_art.recommender.report_parameters import RecommenderParameters
from state_of_the_art.recommender.reports_data import ReportsData
import sys

from state_of_the_art.recommender.topic_based.topic_search import TopicSearch

class RecommenderReport():
    """
    Class responsible to the entire generation pipeline
    """

    def generate(self, *, number_lookback_days=None, from_date=None, to_date=None, skip_register=False, dry_run=False,
                 batch=1, batch_size=None, max_papers_per_query=None, papers_to_rank=None, query: Optional[str] = None, topic_dive: Optional[str] = None):
        """
        The main entrypoint of the application does the entire cycle from registering papers to ranking them
        """

        parameters = RecommenderParameters(lookback_days=number_lookback_days, from_date=from_date, to_date=to_date,
                                           skip_register=skip_register, dry_run=dry_run, batch=batch,
                                           batch_size=batch_size, papers_to_rank=papers_to_rank, query=query, topic_dive=topic_dive)

        if not skip_register:
            PaperMiner().register_new(dry_run=dry_run, max_papers_per_query=max_papers_per_query)
        else:
            print("Skipping registering papers")

        result = self._rank(parameters)

        return result

    def _rank(self, parameters: RecommenderParameters) -> str:

        if parameters.topic_dive:
            return TopicSearch().search_by_topic(parameters.topic_dive)

        if parameters.query:
            return TopicSearch().search_with_query(parameters.query)

        if parameters.papers_to_rank:
            articles = self._load_papers_from_str(parameters.papers_to_rank)
        elif not sys.stdin.isatty():
            print("Reading from stdin")
            stdindata = sys.stdin.readlines()
            stdindata = "\n".join(stdindata)
            articles = self._load_papers_from_str(stdindata)
        else:
            articles = PapersInDataWharehouse().get_latest_articles(lookback_days=parameters.lookback_days,
                                                                    from_date=parameters.from_date,
                                                                    batch=parameters.batch,
                                                                    batch_size=parameters.batch_size)
            print(f"Found {len(articles)} articles")

        if len(articles) == 0:
            return "No articles found"

        result = PaperRanker().rank(articles=articles, parameters=parameters)
        return result

    def _load_papers_from_str(self, papers_str: str):
        urls = PapersUrlsExtractor().extract_urls(papers_str)

        return PapersInDataWharehouse().load_from_urls(urls, fail_on_missing_ids=False)

    def latest(self):
        return ReportsData().get_latest_summary()
