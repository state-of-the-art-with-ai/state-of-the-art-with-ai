
from state_of_the_art.paper_miner.arxiv import ArxivPaperMiner
from state_of_the_art.ranker.paper_ranker import PaperRanker
from state_of_the_art.papers import PapersData
from state_of_the_art.papers import BrowserPapers as browser_papers
from state_of_the_art.paper_insight import InsightExtractor
from state_of_the_art.paper import Paper

from state_of_the_art.bookmark import Bookmark as bookmark
from state_of_the_art.report.reports import Report
from state_of_the_art.topic_deepdive.search import TopicSearch
from state_of_the_art.report.formatter import SummaryFormatter
from state_of_the_art.report.reports import ReportsData


class Sota:
    def __init__(self):
        self.browser_papers = browser_papers
        self.papers_ui = browser_papers().fzf
        self.papers = PapersData().display
        self.rank = PaperRanker().rank
        self.paper_miner = ArxivPaperMiner()
        self.arxiv = self.paper_miner
        self.find_latest_papers = self.paper_miner.find_latest_papers
        self.report = Report
        self.extract_insights = InsightExtractor().extract
        self.bookmark = bookmark()
        self.open_paper = lambda paper: Paper(arxiv_url=paper).download_and_open()
        self.topic_search = TopicSearch
        self.SummaryFormatter = SummaryFormatter
        self.SummariesData = ReportsData



def main():
    import fire
    fire.Fire(Sota)

if __name__ == "__main__":
    main()
