import os


def no_internet() -> bool:
    if os.environ.get("NO_INTERNET"):
        return True
    return False
