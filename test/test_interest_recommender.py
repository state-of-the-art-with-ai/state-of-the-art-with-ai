import datetime
from operator import itemgetter

from state_of_the_art.recommenders.interest_recommender.interest_recommender_generator import (
    InterestsRecommender,
)
from state_of_the_art.recommenders.interest_recommender.interest_recommender_generator import remove_duplicates
from state_of_the_art.tables.recommendations_history_table import RecommendationsHistoryTable


def test_single_interest_relevance():
    interest = "security in machine learning "
    recommender = InterestsRecommender()
    number_of_days_look_back = 3
    date_to = (datetime.datetime.now() - datetime.timedelta(days=0)).date()
    date_from = (datetime.datetime.now() - datetime.timedelta(days=number_of_days_look_back)).date()

    papers, _ = recommender.load_papers_and_embeddings(date_from, date_to)
    recommender._encode_missing_papers(papers)
    papers, scores = recommender.get_papers_for_interest(interest)
    print(str([paper.title for paper in papers]))


def test_load_results():
    recommendation, row = RecommendationsHistoryTable().get_parsed_recommended_papers()

    import json ; print(json.dumps(recommendation, indent=4))

def test_remove_duplicates():
    data = {
        "first interest": {
            "papers": {
                "http://arxiv.org/abs/2409.04332": {
                    "score": 0.1
                },
                "http://arxiv.org/abs/2409.04348": {
                    "score": 0.2
                },
            }
        },
        "second interest": {
            "papers": {
                "http://arxiv.org/abs/2409.04332": {
                    "score": 0.9
                },
                "http://arxiv.org/abs/2409.04348": {
                    "score": 0.1
                },
            }
        },
    }

    result = remove_duplicates(recommendation_structure=data)
    print(result)

    assert len(result['first interest']['papers'].items()) == 1

    

    
