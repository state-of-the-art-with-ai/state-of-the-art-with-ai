import os
import pickle
from typing import List, Tuple

import nltk
from rank_bm25 import BM25Okapi as BM25

from state_of_the_art.paper.arxiv_paper import ArxivPaper
from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.config import config


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

    def search_returning_papers(self, query, n=100) -> List[ArxivPaper]:
        tokenized_query = self.tokenize(query)

        matches = self.bm25.get_top_n(tokenized_query, self.papers_list, n=n)

        return matches

    def search_returning_paper_and_score(
        self, query, n=100
    ) -> Tuple[List[ArxivPaper], List[float]]:
        tokenized_query = self.tokenize(query)

        matches = self.bm25.get_top_n(tokenized_query, self.papers_list, n=n)
        scores = sorted(self.bm25.get_scores(tokenized_query)[0:n], reverse=True)

        return matches, scores

    def tokenize(self, string):
        tokens = self.tokenizer.tokenize(string)
        lemmas = [self.lemmatizer.lemmatize(t) for t in tokens]
        return lemmas

class PrecomputedSearch:
    def pickle_search(self):
        papers = self.setup_search_with_all_papers()
        if not os.path.exists(config.PRECOMPUTED_FOLDER):
            os.makedirs(config.PRECOMPUTED_FOLDER)

        with open(config.PRECOMPUTED_SEARCH, "wb") as f:
            pickle.dump(papers, f)
        print(f"Search pickled to {config.PRECOMPUTED_SEARCH} scuccessfully")
    def setup_search_with_all_papers(self):
        papers = PapersLoader().get_all_papers()
        return Bm25Search(papers)
    
    def load_papers_from_pickle(self) -> Bm25Search:
        with open(config.PRECOMPUTED_SEARCH, "rb") as f:
            return pickle.load(f)
    
    def search_returning_papers(self, query, n=100) -> List[ArxivPaper]:
        search = self.load_papers_from_pickle()
        return search.search_returning_papers(query, n=n)
    

        

if __name__ == "__main__":
    import fire

    fire.Fire()
