from state_of_the_art.paper.downloader import Downloader
from state_of_the_art.paper.papers_data import PapersDataLoader
from state_of_the_art.paper.papers_report import PapersReport
from state_of_the_art.insight_extractor.insight_extractor import InsightExtractor

from state_of_the_art.bookmark import Bookmark as bookmark
from state_of_the_art.recommender.generator import Recommender
from state_of_the_art.recommender.topic_based.semantic_search import SemanticSearch
from state_of_the_art.recommender.topic_based.topic_search import TopicSearch
from state_of_the_art import validation
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
from state_of_the_art.review import ReportReview
from state_of_the_art.insight_extractor.summarize_and_sharpen import Sharpen


class Sota:
    """
    State of the art via ai main entry script
    """

    def __init__(self):
        self.recommender = Recommender
        self.papers = PapersDataLoader()
        self.InsightExtractor = InsightExtractor
        self.bookmark = bookmark()
        self.topic_search = TopicSearch
        self.SemanticSearch = SemanticSearch
        self._ci = validation
        self.papers_report = PapersReport
        self.downloader = Downloader
        self.ArxivMiner = ArxivMiner
        self.ReportReview = ReportReview
        self.Sharpen = Sharpen


def main():
    import fire

    fire.Fire(Sota)


if __name__ == "__main__":
    main()
