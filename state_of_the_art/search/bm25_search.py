from typing import List, Tuple

import nltk
from rank_bm25 import BM25Okapi as BM25

from state_of_the_art.paper.arxiv_paper import ArxivPaper


class Bm25Search:
    def __init__(self, papers_data: List[ArxivPaper]):
        self.tokenizer = nltk.tokenize.RegexpTokenizer(r"\w+")
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.papers_data = papers_data

        self.bm25 = self.setup_bm25()

    def setup_bm25(self):
        tokenized_corpus = [
            self.tokenize(paper.title + " " + paper.abstract)
            for paper in self.papers_data
        ]

        bm25 = BM25(tokenized_corpus)

        return bm25

    def search(self, query, n=100):
        tokenized_query = self.tokenize(query)

        matches = self.bm25.get_top_n(tokenized_query, self.papers_data, n=n)

        return matches

    def search_returning_tuple(self, query, n=100) -> List[Tuple[ArxivPaper, float]]:
        tokenized_query = self.tokenize(query)

        matches = self.bm25.get_top_n(tokenized_query, self.papers_data, n=n)
        scores = sorted(self.bm25.get_scores(tokenized_query)[0:n], reverse=True)

        return zip(matches, scores)


    def tokenize(self, string):
        tokens = self.tokenizer.tokenize(string)
        lemmas = [self.lemmatizer.lemmatize(t) for t in tokens]
        return lemmas


if __name__ == "__main__":
    import fire

    fire.Fire()
