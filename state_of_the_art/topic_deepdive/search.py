from typing import List

from state_of_the_art.paper import Paper
from state_of_the_art.papers import PapersData
from state_of_the_art.topic_deepdive.topic import Topic
from state_of_the_art.preferences.topics import topics
from rank_bm25 import BM25Okapi as BM25
import nltk


MAX_PAPERS = 30


class TopicSearch:
    def __init__(self):
        papers_data = PapersData()
        papers = papers_data.load_papers()
        papers_list = papers_data.df_to_papers(papers)
        self.search = Bm25Search(papers_list)

    def search_by_topic(self, topic_name: str):
        """
        Search for papers on a given topic
        :param topic_name:
        :return:
        """

        selected_topic = topics[topic_name]

        word_bag = []
        for topic in selected_topic.subtopics:
            word_bag = word_bag + topic.split(' ')

        for topic in selected_topic.synonyms:
            word_bag = word_bag + topic.split(' ')

        word_bag = list(set(word_bag))
        print(f"Searching for papers on '{word_bag}'")
        query = ' '.join(word_bag)
        print("\n\n")
        self.search_with_query(query)
    def search_with_query(self, query):
        papers = self.search.search(query)
        self.print_papers(papers)

    def print_papers(self, papers):
        result = [ p.published_str() + ' ' + p.title[0:100] + ' ' + p.url for p in papers]
        for r in result:
            print(r)

    def by_topic(self, topic: Topic):
        print(topic.synonyms)
        print(topic.subtopics)
        return papers


class Bm25Search:
    def __init__(self, papers_data: List[Paper]):
        self.tokenizer = nltk.tokenize.RegexpTokenizer(r"\w+")
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.papers_data = papers_data

        self.bm25 = self.setup_bm25()

    def setup_bm25(self):
        tokenized_corpus = [
            self.tokenize(paper.title + ' ' + paper.abstract) for paper in self.papers_data
        ]

        bm25 = BM25(tokenized_corpus)

        return bm25

    def search(self, query):
        tokenized_query = self.tokenize(query)

        matches = self.bm25.get_top_n(
            tokenized_query, self.papers_data, n=MAX_PAPERS
        )

        return matches

    def tokenize(self, string):
        tokens = self.tokenizer.tokenize(string)
        lemmas = [self.lemmatizer.lemmatize(t) for t in tokens]
        return lemmas



if __name__ == "__main__":
    import fire
    fire.Fire()