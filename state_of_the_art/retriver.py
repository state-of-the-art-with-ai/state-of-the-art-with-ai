from state_of_the_art.topic import deep_learning, marketing_measurment, bidding, Topic
class TopicRetriver:
    def retrieve(self):
        papers = PapersData().load_papers()

        self.by_topic(marketing_measurment)

    def by_topic(self, topic: Topic):
        print(topic.synonyms)
        print(topic.subtopics)

from rank_bm25 import BM25Okapi as BM25
import nltk


class Bm25Search:
    def __init__(self, data):
        self.tokenizer = nltk.tokenize.RegexpTokenizer(r"\w+")
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.bm25 = self.setup_bm25(['data'])

    def build_bm25(self):
        tokenized_corpus = [
            self.tokenize((key + str(value))) for key, value in self.commands.items()
        ]

        bm25 = BM25(tokenized_corpus)
        self.searialize_database(bm25)

        return bm25

    def search(self, query):

        if not query:
            return self.entries[0:self.number_entries_to_return], []

        tokenized_query = self.tokenize(query)

        matches = self.bm25.get_top_n(
            tokenized_query, self.entries, n=self.number_entries_to_return
        )

        return matches, tokenized_query


    def tokenize(self, string):
        tokens = self.tokenizer.tokenize(string)
        lemmas = [self.lemmatizer.lemmatize(t) for t in tokens]
        return lemmas


if __name__ == "__main__":
    import fire
    fire.Fire()



if __name__ == "__main__":
    import fire
    fire.Fire()