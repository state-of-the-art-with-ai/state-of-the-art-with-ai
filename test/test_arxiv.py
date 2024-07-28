import pytest

from state_of_the_art.utils.internet import has_internet


@pytest.mark.skipif(not has_internet(), reason="No internet")
def test_arxiv_api():
    import arxiv

    result = arxiv.Search(query="test", max_results=2)
    results = list(result.results())
    assert len(results) == 2
