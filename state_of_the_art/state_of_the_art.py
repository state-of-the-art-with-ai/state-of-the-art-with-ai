
from state_of_the_art.paper_miner import ArxivMiner
from state_of_the_art.ranker.paper_ranker import PaperRanker
from state_of_the_art.summaries import TopSummaries, SummariesData
from state_of_the_art.papers import PapersData, BrowserPapers as browser_papers
from state_of_the_art.paper_insight import InsightExtractor
from state_of_the_art.topic_insights import TopicInsights
from state_of_the_art.config import config

from state_of_the_art.bookmark import Bookmark as bookmark


class Sota:
    def __init__(self):
        self.latest_summary = SummariesData().get_latest_summary
        self.papers_ui = browser_papers().fzf
        self.papers = PapersData().display
        self.rank = PaperRanker().rank
        self.register = ArxivMiner().register_papers
        self.extract_insights = InsightExtractor().extract

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
