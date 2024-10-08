from state_of_the_art.container_startup import ContainerStartup
from state_of_the_art.paper.downloader import PaperDownloader
from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.insight_extractor.insight_extractor import AIInsightsExtractor

from state_of_the_art.recommenders.interest_recommender.interest_recommender_generator import (
    InterestPaperRecommender,
)
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
from state_of_the_art.review import ReportReview
from state_of_the_art import scheduler
from state_of_the_art.ci_cd import Cli
from state_of_the_art.search.bm25_search import PrecomputedSearch
from state_of_the_art.tables.tables import Table


class Sota:
    """
    State of the art via ai main entry script
    """

    def __init__(self):
        self.papers = PapersLoader()
        self.InsightExtractor = AIInsightsExtractor
        self.downloader = PaperDownloader
        self.ArxivMiner = ArxivMiner
        self.ReportReview = ReportReview
        self.InterestsRecommender = InterestPaperRecommender
        self.scheduler = scheduler
        self.cicd = Cli
        self.container_startup = ContainerStartup
        self.table = Table
        self.PrecomputedSearch = PrecomputedSearch


def main():
    import fire

    fire.Fire(Sota)


if __name__ == "__main__":
    main()
