import time
import datetime

from state_of_the_art.infrastructure.sentry import setup_sentry
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
from state_of_the_art.scheduling.utils import capture_errors
from state_of_the_art.search.bm25_search import PrecomputedSearch
from state_of_the_art.utils.mail import EmailService

MINUTES_TO_REPEAT_LIVENESS_PROBE = 10

setup_sentry()

@capture_errors()
def send_recommendations_job():
    print("Running recommender")
    from state_of_the_art.recommenders.interest_recommender.interest_recommender_generator import (
        InterestsRecommender,
    )

    InterestsRecommender().generate(
        repeat_check_disable=True,
        number_of_days_to_look_back=get_random_number_of_days(),
        skip_register_new_papers=True,
    )

def get_random_number_of_days():
    import random
    return random.randint(1, 20)

@capture_errors()
def liveness_probe():
    print(
        f"Test run every {MINUTES_TO_REPEAT_LIVENESS_PROBE} mins at "
        + datetime.datetime.now().isoformat()
    )
    raise Exception("Testing errors")


@capture_errors()
def push_data_to_s3():
    print("Pushing data to s3")
    from state_of_the_art.infrastructure.s3 import S3

    out, error = S3().push_local_events_data()
    print(error, out)

@capture_errors()
def mine_all_keywords():
    ArxivMiner().mine_all_keywords()
    PrecomputedSearch().pickle_all_documents()



def run():
    import schedule

    print("starting scheduler setup at " + datetime.datetime.now().isoformat())

    schedule.every(MINUTES_TO_REPEAT_LIVENESS_PROBE).minutes.do(liveness_probe)
    schedule.every(20).minutes.do(push_data_to_s3)

    schedule.every().day.at("06:00").do(mine_all_keywords)
    schedule.every().day.at("12:00").do(mine_all_keywords)
    schedule.every().day.at("23:00").do(mine_all_keywords)

    # send email
    schedule.every().day.at("00:00").do(send_recommendations_job)
    schedule.every().day.at("01:00").do(send_recommendations_job)
    schedule.every().day.at("02:00").do(send_recommendations_job)
    schedule.every().day.at("03:00").do(send_recommendations_job)
    schedule.every().day.at("04:00").do(send_recommendations_job)
    schedule.every().day.at("05:00").do(send_recommendations_job)
    schedule.every().day.at("06:00").do(send_recommendations_job)
    schedule.every().day.at("08:30").do(send_recommendations_job)
    schedule.every().day.at("13:00").do(send_recommendations_job)
    schedule.every().day.at("17:35").do(send_recommendations_job)
    schedule.every().day.at("23:00").do(send_recommendations_job)


    print("Scheduler infinite loop started")
    while True:
        schedule.run_pending()
        time.sleep(0.5)
