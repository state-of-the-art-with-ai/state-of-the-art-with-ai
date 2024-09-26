import time
import datetime

from state_of_the_art.infrastructure.s3 import S3
from state_of_the_art.recommenders.interest_recommender.interest_recommender_generator import InterestsRecommender

def send_email_job():
    print("Running recommender")
    try:
        InterestsRecommender().generate(
            repeat_check_disable=True,
            number_of_days_to_look_back=1
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

    schedule.every().day.at("01:00").do(push_data_to_s3)
    schedule.every().day.at("04:00").do(push_data_to_s3)
    schedule.every().day.at("06:00").do(push_data_to_s3)
    schedule.every().day.at("08:00").do(push_data_to_s3)
    schedule.every().day.at("09:00").do(push_data_to_s3)
    schedule.every().day.at("10:00").do(push_data_to_s3)
    schedule.every().day.at("12:00").do(push_data_to_s3)
    schedule.every().day.at("13:00").do(push_data_to_s3)
    schedule.every().day.at("14:00").do(push_data_to_s3)
    schedule.every().day.at("15:00").do(push_data_to_s3)
    schedule.every().day.at("16:00").do(push_data_to_s3)
    schedule.every().day.at("17:00").do(push_data_to_s3)
    schedule.every().day.at("18:00").do(push_data_to_s3)
    schedule.every().day.at("19:00").do(push_data_to_s3)
    schedule.every().day.at("20:00").do(push_data_to_s3)
    schedule.every().day.at("21:00").do(push_data_to_s3)
    schedule.every().day.at("22:00").do(push_data_to_s3)
    schedule.every().day.at("23:00").do(push_data_to_s3)

    # send email
    schedule.every().day.at("22:40").do(send_email_job)
    schedule.every().day.at("22:00").do(send_email_job)
    schedule.every().day.at("15:00").do(send_email_job)
    schedule.every().day.at("11:00").do(send_email_job)

    print("Scheduler infinite loop started")
    while True:
        schedule.run_pending()
        time.sleep(1)
