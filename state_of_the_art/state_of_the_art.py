
from state_of_the_art.register_papers.arxiv_miner import PaperMiner
from state_of_the_art.paper.papers_data import PapersInDataWharehouse
from state_of_the_art.paper.browser import BrowserPapers as browser_papers
from state_of_the_art.paper_insight.paper_insight import PaperInsightExtractor
from state_of_the_art.paper.paper import Paper

from state_of_the_art.bookmark import Bookmark as bookmark
from state_of_the_art.recommender.report import RecommenderReport
from state_of_the_art.recommender.topic_based.searches import SemanticSearch
from state_of_the_art.recommender.topic_based.topic_search import TopicSearch

class Sota:
    def __init__(self):
        self.recommender = RecommenderReport
        self.browser_papers = browser_papers
        self.papers_ui = browser_papers().fzf
        self.papers = PapersInDataWharehouse()
        self.PaperMiner = PaperMiner()
        self.PaperInsightExtractor = PaperInsightExtractor
        self.bookmark = bookmark()
        self.open_paper = lambda paper: Paper(arxiv_url=paper).download_and_open()
        self.topic_search = TopicSearch
        self.SemanticSearch = SemanticSearch


def main():
    import fire
    fire.Fire(Sota)

if __name__ == "__main__":
    main()
