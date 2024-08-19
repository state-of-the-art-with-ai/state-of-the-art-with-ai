import time


def job():
    print("Running recommender")
    from state_of_the_art.recommender.generator import Recommender

    try:
        Recommender().generate(
            skip_register=False,
            disable_open_pdf=True,
            disable_pdf=True,
            number_lookback_days=2,
        )
    except Exception as e:
        print("Error in scheduler job", e)


def run_scheduler():
    import schedule

    schedule.every().day.at("09:00").do(job)
    print("Scheduler infinite loop started")
    while True:
        schedule.run_pending()
        time.sleep(1)
