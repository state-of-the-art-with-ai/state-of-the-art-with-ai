
from state_of_the_art.arxiv_loader import register_papers
from state_of_the_art.paper_ranker import rank
from state_of_the_art.summaries import TopSummaries, SummariesData
from state_of_the_art.papers import PapersData as papers
from state_of_the_art.paper_insight import InsightExtractor
from state_of_the_art.topic_insights import TopicInsights

from state_of_the_art.bookmark import Bookmark as bookmark

latest_summary = SummariesData().get_latest_summary

def generate(*, look_back_days=7, from_date=None, skip_register=False):
    """
    The main entrypoint of the application does the entire cycle from registering papers to ranking them
    """
    if not skip_register:
        register_papers()
    else:
        print("Skipping registering papers")

    rank(look_back_days=look_back_days, from_date=from_date)

def main():
    import fire
    fire.Fire()

if __name__ == "__main__":
    main()
