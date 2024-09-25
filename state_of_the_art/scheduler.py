import time
import datetime

from state_of_the_art.ci_cd import S3
from state_of_the_art.recommenders.interest_recommender.interest_recommender_generator import InterestsRecommender

def send_email_job():
    print("Running recommender")

    try:
        InterestsRecommender().generate(
            repeat_check_disable=True,
        )
    except Exception as e:
        print("Error in scheduler job", e)


def print_test():
    print("Test run every 5 mins at " + datetime.datetime.now().isoformat())


def push_data_to_s3():
    print("Pushing data to s3")
    out, error = S3().push_local_data()
    print(error, out)

def run_scheduler():
    import schedule
    print("starting scheduler setup at " + datetime.datetime.now().isoformat())

    schedule.every(5).minutes.do(print_test)
    schedule.every(3).hours.do(push_data_to_s3)
    schedule.every().day.at("22:00").do(send_email_job)
    schedule.every().day.at("15:00").do(send_email_job)
    schedule.every().day.at("11:00").do(send_email_job)
    print("Scheduler infinite loop started")
    while True:
        schedule.run_pending()
        time.sleep(1)
