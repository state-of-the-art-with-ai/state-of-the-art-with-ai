
from state_of_the_art.arxiv_utils import register_papers_by_topic
from state_of_the_art.paper_ranker import rank
from state_of_the_art.summaries import TopSummaries, SummariesData
from state_of_the_art.papers import PapersData
from state_of_the_art.config import Config
from state_of_the_art.insight_extractor import InsightExtractor
from state_of_the_art import open_ai_utils
from state_of_the_art.topic_insights import TopicInsights

get_latest_summary = SummariesData().get_latest_summary

def register_papers():
    topics = Config.load_config().get_current_profile().arxiv_topics
    print("Registering papers for topics: ", topics)
    for topic in topics:
        register_papers_by_topic(query=topic, sort_by='relevance')
        register_papers_by_topic(query=topic, sort_by='submitted')


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
