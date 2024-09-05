
import datetime

from state_of_the_art.recommenders.interest_recommender.interest_recommender_generator import InterestsRecommender


def test_single_interest_relevance():
    interest = 'ethics ai and ml ethics fairness accountability transparency humanism and social challenges, social impact'
    recommender = InterestsRecommender()
    date_to = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
    date_from = (datetime.datetime.now() - datetime.timedelta(days=6)).date()
    
    recommender.load_papers_and_embeddings(date_from, date_to)
    papers, scores = recommender.get_papers_for_interest(interest)
    print(str([paper.title for paper in papers]))
