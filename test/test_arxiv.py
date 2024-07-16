import pytest

from utils import no_internet


@pytest.mark.skipif(no_internet(), reason="No internet")
def test_arxiv_api():
    import arxiv

    result = arxiv.Search(query="test", max_results=100)
    results = list(result.results())
    assert len(results) == 100
