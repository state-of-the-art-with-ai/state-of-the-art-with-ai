
from state_of_the_art.arxiv_utils import register_papers_by_topic
from state_of_the_art.paper_ranker import rank_by_relevance
from state_of_the_art.summaries import TopSummaries, SummariesData
from state_of_the_art.papers import PapersData
from state_of_the_art.config import Config
from state_of_the_art.insight_extractor import InsightExtractor
from state_of_the_art import open_ai_utils
from state_of_the_art.topic_insights import TopicInsights


def register_papers():
    topics = Config.load_config().topics_to_query_arxiv
    print("Registering papers for topics: ", topics)
    for topic in topics:
        register_papers_by_topic(query=topic, sort_by='relevance')
        register_papers_by_topic(query=topic, sort_by='submitted')


def register_and_sort_papers():
    register_papers()
    rank_by_relevance()

def main():
    import fire
    fire.Fire()

if __name__ == "__main__":
    main()
