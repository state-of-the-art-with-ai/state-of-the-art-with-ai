
from state_of_the_art.paper_miner.arxiv_miner import PaperMiner
from state_of_the_art.ranker.ranker import PaperRanker
from state_of_the_art.paper.papers_data import PapersInDataWharehouse
from state_of_the_art.paper.browser import BrowserPapers as browser_papers
from state_of_the_art.paper_insight.paper_insight import PaperInsightExtractor
from state_of_the_art.paper.paper import Paper

from state_of_the_art.bookmark import Bookmark as bookmark
from state_of_the_art.recommender.report import RecommenderReport
from state_of_the_art.recommender.formatter import SummaryFormatter
from state_of_the_art.recommender.reports_data import ReportsData
from state_of_the_art.topic_deepdive.topic_search import TopicSearch
from state_of_the_art.utils.mail import Mail

class Sota:
    def __init__(self):
        self.recommender = RecommenderReport
        self.browser_papers = browser_papers
        self.papers_ui = browser_papers().fzf
        self.papers = PapersInDataWharehouse()
        self.rank = PaperRanker().rank
        self.PaperMiner = PaperMiner()
        self.PaperInsightExtractor = PaperInsightExtractor
        self.bookmark = bookmark()
        self.open_paper = lambda paper: Paper(arxiv_url=paper).download_and_open()
        self.topic_search = TopicSearch


def main():
    import fire
    fire.Fire(Sota)

if __name__ == "__main__":
    main()
