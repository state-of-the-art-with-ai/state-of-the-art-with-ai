
from state_of_the_art.paper_miner import ArxivMiner
from state_of_the_art.ranker.paper_ranker import PaperRanker
from state_of_the_art.summaries import TopSummaries, SummariesData
from state_of_the_art.papers import PapersData, BrowserPapers as browser_papers
from state_of_the_art.paper_insight import InsightExtractor
from state_of_the_art.topic_insights import TopicInsights
from state_of_the_art.config import config

from state_of_the_art.bookmark import Bookmark as bookmark

latest_summary = SummariesData().get_latest_summary
papers_ui = browser_papers().fzf
papers = PapersData().display
rank = PaperRanker().rank

def generate(*, lookback_days=None, from_date=None, skip_register=False, dry_run=False):
    """
    The main entrypoint of the application does the entire cycle from registering papers to ranking them
    """
    miner = ArxivMiner()
    if not skip_register:
        miner.register_papers(dry_run=dry_run)
    else:
        print("Skipping registering papers")

    rank(look_back_days=lookback_days, from_date=from_date)

def main():
    import fire
    fire.Fire()

if __name__ == "__main__":
    main()
