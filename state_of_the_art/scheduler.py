import time
import datetime

from state_of_the_art.recommenders.interest_recommender.interest_recommender_generator import InterestsRecommender

def job():
    print("Running recommender")

    try:
        InterestsRecommender().generate(
            repeat_check_disable=True,
        )
    except Exception as e:
        print("Error in scheduler job", e)

def print_test():
    print("Run at " + datetime.datetime.now().isoformat())

def run_scheduler():
    import schedule

    schedule.every(5).minutes.do(print_test)
    schedule.every().day.at("09:00").do(job)
    print("Scheduler infinite loop started")
    while True:
        schedule.run_pending()
        time.sleep(1)
