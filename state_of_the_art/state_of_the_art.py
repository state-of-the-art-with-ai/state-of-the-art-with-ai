from state_of_the_art.paper.downloader import Downloader
from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.insight_extractor.insight_extractor import InsightExtractor

from state_of_the_art.recommenders.interest_recommender.interest_recommender_generator import InterestsRecommender
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
from state_of_the_art.review import ReportReview
from state_of_the_art.scheduler import run_scheduler


class Sota:
    """
    State of the art via ai main entry script
    """

    def __init__(self):
        self.papers = PapersLoader()
        self.InsightExtractor = InsightExtractor
        self.downloader = Downloader
        self.ArxivMiner = ArxivMiner
        self.ReportReview = ReportReview
        self.InterestsRecommender = InterestsRecommender
        self.run_scheduler = run_scheduler


def main():
    import fire

    fire.Fire(Sota)


if __name__ == "__main__":
    main()
