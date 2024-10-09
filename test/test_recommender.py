import datetime

from state_of_the_art.recommenders.interest_recommender.embeddings_similarity import (
    EmbeddingsSimilarity,
)
from state_of_the_art.recommenders.interest_recommender.interest_recommender_generator import (
    InterestPaperRecommender,
)
import scipy.stats as stats
import pytest
import os

from unittest import mock

@pytest.mark.skipif(True, reason="failing in the ci due to missing data to run ")
@mock.patch.dict(os.environ, {"SKIP_AUTH_FILTER": "1"})
@mock.patch.dict(os.environ, {"SOTA_TEST": "1"})
def test_recommender_end2end():
    recommender = InterestPaperRecommender()
    recommender.generate()

@pytest.mark.skipif(True, reason="failing in the ci")
def test_single_interest_relevance():
    interest = "security in machine learning "
    recommender = EmbeddingsSimilarity()
    number_of_days_look_back = 3
    date_to = (datetime.datetime.now() - datetime.timedelta(days=0)).date()
    date_from = (
        datetime.datetime.now() - datetime.timedelta(days=number_of_days_look_back)
    ).date()

    papers, _ = recommender.load_papers_and_embeddings(date_from, date_to)
    recommender._encode_missing_papers(papers)
    papers, scores = recommender.get_papers_for_interest(interest)
    print(str([paper.title for paper in papers]))



def test_remove_duplicates():
    data = {
        "first interest": {
            "papers": {
                "http://arxiv.org/abs/2409.04332": {"final_score": 0.1},
                "http://arxiv.org/abs/2409.04348": {"final_score": 0.2},
            }
        },
        "second interest": {
            "papers": {
                "http://arxiv.org/abs/2409.04332": {"final_score": 0.9},
                "http://arxiv.org/abs/2409.04348": {"final_score": 0.1},
            }
        },
    }

    result = InterestPaperRecommender()._remove_duplicates(recommendation_structure=data)
    print(result)

    assert len(result["first interest"]["papers"].items()) == 1


def test_sort_interests_by_paper_scores():
    data = {
        "first interest": {
            "papers": {
                "http://arxiv.org/abs/2409.04332": {"final_score": 0.1},
                "http://arxiv.org/abs/2409.04348": {"final_score": 0.2},
            }
        },
        "second interest": {
            "papers": {
                "http://arxiv.org/abs/2409.04332": {"final_score": 0.9},
                "http://arxiv.org/abs/2409.04348": {"final_score": 0.1},
            }
        },
    }

    result = InterestPaperRecommender()._sort_interests_by_scores(data)
    iterator = iter(result.items())
    assert next(iterator)[0] == "second interest"
    assert next(iterator)[0] == "first interest"


def test_normalize():
    series = [35, 10, 5, 0, 1]
    normalized = zscore(series)
    print("Normalized: ", normalized)

    series_2 = [0.5, 0.3, 0.1, 0]
    normalized_2 = zscore(series_2)
    print("Normalized2: ", normalized_2)


def zscore(series):
    return stats.zscore(series)
