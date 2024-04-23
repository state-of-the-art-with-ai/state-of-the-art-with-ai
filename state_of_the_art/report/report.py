from typing import Optional

from state_of_the_art.paper.papers_data import Papers
from state_of_the_art.paper.text_extractor import PapersUrlsExtractor
from state_of_the_art.paper_miner.arxiv_miner import PaperMiner
from state_of_the_art.ranker.paper_ranker import PaperRanker
from state_of_the_art.report.report_parameters import ReportParemeters
from state_of_the_art.report.reports_data import ReportsData
import sys

class Report():
    """
    Class responsible to the entire generation pipeline
    """
    def generate(self, *, lookback_days=None, from_date=None, to_date=None, skip_register=False, dry_run=False, batch=1, max_papers_per_query=None):
        """
        The main entrypoint of the application does the entire cycle from registering papers to ranking them
        """

        if not skip_register:
            PaperMiner().register_new(dry_run=dry_run, max_papers_per_query=max_papers_per_query)
        else:
            print("Skipping registering papers")

        result =self.rank(lookback_days=lookback_days, from_date=from_date, to_date=to_date, skip_register=skip_register, dry_run=dry_run, batch=batch)

        return result

    def rank(self, *, lookback_days=None, from_date=None, to_date=None, skip_register=False, dry_run=False, batch=1, given_data:Optional[str]=None) -> str:
        parameters = ReportParemeters(lookback_days=lookback_days, from_date=from_date, to_date=to_date, skip_register=skip_register, dry_run=dry_run, batch=batch)
        if given_data:
            articles  = self._load_papers_from_str(given_data)
        elif not sys.stdin.isatty():
            print("Reading from stdin")
            stdindata = sys.stdin.readlines()
            stdindata = "\n".join(stdindata)
            articles  = self._load_papers_from_str(stdindata)
        else:
            articles = Papers().get_latest_articles(lookback_days=lookback_days, from_date=from_date, batch=batch)
            print(f"Found {len(articles)} articles")

        if len(articles) == 0:
            return "No articles found"

        result = PaperRanker().rank(articles=articles, parameters=parameters)
        return result

    def _load_papers_from_str(self, papers_str: str):
        urls = PapersUrlsExtractor().extract_urls(papers_str)

        return Papers().load_from_urls(urls, fail_on_missing_ids=False)

    def latest(self):
        return ReportsData().get_latest_summary()


