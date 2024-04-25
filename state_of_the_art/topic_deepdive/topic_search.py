from state_of_the_art.paper.papers_data import PapersInDataWharehouse
from state_of_the_art.preferences.audience import Audience

from state_of_the_art.topic_deepdive.searches import Bm25Search
from state_of_the_art.topic_deepdive.topic import Topic

MAX_PAPERS = 30

class TopicSearch:
    def __init__(self):
        papers_data = PapersInDataWharehouse()
        papers = papers_data.load_papers()
        papers_list = papers_data.df_to_papers(papers)
        self.search = Bm25Search(papers_list)

    def search_by_topic(self, topic_name: str):
        """
        Search for papers on a given topic
        :param topic_name:
        :return:
        """
        from state_of_the_art.config import config
        audience: Audience = config.get_current_audience()
        topic : Topic = audience.get_topics()[topic_name]
        print(f"Searching for topic {topic_name} with query {topic.semantic_query}")

        self.search_with_query(topic.semantic_query)

    def search_with_query(self, query: str):
        papers = self.search.search(query)
        self.print_papers(papers)

    def print_papers(self, papers):
        result = [p.published_date_str() + ' ' + p.title[0:100] + ' ' + p.url for p in papers]
        for r in result:
            print(r)


if __name__ == "__main__":
    import fire
    fire.Fire()