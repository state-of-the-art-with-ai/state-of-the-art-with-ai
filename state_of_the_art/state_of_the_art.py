from state_of_the_art.register_papers.arxiv_miner import PaperMiner
from state_of_the_art.paper.papers_data import PapersInDataWharehouse
from state_of_the_art.paper.browser import BrowserPapers as browser_papers
from state_of_the_art.paper_insight.paper_insight import PaperInsightExtractor
from state_of_the_art.paper.paper import Paper

from state_of_the_art.bookmark import Bookmark as bookmark
from state_of_the_art.recommender.recommender import Recommender
from state_of_the_art.recommender.topic_based.searches import SemanticSearch
from state_of_the_art.recommender.topic_based.topic_search import TopicSearch
from state_of_the_art import continuous_integration


class Sota:
    """State of the art via ai main entry script"""

    def __init__(self):
        self.recommender = Recommender
        self.browser_papers = browser_papers
        self.papers_ui = browser_papers().fzf
        self.papers = PapersInDataWharehouse()
        self.PaperMiner = PaperMiner()
        self.PaperInsightExtractor = PaperInsightExtractor
        self.bookmark = bookmark()
        self.open_paper = lambda paper: Paper(arxiv_url=paper).download_and_open()
        self.topic_search = TopicSearch
        self.SemanticSearch = SemanticSearch
        self._ci = continuous_integration


def main():
    import fire

    fire.Fire(Sota)


if __name__ == "__main__":
    main()
