import pytest
import datetime
import arxiv

from state_of_the_art.utils.internet import has_internet


@pytest.mark.skipif(not has_internet(), reason="No internet")
def test_arxiv_api():
    result = arxiv.Search(query="test", max_results=2)
    results = list(result.results())
    assert len(results) == 2
    assert results[0].entry_id is not None


def test_latest_date():
    result = arxiv.Search(
        query="test", sort_by=arxiv.SortCriterion.SubmittedDate, max_results=1
    )
    result_list = list(result.results())
    past_week = (datetime.datetime.now() - datetime.timedelta(days=7)).date()
    assert result_list[0].published.date() >= past_week


def test_find_by_id():
    result = arxiv.Search(id_list=["2409.02069"])
    result_list = list(result.results())
    result_list[0].published.date() >= datetime.date(2024, 9, 4)


def test_last_updated_date():
    result = arxiv.Search(
        query="Machine Learning",
        sort_by=arxiv.SortCriterion.LastUpdatedDate,
        sort_order=arxiv.SortOrder.Descending,
        max_results=1,
    )

    result_list = list(result.results())
    print(result_list)
    print(result_list[0].entry_id)
    print(result_list[0].published.date())
