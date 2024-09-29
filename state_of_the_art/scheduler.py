import time
import datetime

from state_of_the_art.scheduling.utils import capture_exeption

MINUTES_TO_REPEAT_LIVENESS_PROBE = 10


@capture_exeption()
def send_recommendations_job():
    print("Running recommender")
    try:
        from state_of_the_art.recommenders.interest_recommender.interest_recommender_generator import (
            InterestsRecommender,
        )

        InterestsRecommender().generate(
            repeat_check_disable=True, number_of_days_to_look_back=1
        )
    except Exception as e:
        print("Error in scheduler job", e)


@capture_exeption()
def liveness_probe():
    print(
        f"Test run every {MINUTES_TO_REPEAT_LIVENESS_PROBE} mins at "
        + datetime.datetime.now().isoformat()
    )
    raise Exception("Testing errors")


@capture_exeption()
def push_data_to_s3():
    print("Pushing data to s3")
    from state_of_the_art.infrastructure.s3 import S3

    out, error = S3().push_local_events_data()
    print(error, out)


def run():
    import schedule

    print("starting scheduler setup at " + datetime.datetime.now().isoformat())

    schedule.every(MINUTES_TO_REPEAT_LIVENESS_PROBE).minutes.do(liveness_probe)

    # send email
    schedule.every().day.at("01:00").do(send_recommendations_job)
    schedule.every().day.at("08:00").do(send_recommendations_job)
    schedule.every().day.at("18:45").do(send_recommendations_job)
    schedule.every().day.at("19:30").do(send_recommendations_job)
    schedule.every().day.at("20:30").do(send_recommendations_job)
    schedule.every().day.at("22:30").do(send_recommendations_job)
    schedule.every().day.at("23:30").do(send_recommendations_job)

    schedule.every().day.at("01:00").do(push_data_to_s3)
    schedule.every().day.at("04:00").do(push_data_to_s3)
    schedule.every().day.at("06:00").do(push_data_to_s3)
    schedule.every().day.at("08:00").do(push_data_to_s3)
    schedule.every().day.at("09:00").do(push_data_to_s3)
    schedule.every().day.at("10:00").do(push_data_to_s3)
    schedule.every().day.at("11:00").do(push_data_to_s3)
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

    print("Scheduler infinite loop started")
    while True:
        schedule.run_pending()
        time.sleep(1)
