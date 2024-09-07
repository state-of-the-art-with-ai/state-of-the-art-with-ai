import datetime

from state_of_the_art.recommenders.interest_recommender.interest_recommender_generator import (
    InterestsRecommender,
)


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
