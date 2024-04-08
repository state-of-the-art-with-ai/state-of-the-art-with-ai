
from state_of_the_art.paper_miner import ArxivMiner
from state_of_the_art.ranker.paper_ranker import PaperRanker
from state_of_the_art.summaries import SummariesData
from state_of_the_art.papers import PapersData
from state_of_the_art.papers import BrowserPapers as browser_papers
from state_of_the_art.paper_insight import InsightExtractor
from state_of_the_art.paper import Paper

from state_of_the_art.bookmark import Bookmark as bookmark
from state_of_the_art.retriver import TopicRetriver


class Sota:
    def __init__(self):
        self.latest_summary = SummariesData().get_latest_summary
        self.browser_papers = browser_papers
        self.papers_ui = browser_papers().fzf
        self.papers = PapersData().display
        self.rank = PaperRanker().rank
        self._arxiv_miner = ArxivMiner()
        self.register = self._arxiv_miner.register_papers
        self.find_latest_papers = self._arxiv_miner.find_latest_papers
        self.extract_insights = InsightExtractor().extract
        self.bookmark = bookmark()
        self.open_paper = lambda paper: Paper(arxiv_url=paper).download_and_open()
        self.topic_retriver = TopicRetriver

    def generate(self, *, lookback_days=None, from_date=None, skip_register=False, dry_run=False):
        """
        The main entrypoint of the application does the entire cycle from registering papers to ranking them
        """
        if not skip_register:
            self.register(dry_run=dry_run)
        else:
            print("Skipping registering papers")

        self.rank(lookback_days=lookback_days, from_date=from_date)

def main():
    import fire
    fire.Fire(Sota)

if __name__ == "__main__":
    main()
