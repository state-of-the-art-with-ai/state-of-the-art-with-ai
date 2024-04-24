
from state_of_the_art.paper_miner.arxiv_miner import PaperMiner
from state_of_the_art.ranker.paper_ranker import PaperRanker
from state_of_the_art.paper.papers_data import Papers
from state_of_the_art.paper.browser import BrowserPapers as browser_papers
from state_of_the_art.paper_insight.paper_insight import PaperInsightExtractor
from state_of_the_art.paper.paper import Paper

from state_of_the_art.bookmark import Bookmark as bookmark
from state_of_the_art.report.recommender import RecommenderReport
from state_of_the_art.topic_deepdive.bm25_search import TopicSearch
from state_of_the_art.report.formatter import SummaryFormatter
from state_of_the_art.report.reports_data import ReportsData
from state_of_the_art.topic_deepdive.topic_extractor import TopicExtractor
from state_of_the_art.topic_deepdive.vector_search import VectorSearch
from state_of_the_art.utils.mail import Mail

class Sota:
    def __init__(self):
        self.recommender = RecommenderReport
        self.browser_papers = browser_papers
        self.papers_ui = browser_papers().fzf
        self.papers = Papers()
        self.rank = PaperRanker().rank
        self.PaperMiner = PaperMiner()
        self.PaperInsightExtractor = PaperInsightExtractor
        self.bookmark = bookmark()
        self.open_paper = lambda paper: Paper(arxiv_url=paper).download_and_open()
        self.topic_search = TopicSearch
        self.SummaryFormatter = SummaryFormatter
        self.SummariesData = ReportsData
        self.Mail = Mail
        self.VectorSearch = VectorSearch
        self.TopicExtractor = TopicExtractor



def main():
    import fire
    fire.Fire(Sota)

if __name__ == "__main__":
    main()
