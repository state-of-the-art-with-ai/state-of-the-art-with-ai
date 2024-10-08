import time
import datetime

from state_of_the_art.infrastructure.sentry import setup_sentry
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
from state_of_the_art.scheduling.utils import capture_errors
from state_of_the_art.search.bm25_search import PrecomputedSearch
from state_of_the_art.recommenders.interest_recommender.interest_recommender_generator import (
    InterestPaperRecommender,
)

MINUTES_TO_REPEAT_LIVENESS_PROBE = 10

setup_sentry()

@capture_errors()
def send_recommendations_job(number_of_days_to_look_back=1):
    def _send_recos():
        print("Sending recommendations")
        print("Running recommender")

        InterestPaperRecommender().generate(
            number_of_days_to_look_back=number_of_days_to_look_back,
        )
    return _send_recos


@capture_errors()
def liveness_probe():
    print(
        f"Test run every {MINUTES_TO_REPEAT_LIVENESS_PROBE} mins at "
        + datetime.datetime.now().isoformat()
    )

@capture_errors()
def push_data_to_s3():
    print("Pushing data to s3")
    from state_of_the_art.infrastructure.s3 import S3

    out, error = S3().push_local_events_data()
    print(error, out)

@capture_errors()
def mine_all_keywords():
    ArxivMiner().mine_all_keywords()
    PrecomputedSearch().index_and_store_documents()



def run():
    import schedule

    print("starting scheduler setup at " + datetime.datetime.now().isoformat())

    schedule.every(MINUTES_TO_REPEAT_LIVENESS_PROBE).minutes.do(liveness_probe)
    schedule.every(20).minutes.do(push_data_to_s3)

    schedule.every().day.at("05:00").do(mine_all_keywords)
    schedule.every().day.at("08:00").do(mine_all_keywords)
    schedule.every().day.at("12:00").do(mine_all_keywords)
    schedule.every().day.at("15:00").do(mine_all_keywords)
    schedule.every().day.at("23:00").do(mine_all_keywords)

    # send email
    schedule.every().day.at("01:00").do(send_recommendations_job(30))
    schedule.every().day.at("06:00").do(send_recommendations_job(60))
    schedule.every().day.at("06:00").do(send_recommendations_job(90))
    schedule.every().day.at("11:00").do(send_recommendations_job(1))
    schedule.every().day.at("17:30").do(send_recommendations_job(7))


    print("Scheduler infinite loop started")
    while True:
        schedule.run_pending()
        time.sleep(0.5)
