from state_of_the_art.paper.format_papers import PapersFormatter
from state_of_the_art.paper.papers_data import PapersInDataWharehouse
from state_of_the_art.preferences.audience import Audience

from state_of_the_art.recommender.topic_based.searches import Bm25Search, SemanticSearch
from state_of_the_art.recommender.topic_based.topic import Topic

from state_of_the_art.recommender.topic_based.topic_extraction import TopicExtractor


class TopicSearch:
    MAX_PAPERS = 20

    def __init__(self):
        papers_data = PapersInDataWharehouse()
        papers = papers_data.load_papers()
        papers_list = papers_data.df_to_papers(papers)
        self.bm25_search = Bm25Search(papers_list)
        self.semantic_search = SemanticSearch()

    def search_by_topic(self, topic_name: str):
        """
        Search for papers on a given topic
        :param topic_name:
        :return:
        """
        from state_of_the_art.config import config
        audience: Audience = config.get_current_audience()

        topics = audience.get_topics()
        if topic_name not in topics:
            raise Exception(f"Topic {topic_name} not found in audience topics {topics.keys()}")
        topic : Topic = topics[topic_name]

        if not topic.semantic_query:
            topic.semantic_query = TopicExtractor().extract_semantic_query(topic)
            print(f'Extracted semantic query: ', topic.semantic_query)

        print(f"Searching for topic {topic_name} with query {topic.semantic_query}")


        print("Semantic Search")
        ids = self.semantic_search.search(topic.semantic_query, n=TopicSearch.MAX_PAPERS)
        papers_str = str(ids)


        print(PapersFormatter().from_str(papers_str))

        print("BM25")
        papers = self.bm25_search.search(topic.semantic_query, n=TopicSearch.MAX_PAPERS)
        print(PapersFormatter().from_papers(papers))




if __name__ == "__main__":
    import fire
    fire.Fire()