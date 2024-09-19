
from state_of_the_art.paper.arxiv_paper import ArxivPaper
from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.search.bm25_search import Bm25Search


def test_bm25():
    some_papers_df = PapersLoader().load_between_dates_str("2024-09-01", "2024-09-03")
    assert len(some_papers_df.index) > 0 
    some_papers = PapersLoader().to_papers(some_papers_df)
    search = Bm25Search(some_papers)
    result = search.search_returning_paper_and_score("machine learning")
    result = list(result)
    assert result[1][0] > 0 
    assert isinstance(result[0][0], ArxivPaper)