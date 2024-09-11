from typing import List, Tuple

import nltk
from rank_bm25 import BM25Okapi as BM25

from state_of_the_art.paper.arxiv_paper import ArxivPaper


class Bm25Search:
    def __init__(self, papers_list: List[ArxivPaper] = None):
        self.tokenizer = nltk.tokenize.RegexpTokenizer(r"\w+")
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.papers_list = papers_list
        if papers_list:
            self.set_papers_and_index(papers_list=papers_list)

    def set_papers_and_index(self, papers_list: List[ArxivPaper]):
        self.papers_list = papers_list
        tokenized_corpus = [
            self.tokenize(paper.title + " " + paper.abstract)
            for paper in self.papers_list
        ]

        self.bm25 = BM25(tokenized_corpus)

    def search(self, query, n=100) -> List[ArxivPaper]:
        tokenized_query = self.tokenize(query)

        matches = self.bm25.get_top_n(tokenized_query, self.papers_list, n=n)

        return matches

    def search_returning_tuple(self, query, n=100) -> List[Tuple[ArxivPaper, float]]:
        tokenized_query = self.tokenize(query)

        matches = self.bm25.get_top_n(tokenized_query, self.papers_list, n=n)
        scores = sorted(self.bm25.get_scores(tokenized_query)[0:n], reverse=True)

        return zip(matches, scores)


    def tokenize(self, string):
        tokens = self.tokenizer.tokenize(string)
        lemmas = [self.lemmatizer.lemmatize(t) for t in tokens]
        return lemmas


if __name__ == "__main__":
    import fire

    fire.Fire()
