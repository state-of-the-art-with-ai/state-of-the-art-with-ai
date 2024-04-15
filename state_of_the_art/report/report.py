from state_of_the_art.paper.papers_data import PapersData
from state_of_the_art.paper.text_extractor import PapersUrlsExtractor
from state_of_the_art.paper_miner.arxiv import ArxivMiner
from state_of_the_art.ranker.paper_ranker import PaperRanker
from state_of_the_art.report.report_parameters import ReportParemeters
from state_of_the_art.report.reports_data import ReportsData
import sys

class Report():
    """
    Class responsible to the entire generation pipeline

    """
    def __init__(self):
        pass
    def generate(self, *, lookback_days=None, from_date=None, to_date=None, skip_register=False, dry_run=False, batch=1):
        """
        The main entrypoint of the application does the entire cycle from registering papers to ranking them
        """
        parameters = ReportParemeters(lookback_days=lookback_days, from_date=from_date, to_date=to_date, skip_register=skip_register, dry_run=dry_run, batch=batch)

        if not skip_register:
            ArxivMiner().register_new_papers(dry_run=dry_run)
        else:
            print("Skipping registering papers")


        if not sys.stdin.isatty():
            print("Reading from stdin")
            data = sys.stdin.readlines()
            text = "".join(data)
            urls = PapersUrlsExtractor().extract_urls(text)
            articles = PapersData().load_from_urls(urls)
            print(urls)
        else:
            articles = PapersData().get_latest_articles(lookback_days=lookback_days, from_date=from_date, batch=batch)
        print(f"Found {len(articles)} articles")
        if len(articles) == 0:
            return "No articles found"

        result = PaperRanker().rank(articles=articles, parameters=parameters)

        return result

    def latest(self):
        return ReportsData().get_latest_summary()


