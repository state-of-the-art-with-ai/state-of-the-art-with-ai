
import sentry_sdk
import os
from state_of_the_art.config import config

def setup_sentry():
    if not config.is_production():
        print("Skip sentry setup as not in production")

    sentry_sdk.init(
        dsn=os.environ.get("SOTA_SENTRY_DSN", ''),
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )
    print("Sentry setted up successfully")
