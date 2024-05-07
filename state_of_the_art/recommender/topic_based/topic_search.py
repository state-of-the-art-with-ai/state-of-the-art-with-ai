from typing import Optional

from state_of_the_art.paper.format_papers import PapersFormatter
from state_of_the_art.paper.papers_data import PapersInDataWharehouse
from state_of_the_art.preferences.audience import Audience
from state_of_the_art.recommender.topic_based.searches import Bm25Search, SemanticSearch
from state_of_the_art.recommender.topic_based.topic import Topic
from state_of_the_art.recommender.topic_based.topic_extraction import TopicExtractor


class TopicSearch:

    def __init__(self):
        papers_data = PapersInDataWharehouse()
        papers = papers_data.load_papers()
        self._papers_list = papers_data.df_to_papers(papers)
        self.bm25_search = Bm25Search(self._papers_list)
        self.semantic_search = SemanticSearch()

    def search_by_topic(self, topic_name: Optional[str] = None):
        """
        Search for papers on a given topic
        :param topic_name:
        :return:
        """
        from state_of_the_art.config import config

        audience: Audience = config.get_current_audience()

        topics = audience.get_topics()
        if topic_name not in topics:
            raise Exception(
                f"Topic {topic_name} not found in audience topics {topics.keys()}"
            )
        topic: Topic = topics[topic_name]

        query = topic.semantic_query
        if not query:
            return self.extract_query_and_search(topic.problem_description)

        print(f"Searching for topic {topic_name} with query {topic.semantic_query}")

        return self.search_with_query(query)

    def extract_query_and_search(self, text: str):
        query = TopicExtractor().extract_semantic_query(text)
        print(f"Extracted semantic query: ", query)
        return self.search_with_query(query)

    def search_with_query(self, query: str):
        formatter = PapersFormatter()

        papers = self.bm25_search.search(query, n=5)
        result = "BM25\n"
        result += formatter.from_papers(papers)

        ids = self.semantic_search.search(query, n=15)
        papers_str = str(ids)
        result += "Semantic search\n"
        result += formatter.from_str(papers_str)
        print(result)

        return result


if __name__ == "__main__":
    import fire

    fire.Fire()
